# Visual Flow Diagrams

## 🎯 Current System (What You're Using)

```
┌─────────────┐
│   User      │
│  (SalesIQ)  │
└──────┬──────┘
       │ "How do I reset password?"
       ▼
┌─────────────────────────────────────┐
│  Your API (Render Server)           │
│  src/simple_api_working.py          │
│                                     │
│  EXPERT_PROMPT = """                │
│  Password Reset:                    │
│  - Go to SelfCare portal...         │
│  - Click Forgot Password...         │
│  Disk Storage:                      │
│  - 40GB = $10/mo...                 │
│  Support:                           │
│  - Phone: 1-888-415-5240...         │
│  """                                │
└──────┬──────────────────────────────┘
       │ Send full prompt + user message
       ▼
┌─────────────────────────────────────┐
│  OpenAI API                         │
│  GPT-4o-mini                        │
│                                     │
│  Reads prompt + question            │
│  Generates answer                   │
└──────┬──────────────────────────────┘
       │ Response
       ▼
┌─────────────────────────────────────┐
│  Your API                           │
│  Formats response                   │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────┐
│   User      │
│  Gets Answer│
└─────────────┘
```

**Storage:** None! Everything in the prompt.

---

## 🗄️ Vector Store System (You Have Code, Not Using)

```
PHASE 1: BUILD KNOWLEDGE BASE (One Time)
═══════════════════════════════════════

┌─────────────────────┐
│  Your Documents     │
│  - password.pdf     │
│  - disk_guide.txt   │
│  - quickbooks.pdf   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  build_expert_kb.py                 │
│  1. Read documents                  │
│  2. Split into chunks               │
│  3. Send to OpenAI for embeddings   │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  OpenAI Embeddings API              │
│  Converts text → numbers            │
│  "Password reset" → [0.23, -0.56...]│
└──────┬──────────────────────────────┘
       │ Embeddings
       ▼
┌─────────────────────────────────────┐
│  ChromaDB (Local Database)          │
│  chroma_db/                         │
│  Stores embeddings + text           │
└─────────────────────────────────────┘


PHASE 2: ANSWER QUESTIONS (Every Time)
═══════════════════════════════════════

┌─────────────┐
│   User      │
└──────┬──────┘
       │ "How do I reset password?"
       ▼
┌─────────────────────────────────────┐
│  Your API                           │
│  src/expert_rag_engine.py           │
└──────┬──────────────────────────────┘
       │ Convert question to embedding
       ▼
┌─────────────────────────────────────┐
│  OpenAI Embeddings API              │
│  "reset password" → [0.24, -0.55...]│
└──────┬──────────────────────────────┘
       │ Question embedding
       ▼
┌─────────────────────────────────────┐
│  ChromaDB (Local Search)            │
│  Find similar embeddings            │
│  Returns relevant chunks            │
└──────┬──────────────────────────────┘
       │ Top 3 relevant chunks
       ▼
┌─────────────────────────────────────┐
│  Your API                           │
│  Builds prompt with relevant chunks │
└──────┬──────────────────────────────┘
       │ Small prompt + chunks + question
       ▼
┌─────────────────────────────────────┐
│  OpenAI Chat API                    │
│  GPT-4o-mini                        │
│  Generates answer                   │
└──────┬──────────────────────────────┘
       │ Response
       ▼
┌─────────────┐
│   User      │
└─────────────┘
```

**Storage:** ChromaDB (local file on server)

---

## 💰 Token Usage Comparison

### Current System (Per Message):
```
┌────────────────────────────────┐
│ Full Prompt: 2000 tokens       │ ← ALL knowledge
│ User Message: 10 tokens        │
│ Conversation: 200 tokens       │
├────────────────────────────────┤
│ TOTAL INPUT: 2210 tokens       │
│ OUTPUT: 100 tokens             │
└────────────────────────────────┘
Cost: ~$0.00033 per message
```

### Vector Store System (Per Message):
```
┌────────────────────────────────┐
│ System Prompt: 500 tokens      │ ← Small prompt
│ Relevant Chunks: 500 tokens    │ ← Only relevant
│ User Message: 10 tokens        │
│ Conversation: 200 tokens       │
├────────────────────────────────┤
│ TOTAL INPUT: 1210 tokens       │
│ OUTPUT: 100 tokens             │
└────────────────────────────────┘
Cost: ~$0.00018 per message

SAVES: 45% on tokens!
```

---

## 🔢 What Are Embeddings?

### Text to Numbers:
```
"How do I reset my password?"
         ↓
OpenAI Embeddings API
         ↓
[0.234, -0.567, 0.891, 0.123, -0.456, ...]
         ↓
1536 numbers representing meaning
```

### Finding Similar Text:
```
Question: "reset password"
Embedding: [0.23, -0.56, 0.89, ...]

Chunk 1: "Password reset guide"
Embedding: [0.24, -0.55, 0.88, ...] ← VERY SIMILAR!
Distance: 0.05

Chunk 2: "Disk storage upgrade"
Embedding: [0.78, 0.12, -0.45, ...] ← DIFFERENT
Distance: 0.85

→ Return Chunk 1 (most relevant)
```

---

## 📊 Your 1.2M Tokens Explained

```
TOTAL: 1.2 Million Input Tokens
═══════════════════════════════

Building Knowledge Base (One Time):
┌────────────────────────────────┐
│ Documents → Embeddings         │
│ ~100,000 tokens                │
└────────────────────────────────┘

User Conversations:
┌────────────────────────────────┐
│ 500 conversations              │
│ × 2,200 tokens each            │
│ = 1,100,000 tokens             │
└────────────────────────────────┘

TOTAL: ~1,200,000 tokens ✓

COST: ~$0.18 (very cheap!)
```

---

## 🗂️ File Storage Locations

### Current System:
```
Render Server:
├── src/
│   └── simple_api_working.py ← ALL knowledge here
└── (no database files)

Memory (Temporary):
└── Conversation history
    (lost when server restarts)
```

### Vector Store System:
```
Render Server:
├── src/
│   ├── simple_api_working.py
│   ├── vector_store.py
│   └── expert_rag_engine.py
├── chroma_db/ ← LOCAL DATABASE
│   ├── embeddings.parquet
│   ├── metadata.db
│   └── index.bin
└── data/
    ├── password_reset.pdf
    └── disk_guide.txt

Memory (Temporary):
└── Conversation history
```

---

## 🎯 Quick Comparison

| Feature | Current | Vector Store |
|---------|---------|--------------|
| **Storage** | Prompt only | ChromaDB file |
| **Location** | In code | On server disk |
| **Size Limit** | ~8K tokens | Unlimited |
| **Token Cost** | Higher | Lower |
| **Complexity** | Simple | Medium |
| **Updates** | Edit code | Add documents |
| **Speed** | Fast | Fast |

---

## 💡 Key Takeaways

1. **You're using the SIMPLE system** (no database)
2. **All knowledge is in the prompt** (hardcoded)
3. **1.2M tokens = normal usage** (~$0.18 cost)
4. **Embeddings = numbers for meaning** (1536 dimensions)
5. **You HAVE vector store code** (just not using it)
6. **Current system works great** for your needs!
