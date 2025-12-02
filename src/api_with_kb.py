"""
API that uses your actual KB docs from data/ folder
Uses ChromaDB vector store for accurate, company-specific answers
"""
import os
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import sys
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import RAG engine
from src.expert_rag_engine import ExpertRAGEngine

app = FastAPI(
    title="AceBuddy API with KB",
    version="3.0.0",
    description="Uses actual KB docs for accurate answers"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG engine
print("🚀 Initializing RAG engine with KB docs...")
rag_engine = ExpertRAGEngine()
print("✅ RAG engine ready!")

# Session storage
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
        "service": "AceBuddy API with KB",
        "version": "3.0.0",
        "using_kb_docs": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "active_sessions": len(sessions),
        "using_kb_docs": True,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint using KB docs"""
    try:
        # Get conversation history
        if request.conversation_id not in sessions:
            sessions[request.conversation_id] = []
        
        conversation_history = sessions[request.conversation_id][-10:]
        
        # Process with RAG engine (uses your KB docs!)
        result = rag_engine.process_query_expert(
            request.message,
            conversation_history=conversation_history
        )
        
        # Update history
        sessions[request.conversation_id].append({
            "role": "user", 
            "content": request.message
        })
        sessions[request.conversation_id].append({
            "role": "assistant", 
            "content": result["response"]
        })
        
        return ChatResponse(
            response=result["response"],
            conversation_id=request.conversation_id
        )
    except Exception as e:
        print(f"[Chat Error] {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/salesiq")
async def salesiq_webhook(request: Request):
    """SalesIQ webhook using KB docs"""
    try:
        payload = await request.json()
        print(f"[SalesIQ] Received: {payload}")
        
        # Extract message
        session_id = payload.get("session_id") or payload.get("chat_id") or "default"
        message_obj = payload.get("message", {})
        message = message_obj.get("text", "") if isinstance(message_obj, dict) else str(message_obj)
        
        if not message:
            return {
                "action": "reply",
                "replies": ["Hello! I'm AceBuddy. How can I assist you today?"],
                "session_id": session_id
            }
        
        # Get/create session
        session_key = f"salesiq_{session_id}"
        if session_key not in sessions:
            sessions[session_key] = []
        
        conversation_history = sessions[session_key][-10:]
        
        print(f"[SalesIQ] Processing with KB docs...")
        
        # Process with RAG engine (uses your KB docs!)
        result = rag_engine.process_query_expert(
            message,
            conversation_history=conversation_history
        )
        
        ai_response = result["response"]
        
        # Clean for SalesIQ
        ai_response = ai_response.replace("**", "").replace("*", "")
        
        # Update history
        sessions[session_key].append({"role": "user", "content": message})
        sessions[session_key].append({"role": "assistant", "content": ai_response})
        
        print(f"[SalesIQ] Response sent (from KB docs)")
        
        return {
            "action": "reply",
            "replies": [ai_response],
            "session_id": session_id
        }
        
    except Exception as e:
        print(f"[SalesIQ] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "action": "reply",
            "replies": ["I encountered an error. Please try again or contact support."],
            "session_id": payload.get("session_id") if 'payload' in locals() else None
        }

@app.get("/stats")
async def get_stats():
    """Get stats"""
    return {
        "active_sessions": len(sessions),
        "total_messages": sum(len(msgs) for msgs in sessions.values()),
        "using_kb_docs": True,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print("="*70)
    print("🚀 Starting AceBuddy API with KB docs...")
    print("📚 Using ChromaDB vector store")
    print("📁 Reading from data/SOP and KB Docs/")
    print("="*70)
    uvicorn.run(app, host="0.0.0.0", port=port)
