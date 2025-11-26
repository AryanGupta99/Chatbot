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
        
        # Check if OpenAI API key is set
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key == "":
            print("[ERROR] OPENAI_API_KEY not set!")
            return {
                "action": "reply",
                "replies": ["I'm having configuration issues. Please contact support."],
                "session_id": payload.get("session_id")
            }
        
        # Extract data from SalesIQ payload
        session_id = payload.get("session_id") or payload.get("chat_id") or payload.get("visitor_id")
        message = payload.get("message", "")
        
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
        
        # Add user message to history
        sessions[session_key].append({"role": "user", "content": message})
        
        # Keep only last 10 messages
        conversation_history = sessions[session_key][-10:]
        
        # Build messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": """You are AceBuddy, a helpful IT support assistant for ACE Cloud Hosting.

Provide SHORT, CONCISE responses (1-2 sentences max). No markdown, no code blocks, no newlines.

Help with:
- QuickBooks Desktop and Enterprise issues
- Remote Desktop (RDP) connection problems  
- Email setup and configuration
- Server performance and slowness
- Password resets
- Printer issues
- Account access problems

Keep responses brief and actionable. Ask one question at a time if you need more info."""
            }
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        print(f"[SalesIQ Webhook] Calling OpenAI with {len(messages)} messages...")
        
        # Get AI response
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.3,
            max_tokens=150  # Shorter responses
        )
        
        print(f"[SalesIQ Webhook] OpenAI response received")
        
        ai_response = response.choices[0].message.content.strip()
        
        # Remove markdown and newlines for SalesIQ widget
        ai_response = ai_response.replace("**", "").replace("*", "").replace("\n", " ").replace("  ", " ")
        
        # Add assistant response to history
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
