from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime
import hashlib
import hmac

from config import settings
from src.rag_engine import RAGEngine

app = FastAPI(title="AceBuddy RAG API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG engine
rag_engine = RAGEngine()

# Session storage (in production, use Redis or database)
sessions: Dict[str, List[Dict[str, str]]] = {}

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    escalate: bool
    confidence: str
    sources: List[Dict[str, Any]]
    timestamp: str

class ZohoWebhookPayload(BaseModel):
    """Zoho SalesIQ webhook payload structure"""
    visitor_id: str
    chat_id: str
    message: str
    visitor_name: Optional[str] = None
    visitor_email: Optional[str] = None

def verify_zoho_signature(payload: str, signature: str) -> bool:
    """Verify Zoho webhook signature"""
    if not settings.zoho_webhook_secret:
        return True  # Skip verification if no secret configured
    
    expected_signature = hmac.new(
        settings.zoho_webhook_secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AceBuddy RAG API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        stats = rag_engine.vector_store.get_collection_stats()
        return {
            "status": "healthy",
            "vector_store": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Get or create session
        session_id = request.session_id or f"session_{datetime.now().timestamp()}"
        conversation_history = sessions.get(session_id, [])
        
        # Process query
        result = rag_engine.process_query(request.query, conversation_history)
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": request.query})
        conversation_history.append({"role": "assistant", "content": result["response"]})
        sessions[session_id] = conversation_history[-10:]  # Keep last 10 messages
        
        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            escalate=result["escalate"],
            confidence=result["confidence"],
            sources=result.get("sources", []),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/webhook/zoho")
async def zoho_webhook(
    request: Request,
    x_zoho_signature: Optional[str] = Header(None)
):
    """Webhook endpoint for Zoho SalesIQ"""
    try:
        # Get raw body for signature verification
        body = await request.body()
        payload_str = body.decode()
        
        # Verify signature
        if x_zoho_signature and not verify_zoho_signature(payload_str, x_zoho_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse payload
        payload = await request.json()
        
        # Extract message
        message = payload.get("message", "")
        chat_id = payload.get("chat_id", "")
        visitor_id = payload.get("visitor_id", "")
        
        if not message:
            return {"status": "ignored", "reason": "No message content"}
        
        # Process with RAG
        session_id = f"zoho_{chat_id}"
        conversation_history = sessions.get(session_id, [])
        
        result = rag_engine.process_query(message, conversation_history)
        
        # Update history
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": result["response"]})
        sessions[session_id] = conversation_history[-10:]
        
        # Return response in Zoho format
        return {
            "status": "success",
            "response": {
                "message": result["response"],
                "escalate": result["escalate"],
                "confidence": result["confidence"]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook error: {str(e)}")

@app.post("/session/clear")
async def clear_session(session_id: str):
    """Clear a conversation session"""
    if session_id in sessions:
        del sessions[session_id]
        return {"status": "success", "message": f"Session {session_id} cleared"}
    return {"status": "not_found", "message": f"Session {session_id} not found"}

@app.get("/stats")
async def get_stats():
    """Get API statistics"""
    return {
        "active_sessions": len(sessions),
        "vector_store": rag_engine.vector_store.get_collection_stats(),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
