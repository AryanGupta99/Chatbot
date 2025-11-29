# Upgrade to Expert RAG - Action Checklist

## 🎯 Goal
Upgrade your chatbot from basic RAG to **Expert-Level RAG** with multi-source knowledge base.

---

## ✅ What I've Done For You

- [x] Created Expert RAG Engine (`src/expert_rag_engine.py`)
- [x] Created Multi-Source KB Builder (`build_expert_kb.py`)
- [x] Created Testing Tools (`test_expert_rag.py`)
- [x] Updated API to use Expert RAG (`src/simple_api.py`)
- [x] Created Documentation:
  - `EXPERT_RAG_GUIDE.md` (full guide)
  - `EXPERT_RAG_SUMMARY.md` (quick summary)
  - `RAG_EXPLAINED_SIMPLE.md` (simple explanation)

---

## 📋 What You Need to Do

### Step 1: Build Expert Knowledge Base

```bash
python build_expert_kb.py
```

**What this does:**
- Loads all 90+ PDF SOPs
- Loads manual KB articles
- Loads chat transcripts
- Loads Zobot Q&A data
- Combines and deduplicates everything
- Creates embeddings (costs ~$0.02)
- Builds vector store

**Time:** 5-10 minutes
**Cost:** ~$0.02 (2 cents)

**Output:**
- `data/expert_kb/expert_kb_chunks.json` (all chunks)
- `data/expert_kb/expert_kb_stats.json` (statistics)
- `data/chroma/` (vector database)

---

### Step 2: Test Expert RAG

```bash
# Compare regular vs expert
python test_expert_rag.py

# Test expert features only
python test_expert_rag.py features
```

**What this does:**
- Tests query classification
- Tests retrieval quality
- Compares regular vs expert responses
- Shows performance metrics

**Time:** 2-3 minutes

---

### Step 3: Review Results

Check the test output:
- Are responses better?
- Are they more specific?
- Do they include URLs and steps?
- Is confidence higher?

If yes, proceed to deployment!

---

### Step 4: Deploy to Render

```bash
# Add all new files
git add .

# Commit changes
git commit -m "Upgrade to Expert RAG system with multi-source KB"

# Push to GitHub
git push origin main
```

**What happens:**
- Render detects the push
- Auto-deploys your updated code
- Expert RAG goes live!

**Time:** 5-10 minutes (Render build time)

---

### Step 5: Verify Deployment

1. **Check Render Dashboard:**
   - Go to your Render service
   - Check "Events" tab for successful deploy
   - Check "Logs" for any errors

2. **Test the API:**
   ```bash
   curl https://your-app.onrender.com/
   ```
   
   Should return:
   ```json
   {
     "status": "healthy",
     "service": "AceBuddy Expert RAG API",
     "version": "3.0.0",
     "mode": "EXPERT"
   }
   ```

3. **Test a Query:**
   ```bash
   curl -X POST https://your-app.onrender.com/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "How do I reset my password?", "conversation_id": "test"}'
   ```

---

### Step 6: Monitor Performance

1. **OpenAI Dashboard:**
   - Check usage at https://platform.openai.com/usage
   - Monitor costs (should be ~0.01-0.03 cents per query)

2. **Render Logs:**
   - Watch for any errors
   - Check response times
   - Monitor memory usage

3. **User Feedback:**
   - Are responses better?
   - Are users satisfied?
   - Any issues reported?

---

## 🔧 Configuration (Optional)

If you want to tune the system, edit `config.py`:

```python
# For better accuracy (slower, more expensive)
top_k_results: int = 15
similarity_threshold: float = 0.2
max_context_length: int = 6000
max_tokens: int = 1200

# For faster responses (less accurate, cheaper)
top_k_results: int = 5
similarity_threshold: float = 0.5
max_context_length: int = 3000
max_tokens: int = 600

# Balanced (recommended)
top_k_results: int = 10
similarity_threshold: float = 0.3
max_context_length: int = 4000
max_tokens: int = 900
```

---

## 📊 Expected Results

### Before (Regular RAG):

```
User: "How do I reset my password?"
Bot: "You can reset your password through the SelfCare portal."
```

### After (Expert RAG):

```
User: "How do I reset my password?"
Bot: "To reset your password:

1. Go to https://selfcare.acecloudhosting.com
2. Click 'Forgot Password'
3. Enter your registered email
4. Check email for reset link (arrives in 2-3 minutes)

If you're not enrolled in SelfCare Portal:
- Contact support@acecloudhosting.com
- Or call our helpdesk for immediate assistance

Need help? I can create a support ticket for you."
```

**Improvements:**
- ✅ Specific URL included
- ✅ Step-by-step instructions
- ✅ Timeframe mentioned
- ✅ Alternative provided
- ✅ Escalation path offered

---

## 💰 Cost Comparison

### One-Time Setup:
```
Building Expert KB: ~$0.02 (2 cents)
```

### Per Query:
```
Regular RAG: ~$0.01 (1 cent)
Expert RAG:  ~$0.015 (1.5 cents)

Difference: +$0.005 (0.5 cents) per query
```

**Worth it?** YES! Better responses = happier users = fewer escalations

---

## 🚨 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src.expert_rag_engine'"

**Solution:**
```bash
# Make sure you're in the project root
cd /path/to/your/project

# Run the build script
python build_expert_kb.py
```

### Issue: "No such file or directory: 'data/SOP and KB Docs'"

**Solution:**
Make sure your PDF files are in the correct location:
```bash
ls "data/SOP and KB Docs/"
```

### Issue: "OpenAI API key not set"

**Solution:**
Check your `.env` file:
```bash
cat .env | grep OPENAI_API_KEY
```

Make sure it's set in Render environment variables too!

### Issue: "ChromaDB collection not found"

**Solution:**
Rebuild the vector store:
```bash
python build_expert_kb.py
```

---

## 📚 Documentation

- **Full Guide:** `EXPERT_RAG_GUIDE.md`
- **Quick Summary:** `EXPERT_RAG_SUMMARY.md`
- **Simple Explanation:** `RAG_EXPLAINED_SIMPLE.md`
- **This Checklist:** `UPGRADE_TO_EXPERT_RAG.md`

---

## ✨ Next Steps After Deployment

1. **Add More Data:**
   - Add new PDFs to `data/SOP and KB Docs/`
   - Add new KB articles to `data/kb/`
   - Run `python build_expert_kb.py` to update

2. **Fine-Tune:**
   - Adjust `config.py` settings
   - Test different configurations
   - Monitor performance

3. **Monitor:**
   - Check OpenAI usage
   - Review user feedback
   - Track response quality

4. **Iterate:**
   - Add more training data
   - Improve prompts
   - Optimize retrieval

---

## 🎉 Success Criteria

You'll know it's working when:

- ✅ Responses include specific URLs
- ✅ Step-by-step instructions are clear
- ✅ Company-specific information is accurate
- ✅ Timeframes and contact info are included
- ✅ Users are satisfied with answers
- ✅ Fewer escalations to human agents

---

## 🆘 Need Help?

1. Check the logs: `python test_expert_rag.py`
2. Review the docs: `EXPERT_RAG_GUIDE.md`
3. Check stats: `data/expert_kb/expert_kb_stats.json`
4. Test retrieval: See examples in `test_expert_rag.py`

---

## Quick Command Reference

```bash
# Build expert KB
python build_expert_kb.py

# Test expert RAG
python test_expert_rag.py

# Test expert features
python test_expert_rag.py features

# Deploy to Render
git add .
git commit -m "Upgrade to Expert RAG"
git push origin main

# Check API status
curl https://your-app.onrender.com/

# Test chat
curl -X POST https://your-app.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "conversation_id": "test"}'
```

---

**Ready to upgrade? Start with Step 1! 🚀**
