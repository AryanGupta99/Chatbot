# How to Use Your KB Docs for Accurate Answers

## 🎯 What You Want

**Current:** GPT's general knowledge + small prompt
**You Want:** Your actual KB docs (100+ PDFs) + accurate company-specific answers

**Good news: You already have all the code! Just need to switch it on!**

---

## 📋 Step-by-Step Guide

### Step 1: Check if ChromaDB Has Your Data (2 minutes)

```bash
python check_vector_store_content.py
```

This will show if your KB docs are already in the database.

**If it shows data:** Great! Skip to Step 3
**If empty:** Go to Step 2

---

### Step 2: Build the Knowledge Base (5-10 minutes, ONE TIME)

Run this to load all your KB docs into ChromaDB:

```bash
python build_expert_kb.py
```

This will:
- Read all 100+ PDFs from `data/SOP and KB Docs/`
- Convert them to embeddings
- Store in ChromaDB database
- Takes 5-10 minutes (one time only!)

**Cost:** ~$0.10 for embeddings (one time)

---

### Step 3: Create New API File (2 minutes)

Create `src/api_with_kb.py`:

```python
"""
API that uses your actual KB docs from data/ folder
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
    description="Uses actual KB docs"
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
rag_engine = ExpertRAGEngine()

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
        
        print(f"[SalesIQ] Response sent (using KB docs)")
        
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
        "using_kb_docs": True,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print("🚀 Starting AceBuddy API with KB docs...")
    print("📚 Using ChromaDB vector store")
    uvicorn.run(app, host="0.0.0.0", port=port)
```

---

### Step 4: Test Locally (5 minutes)

```bash
# Start the new API
python src/api_with_kb.py

# In another terminal, test it
python test_expert_rag.py
```

Compare responses - they should be MORE ACCURATE now!

---

### Step 5: Update render.yaml (1 minute)

Change this line:

```yaml
# OLD:
startCommand: python src/simple_api_working.py

# NEW:
startCommand: python src/api_with_kb.py
```

---

### Step 6: Deploy to Render (2 minutes)

```bash
git add src/api_with_kb.py render.yaml
git commit -m "Switch to KB docs for accurate answers"
git push origin main
```

Render will deploy in 2-3 minutes.

---

## 🎯 What Changes?

### Before (Current):
```
User: "QuickBooks error -6177"
↓
GPT's general knowledge
↓
Generic answer
```

### After (With KB Docs):
```
User: "QuickBooks error -6177"
↓
Search your PDF: "Fix QuickBooks Error codes.pdf"
↓
Get EXACT steps from YOUR document
↓
Accurate company-specific answer
```

---

## 💰 Cost Comparison

### Current (Without KB):
- Per chat: ~$0.0001
- 900 chats/month: ~$0.09/month

### With KB Docs:
- Per chat: ~$0.00015 (slightly more for embeddings)
- 900 chats/month: ~$0.14/month

**Extra cost: $0.05/month = 5 cents!**

**Worth it for accurate answers? YES!**

---

## ✅ Benefits of Using KB Docs

1. **More Accurate:** Uses YOUR exact procedures
2. **Company-Specific:** Your SOPs, not generic advice
3. **Up-to-Date:** Add new PDFs anytime
4. **Detailed:** Full information from docs
5. **Traceable:** Know which doc the answer came from

---

## 🧪 Quick Test

After deploying, test with:

```
User: "How to fix QuickBooks error -6177?"

Current system: Generic QuickBooks advice
With KB docs: Exact steps from your PDF
```

You'll see the difference immediately!

---

## 📊 Summary

| Step | Time | Cost |
|------|------|------|
| 1. Check ChromaDB | 2 min | Free |
| 2. Build KB (if needed) | 10 min | $0.10 (one time) |
| 3. Create new API | 2 min | Free |
| 4. Test locally | 5 min | Free |
| 5. Update render.yaml | 1 min | Free |
| 6. Deploy | 2 min | Free |
| **Total** | **22 min** | **$0.10** |

**Ongoing cost: +$0.05/month (5 cents more)**

---

## 🚀 Ready to Switch?

Just say "yes" and I'll help you do it step by step!

The code is already there, just need to:
1. Build the KB (if not done)
2. Create the new API file
3. Update render.yaml
4. Deploy

**Total time: 20 minutes**
**Result: Much more accurate answers from YOUR docs!**

Karna hai? 😊
