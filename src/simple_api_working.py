"""
Simple Working API for Zoho SalesIQ webhook
Uses OpenAI directly with expert prompts (no vector store needed)
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
    version="2.0.0",
    description="SalesIQ webhook with OpenAI"
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

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

# Expert system prompt - SHORT & INTERACTIVE
EXPERT_PROMPT = """You are AceBuddy, a friendly IT support assistant for ACE Cloud Hosting.

RESPONSE STYLE - CRITICAL:
- Keep responses SHORT (2-4 sentences max)
- Guide users ONE STEP at a time
- Wait for confirmation before giving next step
- Be conversational and friendly
- Don't overwhelm with long lists

INTERACTIVE APPROACH:
User: "QuickBooks frozen"
You: "Let's fix that! First, press Ctrl+Shift+Esc to open Task Manager. Can you see QuickBooks in the list?"

User: "Need password reset"
You: "I can help! Are you registered on our SelfCare portal? (https://selfcare.acecloudhosting.com)"

User: "Disk full"
You: "Let's check your space. Right-click your C: drive and select Properties. How much space is left?"

User: "Account locked"
You: "I'll help unlock it. Call support at 1-888-415-5240 - they'll unlock it right away."

User: "Contact info" or "phone number"
You: "Support: 1-888-415-5240 | Email: support@acecloudhosting.com | How can I help?"

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
        "version": "2.0.0",
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
    """Chat endpoint"""
    try:
        # Get conversation history
        if request.conversation_id not in sessions:
            sessions[request.conversation_id] = []
        
        conversation_history = sessions[request.conversation_id][-10:]
        
        # Build messages
        messages = [{"role": "system", "content": EXPERT_PROMPT}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": request.message})
        
        # Get response (short and interactive)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=150  # Force short, interactive responses
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

@app.get("/webhook/salesiq/test")
async def test_salesiq_webhook():
    """Test endpoint"""
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
    """SalesIQ webhook"""
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
        
        # Build messages
        messages = [{"role": "system", "content": EXPERT_PROMPT}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        print(f"[SalesIQ] Calling OpenAI...")
        
        # Get response (short and interactive for SalesIQ)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=150  # Force short, interactive responses
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
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
