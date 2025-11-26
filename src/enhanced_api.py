"""Enhanced API with Hybrid Chatbot
Combines Zobot flows with RAG responses
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from src.hybrid_chatbot import HybridChatbot
from src.zoho_desk_integration import ZohoDeskIntegration
from src.salesiq_handler import SalesIQHandler

app = FastAPI(title="AceBuddy Hybrid RAG API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize hybrid chatbot and integrations
hybrid_chatbot = HybridChatbot()
zoho_desk = ZohoDeskIntegration()
salesiq_handler = SalesIQHandler()

# Session storage
sessions: Dict[str, List[Dict[str, str]]] = {}

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class QuickAction(BaseModel):
    text: str
    action: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    escalate: bool
    confidence: str
    source: str
    sources: List[Dict[str, Any]] = []
    quick_actions: List[QuickAction] = []
    timestamp: str
    follow_up: Optional[str] = None

class ActionRequest(BaseModel):
    action: str
    session_id: Optional[str] = None

class WorkflowStepRequest(BaseModel):
    session_id: str
    step_id: str
    response: Any

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AceBuddy Hybrid RAG API",
        "version": "2.0.0",
        "features": ["RAG", "Zobot Flows", "Quick Actions", "Smart Escalation"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        stats = hybrid_chatbot.rag_engine.vector_store.get_collection_stats()
        zobot_qa_count = len(hybrid_chatbot.zobot_qa_pairs)
        
        return {
            "status": "healthy",
            "rag_engine": stats,
            "zobot_qa_pairs": zobot_qa_count,
            "conversation_flows": len(hybrid_chatbot.conversation_flows),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Enhanced chat endpoint with hybrid responses"""
    try:
        # Get or create session
        session_id = request.session_id or f"session_{datetime.now().timestamp()}"
        conversation_history = sessions.get(session_id, [])
        user_id = request.user_id or "anonymous"
        
        # Process query with hybrid chatbot (including workflow detection)
        result = hybrid_chatbot.process_query(request.query, conversation_history, session_id, user_id)
        
        # Get quick actions
        quick_actions = hybrid_chatbot.get_quick_actions(request.query)
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": request.query})
        conversation_history.append({"role": "assistant", "content": result["response"]})
        sessions[session_id] = conversation_history[-10:]  # Keep last 10 messages
        
        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            escalate=result["escalate"],
            confidence=result["confidence"],
            source=result.get("source", "unknown"),
            sources=result.get("sources", []),
            quick_actions=[QuickAction(**action) for action in quick_actions],
            follow_up=result.get("follow_up"),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/action")
async def handle_action(request: ActionRequest):
    """Handle quick action button clicks"""
    try:
        result = hybrid_chatbot.handle_quick_action(request.action)
        
        # Update session if provided
        if request.session_id:
            conversation_history = sessions.get(request.session_id, [])
            conversation_history.append({"role": "user", "content": f"[Action: {request.action}]"})
            conversation_history.append({"role": "assistant", "content": result["response"]})
            sessions[request.session_id] = conversation_history[-10:]
        
        return {
            "response": result["response"],
            "escalate": result["escalate"],
            "confidence": result["confidence"],
            "source": result["source"],
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error handling action: {str(e)}")

@app.get("/flows")
async def get_conversation_flows():
    """Get available conversation flows"""
    return {
        "flows": list(hybrid_chatbot.conversation_flows.keys()),
        "total_qa_pairs": len(hybrid_chatbot.zobot_qa_pairs),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/workflow/step")
async def process_workflow_step(request: WorkflowStepRequest):
    """Process workflow step response"""
    try:
        result = hybrid_chatbot.process_workflow_response(
            request.session_id,
            request.step_id,
            request.response
        )
        
        return {
            "response": result.get("response"),
            "escalate": result.get("escalate", False),
            "confidence": result.get("confidence", "high"),
            "source": result.get("source"),
            "ticket_id": result.get("ticket_id"),
            "eta": result.get("eta"),
            "workflow_data": result.get("workflow_data"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing workflow step: {str(e)}")

@app.get("/workflows")
async def get_workflows():
    """Get available automation workflows"""
    return {
        "workflows": hybrid_chatbot.workflow_executor.workflows.get_workflow_list(),
        "total": len(hybrid_chatbot.workflow_executor.workflows.workflows),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stats")
async def get_stats():
    """Enhanced statistics"""
    return {
        "active_sessions": len(sessions),
        "rag_engine": hybrid_chatbot.rag_engine.vector_store.get_collection_stats(),
        "zobot_integration": {
            "qa_pairs": len(hybrid_chatbot.zobot_qa_pairs),
            "conversation_flows": len(hybrid_chatbot.conversation_flows)
        },
        "automation_workflows": {
            "total": len(hybrid_chatbot.workflow_executor.workflows.workflows),
            "active_sessions": len(hybrid_chatbot.workflow_executor.active_sessions)
        },
        "workflow_stats": hybrid_chatbot.workflow_executor.get_workflow_stats(),
        "timestamp": datetime.now().isoformat()
    }

# ============ ZOHO DESK INTEGRATION ENDPOINTS ============

@app.post("/webhook/salesiq")
async def salesiq_webhook(request: Request):
    """SalesIQ webhook for incoming messages"""
    try:
        payload = await request.json()
        result = salesiq_handler.handle_incoming_message(payload)
        
        return {
            "status": result.get("status"),
            "response": result.get("response"),
            "ticket_created": result.get("ticket_created", False),
            "ticket_id": result.get("ticket_id"),
            "ticket_number": result.get("ticket_number"),
            "escalate": result.get("escalate", False),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook error: {str(e)}")

@app.post("/zoho/ticket/create")
async def create_zoho_ticket(request: ChatRequest):
    """Create ticket in Zoho Desk"""
    try:
        ticket_data = {
            "subject": request.metadata.get("subject", "Support Request") if request.metadata else "Support Request",
            "description": request.query,
            "email": request.user_id,
            "priority": request.metadata.get("priority", "Medium") if request.metadata else "Medium",
            "workflow_type": request.metadata.get("workflow_type") if request.metadata else "general"
        }
        
        result = zoho_desk.create_ticket(ticket_data)
        
        return {
            "success": result.get("success"),
            "ticket_id": result.get("ticket_id"),
            "ticket_number": result.get("ticket_number"),
            "error": result.get("error"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")

@app.get("/zoho/ticket/{ticket_id}")
async def get_zoho_ticket(ticket_id: str):
    """Get ticket details from Zoho Desk"""
    try:
        result = zoho_desk.get_ticket(ticket_id)
        
        return {
            "success": result.get("success"),
            "ticket": result.get("ticket"),
            "error": result.get("error"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ticket: {str(e)}")

@app.post("/zoho/ticket/{ticket_id}/comment")
async def add_ticket_comment(ticket_id: str, request: Request):
    """Add comment to Zoho Desk ticket"""
    try:
        payload = await request.json()
        comment = payload.get("comment", "")
        is_internal = payload.get("is_internal", False)
        
        result = zoho_desk.add_comment_to_ticket(ticket_id, comment, is_internal)
        
        return {
            "success": result.get("success"),
            "comment_id": result.get("comment_id"),
            "error": result.get("error"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding comment: {str(e)}")

@app.patch("/zoho/ticket/{ticket_id}/status")
async def update_ticket_status(ticket_id: str, request: Request):
    """Update ticket status in Zoho Desk"""
    try:
        payload = await request.json()
        status = payload.get("status", "Open")
        
        result = zoho_desk.update_ticket_status(ticket_id, status)
        
        return {
            "success": result.get("success"),
            "status": result.get("status"),
            "error": result.get("error"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")

@app.get("/zoho/test")
async def test_zoho_connection():
    """Test Zoho Desk API connection"""
    result = zoho_desk.test_connection()
    
    return {
        "success": result.get("success"),
        "message": result.get("message"),
        "error": result.get("error"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/salesiq/session/{chat_id}")
async def get_salesiq_session(chat_id: str):
    """Get SalesIQ session information"""
    result = salesiq_handler.get_session_info(chat_id)
    
    return {
        "success": result.get("success"),
        "session": result,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/salesiq/session/{chat_id}/close")
async def close_salesiq_session(chat_id: str):
    """Close SalesIQ session"""
    result = salesiq_handler.close_session(chat_id)
    
    return {
        "success": result.get("success"),
        "message": result.get("message"),
        "error": result.get("error"),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.enhanced_api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
