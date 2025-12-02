"""
BULLETPROOF API - Works on Render with KB docs
Falls back to simple prompt if ChromaDB fails
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
    title="AceBuddy API",
    version="3.0.0",
    description="Bulletproof API with KB fallback"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Session storage
sessions: Dict[str, list] = {}

# Try to load RAG engine, fallback to simple prompt
USE_RAG = False
rag_engine = None

try:
    import sys
    from pathlib import Path
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    from src.expert_rag_engine import ExpertRAGEngine
    rag_engine = ExpertRAGEngine()
    USE_RAG = True
    print("✅ RAG engine loaded - using KB docs!")
except Exception as e:
    print(f"⚠️ RAG engine failed: {e}")
    print("✅ Falling back to simple prompt")
    USE_RAG = False

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

# Enhanced prompt with more KB knowledge
ENHANCED_PROMPT = """You are AceBuddy, an expert IT support assistant for ACE Cloud Hosting.

CONVERSATIONAL APPROACH:
- FIRST RESPONSE: Ask 1-2 clarifying questions to understand the situation better
- FOLLOW-UP: Provide detailed solution only after understanding the context
- Be friendly and conversational, not robotic
- Keep initial responses short (2-3 sentences max)

EXAMPLES:
User: "I need to reset my password"
You: "I can help with that! Are you currently registered on our SelfCare portal at https://selfcare.acecloudhosting.com?"

User: "My disk is full"
You: "Let me help you with that. First, can you check how much space you currently have? Right-click on your C: drive and select Properties to see the available space."

User: "QuickBooks error"
You: "I can assist with QuickBooks issues. What's the specific error code or message you're seeing?"

User: "Can't connect to RDP"
You: "I'll help you troubleshoot this. Are you connecting from Windows or Mac? And what error message are you seeing?"

User: "What's your phone number?" or "How do I contact support?"
You: "You can reach our support team at: Phone: 1-888-415-5240 | Email: support@acecloudhosting.com | Chat: Right here! How can I help you today?"

CRITICAL KNOWLEDGE BASE:

**PASSWORD RESET:**
- SelfCare Portal: https://selfcare.acecloudhosting.com
- Steps: 1) Go to portal 2) Click "Forgot Password" 3) Enter email 4) Check email for reset link (2-3 min)
- If not enrolled: Contact support@acecloudhosting.com or call 1-888-415-5240
- Requires Google Authenticator enrollment

**DISK STORAGE:**
- Check space: Right-click C: drive → Properties
- Quick cleanup: Delete temp files (%temp%), run Disk Cleanup utility
- Upgrade tiers: 40GB ($10/mo), 80GB ($20/mo), 120GB ($30/mo), 200GB ($50/mo)
- Contact: support@acecloudhosting.com or call 1-888-415-5240
- Ticket ETA: 2-4 hours for upgrade

**QUICKBOOKS ERRORS:**
- Error -6177, 0: Database Server Manager not running. Fix: Services → QuickBooksDBXX → Start
- Error -6189, -816: Company file corruption. Run QuickBooks File Doctor
- Error -6098, 5: Multi-user access issue. Check QB Database Server Manager
- Error -3371: Bank feeds import issue. Rebuild company file
- Always verify QB Database Server Manager is running

**RDP CONNECTION:**
- Server format: server.acecloudhosting.com
- Windows: Use Remote Desktop Connection (mstsc)
- Mac: Use Microsoft Remote Desktop (NOT built-in)
- Error 0x204: Network/firewall issue. Check internet connection
- Error "logon attempt failed": Verify credentials, check Caps Lock
- Disconnection: Check idle timeout policy (default: 2 hours)

**EMAIL (OUTLOOK):**
- SMTP: mail.acecloudhosting.com (Port 587 or 465)
- IMAP: mail.acecloudhosting.com (Port 993)
- POP3: mail.acecloudhosting.com (Port 995)
- Password prompts: Disable MFA or use app-specific password
- Can't send: Check SMTP settings, verify credentials

**SERVER PERFORMANCE:**
- Slow server: Check Task Manager for high CPU/RAM usage
- Close unused applications
- Check for Windows updates
- Restart server if needed
- Contact support if persistent: support@acecloudhosting.com or call 1-888-415-5240

**USER MANAGEMENT:**
- Add user: Contact support@acecloudhosting.com with user details
- Delete user: Contact support with username
- Permissions: Managed through QuickBooks or application settings
- ETA: 1-2 hours for user changes

**PRINTER ISSUES:**
- Local printer: Setup → Devices → Printers → Add printer
- UniPrint: For check printing alignment issues
- Redirect local printer: RDP settings → Local Resources → Printers
- Contact support for complex printer issues

**SUPPORT CONTACTS:**
- Phone: 1-888-415-5240 (IVR support line)
- Email: support@acecloudhosting.com
- Chat: Available on website
- SelfCare Portal: https://selfcare.acecloudhosting.com
- Ticket ETA: 2-4 hours for most issues

**Get In Touch:**
Chat | Phone: 1-888-415-5240 | Email: support@acecloudhosting.com

RESPONSE STYLE:
- INITIAL CONTACT: Ask clarifying questions (1-2 sentences)
- AFTER CLARIFICATION: Provide detailed steps (100-150 words max)
- Use numbered steps for solutions
- Include specific URLs and contact info
- Mention timeframes
- Be conversational and friendly

FORMATTING:
- Keep initial responses very short
- Use numbered lists for detailed solutions
- Include URLs when providing solutions
- Mention support contact for escalation

GREETING:
When user first says hello/hi or starts conversation, respond with:
"Hello! I'm AceBuddy. How can I assist you today?"
"""

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "AceBuddy API",
        "version": "3.0.0",
        "using_rag": USE_RAG,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "active_sessions": len(sessions),
        "using_rag": USE_RAG,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint with RAG fallback"""
    try:
        # Get conversation history
        if request.conversation_id not in sessions:
            sessions[request.conversation_id] = []
        
        conversation_history = sessions[request.conversation_id][-10:]
        
        # Try RAG first, fallback to simple
        if USE_RAG and rag_engine:
            try:
                result = rag_engine.process_query_expert(
                    request.message,
                    conversation_history=conversation_history
                )
                ai_response = result["response"]
            except Exception as e:
                print(f"RAG failed, using simple prompt: {e}")
                # Fallback to simple prompt
                messages = [{"role": "system", "content": ENHANCED_PROMPT}]
                messages.extend(conversation_history)
                messages.append({"role": "user", "content": request.message})
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=500
                )
                ai_response = response.choices[0].message.content.strip()
        else:
            # Use simple prompt
            messages = [{"role": "system", "content": ENHANCED_PROMPT}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": request.message})
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            ai_response = response.choices[0].message.content.strip()
        
        # Update history
        sessions[request.conversation_id].append({"role": "user", "content": request.message})
        sessions[request.conversation_id].append({"role": "assistant", "content": ai_response})
        
        return ChatResponse(
            response=ai_response,
            conversation_id=request.conversation_id
        )
    except Exception as e:
        print(f"[Chat Error] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/salesiq")
async def salesiq_webhook(request: Request):
    """SalesIQ webhook with RAG fallback"""
    try:
        payload = await request.json()
        print(f"[SalesIQ] Received: {payload}")
        
        # Check API key
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or len(api_key) < 20 or not api_key.startswith("sk-"):
            return {
                "action": "reply",
                "replies": ["I'm having configuration issues. Please contact support."],
                "session_id": payload.get("session_id")
            }
        
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
        
        # Try RAG first, fallback to simple
        if USE_RAG and rag_engine:
            try:
                result = rag_engine.process_query_expert(
                    message,
                    conversation_history=conversation_history
                )
                ai_response = result["response"]
                print(f"[SalesIQ] Using RAG engine")
            except Exception as e:
                print(f"[SalesIQ] RAG failed, using simple prompt: {e}")
                # Fallback to simple prompt
                messages = [{"role": "system", "content": ENHANCED_PROMPT}]
                messages.extend(conversation_history)
                messages.append({"role": "user", "content": message})
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=500
                )
                ai_response = response.choices[0].message.content.strip()
        else:
            # Use simple prompt
            messages = [{"role": "system", "content": ENHANCED_PROMPT}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})
            
            print(f"[SalesIQ] Using simple prompt")
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            ai_response = response.choices[0].message.content.strip()
        
        # Clean for SalesIQ
        ai_response = ai_response.replace("**", "").replace("*", "").replace("\n", " ").replace("  ", " ")
        
        # Update history
        sessions[session_key].append({"role": "user", "content": message})
        sessions[session_key].append({"role": "assistant", "content": ai_response})
        
        print(f"[SalesIQ] Response sent")
        
        return {
            "action": "reply",
            "replies": [ai_response],
            "session_id": session_id
        }
        
    except Exception as e:
        print(f"[SalesIQ] ERROR: {str(e)}")
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
        "using_rag": USE_RAG,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print("="*70)
    print("🚀 Starting AceBuddy API")
    if USE_RAG:
        print("✅ Using RAG engine with KB docs")
    else:
        print("✅ Using enhanced prompt (RAG unavailable)")
    print("="*70)
    uvicorn.run(app, host="0.0.0.0", port=port)
