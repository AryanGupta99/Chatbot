"""
Lightweight API for Zoho SalesIQ webhook - Uses RAG engine with knowledge base
"""
import os
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from openai import OpenAI
import uvicorn
from src.hybrid_chatbot import HybridChatbot

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

# Initialize RAG chatbot
try:
    chatbot = HybridChatbot()
    print("[Startup] RAG chatbot initialized successfully")
except Exception as e:
    print(f"[Startup] Warning: Could not initialize RAG chatbot: {e}")
    chatbot = None

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

IMPORTANT - Password Reset Flow:
When user asks about password reset, follow this EXACT flow:
1. First ask: "Are you registered on our Self-Care Portal?"
2. If YES: "Great! You can reset your password directly at https://selfcare.acecloudhosting.com. Login with your email and click 'Forgot Password'."
3. If NO: "No problem! Please contact our IT support team at support@acecloudhosting.com or call the helpdesk to get registered and reset your password."

Other common issues:
- QuickBooks: Ask what specific error or issue they're experiencing
- RDP connection: Ask if they can ping the server or if it's a login issue
- Email: Ask which email client they're using
- Server slowness: Ask which application is slow
- Printer: Ask what error message they see

Keep responses brief and actionable. Ask one question at a time."""
            }
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        print(f"[SalesIQ Webhook] Processing with RAG engine...")
        
        # Use RAG chatbot if available, otherwise fall back to direct OpenAI
        if chatbot:
            try:
                result = chatbot.process_query(
                    message,
                    conversation_history=conversation_history,
                    session_id=session_key,
                    user_id=visitor_email
                )
                ai_response = result.get("response", "I'm having trouble processing that request.")
                print(f"[SalesIQ Webhook] RAG response received (source: {result.get('source')})")
            except Exception as e:
                print(f"[SalesIQ Webhook] RAG error: {e}, falling back to direct OpenAI")
                # Fallback to direct OpenAI
                response = client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=500
                )
                ai_response = response.choices[0].message.content.strip()
        else:
            # Fallback if RAG not initialized
            print(f"[SalesIQ Webhook] RAG not available, using direct OpenAI")
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
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
