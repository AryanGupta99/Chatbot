"""
Smart API that auto-rebuilds ChromaDB on startup
Works on Render free tier by rebuilding from processed data
Version: 3.0.1 - Force redeploy
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
                chunks = json.load(f)
            
            # Handle both formats: list or dict with 'chunks' key
            if isinstance(chunks, dict):
                chunks = chunks.get('chunks', [])
            
            print(f"📚 Found {len(chunks)} chunks to process")
            
            # Add chunks in batches
            batch_size = 100
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                
                ids = []
                documents = []
                metadatas = []
                
                for j, chunk in enumerate(batch):
                    # Handle different chunk formats safely
                    if isinstance(chunk, dict):
                        chunk_id = chunk.get('id', f'chunk_{i+j}')
                        text = chunk.get('text', chunk.get('content', ''))
                        metadata = chunk.get('metadata', {})
                    else:
                        # If chunk is not a dict, convert to string
                        chunk_id = f'chunk_{i+j}'
                        text = str(chunk) if chunk else ''
                        metadata = {}
                    
                    ids.append(chunk_id)
                    documents.append(text)
                    metadatas.append(metadata)
                
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
                
                # LOG PROOF OF RAG USAGE
                print(f"\n{'='*60}")
                print(f"🔍 RAG QUERY: {request.message[:100]}")
                print(f"📂 Category: {result.get('category', 'N/A')}")
                print(f"📚 KB Sources Used: {len(result.get('sources', []))}")
                print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
                if result.get('sources'):
                    for i, src in enumerate(result['sources'][:3], 1):
                        print(f"   [{i}] Category: {src.get('category', 'N/A')}, Score: {src.get('relevance', 0):.3f}")
                        print(f"       ID: {src.get('id', 'N/A')[:50]}")
                print(f"✅ Response: {ai_response[:150]}...")
                print(f"{'='*60}\n")
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
        ai_response = None
        if USE_RAG and rag_engine:
            try:
                result = rag_engine.process_query_expert(
                    message,
                    conversation_history=conversation_history
                )
                ai_response = result.get("response", "").strip()
                
                # LOG PROOF OF RAG USAGE (SalesIQ)
                print(f"\n{'='*60}")
                print(f"🔍 SALESIQ RAG: {message[:100]}")
                print(f"📂 Category: {result.get('category', 'N/A')}")
                print(f"📚 KB Sources: {len(result.get('sources', []))}")
                print(f"✅ Response Length: {len(ai_response)} chars")
                print(f"{'='*60}\n")
                
                # Validate response
                if not ai_response or len(ai_response) < 10:
                    print("⚠️ RAG response too short, using fallback")
                    ai_response = None
                    
            except Exception as e:
                print(f"❌ RAG failed: {e}, using fallback")
                ai_response = None
        
        # Fallback if RAG failed or no response
        if not ai_response:
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
        
        # Clean for SalesIQ (preserve content, just format)
        ai_response = (ai_response
                      .replace("**", "")
                      .replace("*", "")
                      .replace("\n\n", " ")
                      .replace("\n", " ")
                      .strip())
        
        # Remove multiple spaces
        while "  " in ai_response:
            ai_response = ai_response.replace("  ", " ")
        
        # Final validation - ensure we have a response
        if not ai_response or len(ai_response) < 10:
            print(f"⚠️ Empty response detected! Original length: {len(ai_response)}")
            ai_response = "I'm here to help! Could you please provide more details about your question?"
        
        print(f"📤 Final response length: {len(ai_response)} chars")
        
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
        import traceback
        traceback.print_exc()
        
        # Always return valid SalesIQ format
        return {
            "action": "reply",
            "replies": ["I'm experiencing a technical issue. Please contact our support team at 1-888-415-5240 or support@acecloudhosting.com for immediate assistance."],
            "session_id": payload.get("session_id", "error") if 'payload' in locals() else "error"
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
