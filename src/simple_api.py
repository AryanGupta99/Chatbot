"""
API for Zoho SalesIQ webhook with EXPERT RAG support
Uses advanced vector DB and multi-source knowledge base
"""
import os
import sys
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from pathlib import Path

# Add parent directory to path for imports (Render compatibility)
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import both RAG engines with fallback
EXPERT_MODE = False
rag_engine = None

try:
    from expert_rag_engine import ExpertRAGEngine
    EXPERT_MODE = True
except ImportError:
    try:
        from src.expert_rag_engine import ExpertRAGEngine
        EXPERT_MODE = True
    except ImportError:
        try:
            from rag_engine import RAGEngine
            EXPERT_MODE = False
        except ImportError:
            from src.rag_engine import RAGEngine
            EXPERT_MODE = False

app = FastAPI(
    title="AceBuddy Expert RAG API",
    version="3.0.0",
    description="SalesIQ webhook with Expert-Level RAG"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Expert RAG engine
if EXPERT_MODE:
    print("[INFO] Initializing EXPERT RAG Engine...")
    rag_engine = ExpertRAGEngine()
    print("[INFO] Expert RAG Engine ready!")
else:
    print("[INFO] Initializing Regular RAG Engine...")
    rag_engine = RAGEngine()
    print("[INFO] Regular RAG Engine ready!")

# Session storage for conversation history
sessions: Dict[str, list] = {}

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "AceBuddy Expert RAG API",
        "version": "3.0.0",
        "mode": "EXPERT" if EXPERT_MODE else "REGULAR",
        "features": [
            "SalesIQ Webhook",
            "Expert-Level RAG" if EXPERT_MODE else "Regular RAG",
            "Multi-Source KB",
            "Query Classification",
            "Advanced Retrieval",
            "Conversation History"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "active_sessions": len(sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint using Expert RAG"""
    try:
        # Get conversation history
        conversation_history = sessions.get(request.conversation_id, [])
        
        # Use Expert RAG engine
        if EXPERT_MODE:
            result = rag_engine.process_query_expert(
                query=request.message,
                conversation_history=conversation_history
            )
        else:
            result = rag_engine.process_query(
                query=request.message,
                conversation_history=conversation_history
            )
        
        # Update conversation history
        if request.conversation_id not in sessions:
            sessions[request.conversation_id] = []
        
        sessions[request.conversation_id].append({"role": "user", "content": request.message})
        sessions[request.conversation_id].append({"role": "assistant", "content": result["response"]})
        
        # Keep only last 10 messages
        sessions[request.conversation_id] = sessions[request.conversation_id][-10:]
        
        return ChatResponse(
            response=result.get("response", "I'm having trouble processing that. Please try again."),
            conversation_id=request.conversation_id
        )
    except Exception as e:
        print(f"[Chat Error] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook/salesiq/test")
async def test_salesiq_webhook():
    """Test endpoint to verify webhook is accessible"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    api_key_status = "configured" if api_key and len(api_key) > 10 else "NOT SET"
    
    return {
        "status": "ok",
        "message": "SalesIQ webhook endpoint is accessible",
        "openai_api_key": api_key_status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/webhook/salesiq")
async def salesiq_webhook(request: Request):
    """SalesIQ webhook - returns exact format required by SalesIQ widget"""
    try:
        # Parse payload
        payload = await request.json()
        
        # Log incoming request for debugging
        print(f"[SalesIQ Webhook] Received payload: {payload}")
        
        # Check if OpenAI API key is set and valid
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or len(api_key) < 20 or not api_key.startswith("sk-"):
            print(f"[ERROR] OPENAI_API_KEY not set or invalid! Length: {len(api_key)}, Starts with sk-: {api_key.startswith('sk-') if api_key else False}")
            return {
                "action": "reply",
                "replies": ["I'm having configuration issues. Please ask an administrator to set the OPENAI_API_KEY in Render."],
                "session_id": payload.get("session_id")
            }
        
        # Extract data from SalesIQ payload
        # SalesIQ sends message in different formats
        session_id = payload.get("session_id") or payload.get("chat_id") or payload.get("visitor_id")
        
        # Extract message - handle nested structure
        message_obj = payload.get("message", {})
        if isinstance(message_obj, dict):
            message = message_obj.get("text", "")
        else:
            message = str(message_obj) if message_obj else ""
        
        # Handle visitor object if present
        visitor = payload.get("visitor", {})
        visitor_name = visitor.get("name") or payload.get("visitor_name", "there")
        visitor_email = visitor.get("email") or payload.get("visitor_email", "")
        
        print(f"[SalesIQ Webhook] Session: {session_id}, Message: {message}")
        
        # If no message, return default greeting
        if not message:
            return {
                "action": "reply",
                "replies": ["Hello! I'm AceBuddy, your IT support assistant. How can I help you today?"],
                "session_id": session_id
            }
        
        # Get or create session for conversation history
        session_key = f"salesiq_{session_id}" if session_id else "default"
        if session_key not in sessions:
            sessions[session_key] = []
        
        # Keep only last 10 messages for conversation history
        conversation_history = sessions[session_key][-10:]
        
        print(f"[SalesIQ Webhook] Using {'EXPERT' if EXPERT_MODE else 'REGULAR'} RAG engine...")
        
        # Use RAG engine to get response
        if EXPERT_MODE:
            result = rag_engine.process_query_expert(
                query=message,
                conversation_history=conversation_history
            )
        else:
            result = rag_engine.process_query(
                query=message,
                conversation_history=conversation_history
            )
        
        print(f"[SalesIQ Webhook] RAG response received (confidence: {result.get('confidence', 'unknown')})")
        
        ai_response = result.get("response", "I'm having trouble processing that. Please try again.")
        
        # Remove markdown and newlines for SalesIQ widget
        ai_response = ai_response.replace("**", "").replace("*", "").replace("\n", " ").replace("  ", " ")
        
        # Update conversation history
        sessions[session_key].append({"role": "user", "content": message})
        sessions[session_key].append({"role": "assistant", "content": ai_response})
        
        # Return SalesIQ format
        response_data = {
            "action": "reply",
            "replies": [ai_response],
            "session_id": session_id
        }
        
        print(f"[SalesIQ Webhook] Sending response: {response_data}")
        return response_data
        
    except ValueError as e:
        # JSON parsing error
        print(f"[SalesIQ Webhook] JSON parse error: {str(e)}")
        return {
            "action": "reply",
            "replies": ["I didn't receive a valid message. Can you rephrase?"],
            "session_id": payload.get("session_id") if 'payload' in locals() else None
        }
    except Exception as e:
        # Catch all other errors
        error_msg = str(e)
        print(f"[SalesIQ Webhook] ERROR: {error_msg}")
        print(f"[SalesIQ Webhook] Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Check for specific OpenAI errors
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            print("[ERROR] OpenAI API key issue detected!")
            return {
                "action": "reply",
                "replies": ["I'm having authentication issues. Please contact support to check the API configuration."],
                "session_id": payload.get("session_id") if 'payload' in locals() else None
            }
        elif "rate_limit" in error_msg.lower():
            return {
                "action": "reply",
                "replies": ["I'm experiencing high traffic. Please try again in a moment."],
                "session_id": payload.get("session_id") if 'payload' in locals() else None
            }
        else:
            return {
                "action": "reply",
                "replies": ["I encountered an error processing your request. Please try again or contact support."],
                "session_id": payload.get("session_id") if 'payload' in locals() else None
            }

@app.get("/stats")
async def get_stats():
    """Get API statistics"""
    return {
        "active_sessions": len(sessions),
        "total_messages": sum(len(msgs) for msgs in sessions.values()),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
