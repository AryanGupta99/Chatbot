"""
Smart API that auto-rebuilds ChromaDB on startup
Works on Render free tier by rebuilding from processed data
"""
import os
import json
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from openai import OpenAI
import uvicorn
import sys
from pathlib import Path

app = FastAPI(
    title="AceBuddy API with Auto-Rebuild",
    version="3.0.0",
    description="Auto-rebuilds KB on startup"
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

# Try to load/rebuild RAG engine
USE_RAG = False
rag_engine = None

print("="*70)
print("🚀 Starting AceBuddy API with Auto-Rebuild")
print("="*70)

try:
    # Add parent directory to path
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    # Check if ChromaDB exists
    chroma_path = parent_dir / "data" / "chroma" / "chroma.sqlite3"
    processed_path = parent_dir / "data" / "processed" / "final_chunks.json"
    
    if not chroma_path.exists() and processed_path.exists():
        print("⚠️ ChromaDB not found, but processed data exists")
        print("🔨 Rebuilding ChromaDB from processed data...")
        
        # Quick rebuild from processed chunks
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Create ChromaDB client
            chroma_client = chromadb.PersistentClient(
                path=str(parent_dir / "data" / "chroma"),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create collection
            try:
                collection = chroma_client.get_collection("acebuddy_kb")
                print("✅ Collection already exists")
            except:
                collection = chroma_client.create_collection(
                    name="acebuddy_kb",
                    metadata={"hnsw:space": "cosine"}
                )
                print("✅ Created new collection")
            
            # Load processed chunks
            with open(processed_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                chunks = data.get('chunks', [])
            
            print(f"📚 Found {len(chunks)} chunks to process")
            
            # Add chunks in batches
            batch_size = 100
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                
                ids = [chunk.get('id', f'chunk_{i+j}') for j, chunk in enumerate(batch)]
                documents = [chunk.get('text', '') for chunk in batch]
                metadatas = [chunk.get('metadata', {}) for chunk in batch]
                
                # Generate embeddings using OpenAI
                texts_to_embed = [doc[:8000] for doc in documents]  # Limit length
                
                try:
                    response = client.embeddings.create(
                        model="text-embedding-3-small",
                        input=texts_to_embed
                    )
                    embeddings = [item.embedding for item in response.data]
                    
                    # Add to collection
                    collection.add(
                        ids=ids,
                        embeddings=embeddings,
                        documents=documents,
                        metadatas=metadatas
                    )
                    
                    print(f"✅ Processed batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
                except Exception as e:
                    print(f"⚠️ Error processing batch: {e}")
                    continue
            
            print("✅ ChromaDB rebuilt successfully!")
            
        except Exception as e:
            print(f"❌ Rebuild failed: {e}")
            print("⚠️ Falling back to simple prompt")
    
    # Now try to load RAG engine
    from src.expert_rag_engine import ExpertRAGEngine
    rag_engine = ExpertRAGEngine()
    USE_RAG = True
    print("✅ RAG engine loaded - using KB docs!")
    
except Exception as e:
    print(f"⚠️ RAG engine failed: {e}")
    print("✅ Using simple prompt instead")
    USE_RAG = False

print("="*70)

# Enhanced prompt (fallback)
ENHANCED_PROMPT = """You are AceBuddy, an expert IT support assistant for ACE Cloud Hosting.

CONVERSATIONAL APPROACH:
- FIRST RESPONSE: Ask 1-2 clarifying questions to understand the situation better
- FOLLOW-UP: Provide detailed solution only after understanding the context
- Be friendly and conversational, not robotic
- Keep initial responses short (2-3 sentences max)

CRITICAL KNOWLEDGE BASE:

**PASSWORD RESET:**
- SelfCare Portal: https://selfcare.acecloudhosting.com
- Steps: 1) Go to portal 2) Click "Forgot Password" 3) Enter email 4) Check email for reset link (2-3 min)
- If not enrolled: Contact support@acecloudhosting.com or call 1-888-415-5240

**DISK STORAGE:**
- Check space: Right-click C: drive → Properties
- Upgrade tiers: 40GB ($10/mo), 80GB ($20/mo), 120GB ($30/mo), 200GB ($50/mo)
- Contact: support@acecloudhosting.com or call 1-888-415-5240

**QUICKBOOKS ERRORS:**
- Error -6177, 0: Database Server Manager not running. Fix: Services → QuickBooksDBXX → Start
- Error -6189, -816: Company file corruption. Run QuickBooks File Doctor
- Error -6098, 5: Multi-user access issue. Check QB Database Server Manager

**SUPPORT CONTACTS:**
- Phone: 1-888-415-5240
- Email: support@acecloudhosting.com
- Chat: Available on website

GREETING: "Hello! I'm AceBuddy. How can I assist you today?"
"""

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
        "service": "AceBuddy API",
        "version": "3.0.0",
        "using_rag": USE_RAG,
        "auto_rebuild": True,
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
    """Chat endpoint with RAG or fallback"""
    try:
        if request.conversation_id not in sessions:
            sessions[request.conversation_id] = []
        
        conversation_history = sessions[request.conversation_id][-10:]
        
        # Try RAG first
        if USE_RAG and rag_engine:
            try:
                result = rag_engine.process_query_expert(
                    request.message,
                    conversation_history=conversation_history
                )
                ai_response = result["response"]
            except Exception as e:
                print(f"RAG failed: {e}, using fallback")
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
    """SalesIQ webhook"""
    try:
        payload = await request.json()
        
        session_id = payload.get("session_id") or payload.get("chat_id") or "default"
        message_obj = payload.get("message", {})
        message = message_obj.get("text", "") if isinstance(message_obj, dict) else str(message_obj)
        
        if not message:
            return {
                "action": "reply",
                "replies": ["Hello! I'm AceBuddy. How can I assist you today?"],
                "session_id": session_id
            }
        
        session_key = f"salesiq_{session_id}"
        if session_key not in sessions:
            sessions[session_key] = []
        
        conversation_history = sessions[session_key][-10:]
        
        # Try RAG first
        if USE_RAG and rag_engine:
            try:
                result = rag_engine.process_query_expert(
                    message,
                    conversation_history=conversation_history
                )
                ai_response = result["response"]
            except Exception as e:
                print(f"RAG failed: {e}")
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
        
        # Clean for SalesIQ
        ai_response = ai_response.replace("**", "").replace("*", "").replace("\n", " ").replace("  ", " ")
        
        # Update history
        sessions[session_key].append({"role": "user", "content": message})
        sessions[session_key].append({"role": "assistant", "content": ai_response})
        
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
    return {
        "active_sessions": len(sessions),
        "total_messages": sum(len(msgs) for msgs in sessions.values()),
        "using_rag": USE_RAG,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
