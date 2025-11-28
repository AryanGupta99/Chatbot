# Fix Generic Responses - Action Plan

## Problem Summary

Your chatbot gives **generic, static responses** instead of using the trained knowledge base and chat transcripts.

## Root Causes Identified

### 1. ✅ Incomplete Vector Store (CRITICAL)
- **Current**: Only 200/925 chunks loaded
- **Missing**: 725 chunks including ALL 64 training examples
- **Impact**: Bot can't access most of the knowledge base

### 2. ✅ Poor Chat Transcript Quality
- Training examples contain raw chat logs with metadata
- Not properly cleaned or formatted as Q&A pairs
- Low signal-to-noise ratio

### 3. ✅ Missing API Key
- .env file has placeholder: `your_openai_api_key_here`
- Bot can't generate embeddings or responses without valid key

## Quick Fix (30 minutes)

### Step 1: Fix API Key
```bash
# Edit .env file and add your real OpenAI API key
OPENAI_API_KEY=sk-proj-...your-real-key...
```

### Step 2: Rebuild Vector Store
```bash
# This will load all 925 chunks into the vector store
python rebuild_vector_store.py
```

**Expected output:**
- ✅ Loaded 925 chunks (861 docs + 64 training examples)
- ✅ Created new vector store
- ✅ All chunks embedded and indexed
- ✅ Verification shows 925 documents

### Step 3: Test
```bash
# Test if responses are now using knowledge base
python test_chatbot.py
```

**What to look for:**
- Responses should reference specific documents
- Should mention QuickBooks errors, RDP issues, etc.
- Should sound like your support team, not generic AI

## Better Fix (2-3 hours)

### Step 1: Improve Chat Transcript Processing
```bash
# Extract cleaner Q&A pairs from chat transcripts
python src/improved_chat_processor.py
```

This will:
- Remove timestamps, names, metadata
- Extract actual questions and answers
- Filter low-quality conversations
- Create `improved_training_examples.json`

### Step 2: Rebuild Chunks with Improved Data
```bash
# Rebuild chunks including improved training examples
python src/chunker.py
```

### Step 3: Rebuild Vector Store
```bash
python rebuild_vector_store.py
```

### Step 4: Test and Iterate
```bash
python test_chatbot.py
```

## Verification Checklist

After running the fix, verify:

- [ ] Vector store has 925+ documents (not just 200)
- [ ] Training examples are searchable
- [ ] Responses reference specific knowledge base articles
- [ ] Bot uses language patterns from chat transcripts
- [ ] Responses are specific to ACE Cloud Hosting context

## Testing Queries

Try these queries to verify the fix:

```python
from src.rag_engine import RAGEngine

rag = RAGEngine()

# Test 1: Should find QuickBooks error docs
result = rag.process_query("QuickBooks error -6177")
print(result['response'])
print(f"Sources: {result['sources']}")

# Test 2: Should find password reset info
result = rag.process_query("How do I reset my password?")
print(result['response'])

# Test 3: Should find RDP connection docs
result = rag.process_query("Can't connect to Remote Desktop")
print(result['response'])
```

**Expected behavior:**
- Each response should cite 3-5 sources
- Sources should include both documents and training examples
- Responses should be specific, not generic

## What Good Responses Look Like

### ❌ Bad (Generic):
> "To reset your password, you typically need to go to the login page and click 'Forgot Password'. Follow the instructions sent to your email."

### ✅ Good (Using Knowledge Base):
> "To reset your ACE Cloud Hosting password, please contact our support team at 1-855-223-4887. For security reasons, password resets require verification of your account details including your business name and registered email. Our team can assist you with this process in real-time."

## Monitoring After Fix

### Check Vector Store Stats
```python
from src.vector_store import VectorStore

vs = VectorStore()
vs.create_collection()
stats = vs.get_collection_stats()
print(f"Documents: {stats['total_documents']}")  # Should be 925+
```

### Check Retrieval Quality
```python
from src.rag_engine import RAGEngine

rag = RAGEngine()
results = rag.retrieve_context("password reset", top_k=5)

for r in results:
    print(f"Type: {r['metadata'].get('type')}")
    print(f"Category: {r['metadata'].get('category')}")
    print(f"Similarity: {1 - r['distance']:.3f}")
```

## Long-term Improvements

### 1. Manual Training Examples
Create high-quality Q&A pairs manually:

```json
[
  {
    "query": "I'm getting QuickBooks error -6177 when opening my company file",
    "response": "Error -6177 occurs when QuickBooks can't access the company file. To fix: 1) Close QuickBooks, 2) Navigate to your company file location, 3) Right-click the .QBW file and rename it, 4) Rename it back to original name, 5) Try opening again. If this doesn't work, contact support at 1-855-223-4887.",
    "category": "QuickBooks",
    "source": "manual_curation"
  }
]
```

### 2. Improve System Prompt
Update `src/rag_engine.py` to include:
- Specific examples of good responses
- Company-specific terminology
- Escalation guidelines
- Response templates

### 3. Add Feedback Loop
Track which responses users rate as helpful:
- Store successful Q&A pairs
- Retrain on high-rated responses
- Remove low-rated patterns

### 4. Hybrid Search
Combine semantic search with keyword matching:
- Better for specific error codes
- Catches exact matches
- Improves recall

## Troubleshooting

### Issue: Still getting generic responses after rebuild

**Check:**
1. Vector store actually has 925 documents
2. API key is valid and working
3. Retrieved documents are relevant (check similarity scores)
4. System prompt is being used

**Debug:**
```python
# Check what's being retrieved
from src.rag_engine import RAGEngine

rag = RAGEngine()
results = rag.retrieve_context("your test query", top_k=5)

for r in results:
    print(f"Similarity: {1 - r['distance']:.3f}")
    print(f"Content: {r['content'][:200]}")
    print("-" * 50)
```

### Issue: Training examples not being retrieved

**Possible causes:**
1. Training examples have low similarity to queries
2. Document chunks are more relevant
3. Embeddings not capturing semantic meaning

**Solutions:**
1. Improve training example quality
2. Add more training examples
3. Adjust similarity threshold in config.py

### Issue: Responses don't match retrieved context

**Check:**
1. System prompt emphasizes using retrieved context
2. Context is being passed to OpenAI correctly
3. Temperature setting (lower = more factual)

**Fix:**
Update system prompt in `src/rag_engine.py` to be more directive:
```python
self.system_prompt = """You are AceBuddy, an IT support assistant for ACE Cloud Hosting.

CRITICAL: You MUST base your responses on the provided knowledge base context.
DO NOT make up information. If the answer isn't in the context, say so.

Use the exact procedures, error codes, and solutions from the knowledge base.
Include specific phone numbers, steps, and details from the context.
"""
```

## Success Metrics

After the fix, you should see:

- **Automation Rate**: Increase from 11% baseline
- **Response Quality**: Specific, contextual answers
- **Source Attribution**: 3-5 sources cited per response
- **User Satisfaction**: Fewer escalations to human agents

## Need Help?

If responses are still generic after following this guide:

1. Run diagnostics:
   ```bash
   python check_vector_store_content.py
   python test_retrieval.py
   ```

2. Check the logs for:
   - Embedding errors
   - Low similarity scores
   - Missing context in prompts

3. Share the output for further debugging
