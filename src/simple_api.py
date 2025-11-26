"""
Lightweight API for Zoho SalesIQ webhook - No vector DB required
Works on Render without chromadb dependencies
"""
import os
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from openai import OpenAI
import uvicorn

app = FastAPI(
    title="AceBuddy Hybrid RAG API",
    version="2.0.0",
    description="SalesIQ webhook integration with OpenAI"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

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
        "service": "AceBuddy Hybrid RAG API",
        "version": "2.0.0",
        "features": ["SalesIQ Webhook", "OpenAI GPT-4", "Conversation History"],
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
    """Simple chat endpoint"""
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are AceBuddy, a helpful IT support assistant for ACE Cloud Hosting. Help users with QuickBooks, RDP, email, and server issues."},
                {"role": "user", "content": request.message}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return ChatResponse(
            response=response.choices[0].message.content,
            conversation_id=request.conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook/salesiq/test")
async def test_salesiq_webhook():
    """Test endpoint to verify webhook is accessible"""
    return {
        "status": "ok",
        "message": "SalesIQ webhook endpoint is accessible",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/webhook/salesiq")
async def salesiq_webhook(request: Request):
    """SalesIQ webhook for incoming messages - matches our tested format"""
    try:
        # Parse payload
        payload = await request.json()
        
        # Log incoming request for debugging
        print(f"[SalesIQ Webhook] Received payload: {payload}")
        
        # Extract data from payload
        chat_id = payload.get("chat_id", "")
        visitor_id = payload.get("visitor_id", "")
        message = payload.get("message", "")
        visitor_name = payload.get("visitor_name", "Unknown")
        visitor_email = payload.get("visitor_email", "")
        
        if not message:
            return {
                "status": "success",
                "message": "Hello! How can I help you today?",
                "data": {
                    "ticket_created": False,
                    "ticket_id": None,
                    "ticket_number": None,
                    "escalate": False
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Get or create session for conversation history
        session_key = f"salesiq_{chat_id}"
        if session_key not in sessions:
            sessions[session_key] = []
        
        # Add user message to history
        sessions[session_key].append({"role": "user", "content": message})
        
        # Keep only last 10 messages
        conversation_history = sessions[session_key][-10:]
        
        # Build messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": """You are AceBuddy, a helpful IT support assistant for ACE Cloud Hosting.

Help users with:
- QuickBooks Desktop and Enterprise issues
- Remote Desktop (RDP) connection problems
- Email setup and configuration
- Server performance and slowness
- Password resets
- Printer issues
- Account access problems

Provide clear, concise, and helpful responses. If you detect urgent issues like server down, account locked, or critical errors, acknowledge the urgency.

For password resets, ask for their username or email.
For technical issues, ask relevant troubleshooting questions.
Be friendly and professional."""
            }
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Get AI response
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        
        # Add assistant response to history
        sessions[session_key].append({"role": "assistant", "content": ai_response})
        
        # Detect if escalation needed (simple keyword detection)
        escalate_keywords = ["can't help", "don't know", "contact support", "escalate", "urgent", "critical"]
        escalate = any(keyword in ai_response.lower() for keyword in escalate_keywords)
        
        # Prepare response
        response_data = {
            "status": "success",
            "message": ai_response,
            "data": {
                "ticket_created": False,
                "ticket_id": None,
                "ticket_number": None,
                "escalate": escalate
            },
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"[SalesIQ Webhook] Sending response: {response_data}")
        return response_data
        
    except ValueError as e:
        # JSON parsing error
        print(f"[SalesIQ Webhook] JSON parse error: {str(e)}")
        return {
            "status": "error",
            "message": "Invalid JSON payload",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # Catch all other errors and return 200 with error details
        print(f"[SalesIQ Webhook] Error: {str(e)}")
        return {
            "status": "error",
            "message": "I apologize, but I encountered an error processing your message. Please try again or contact support.",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
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
