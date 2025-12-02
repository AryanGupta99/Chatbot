# Quick Guide: Switch to Using Your KB Docs

## 🎯 Goal
Make your chatbot use your actual 100+ KB docs for MORE ACCURATE answers!

---

## ⚡ Super Quick Steps

### 1. Check if KB is Built (30 seconds)
```bash
python check_vector_store_content.py
```

**If it shows data:** Skip to step 3
**If empty or error:** Do step 2

---

### 2. Build KB from Your Docs (10 minutes, ONE TIME)
```bash
python build_expert_kb.py
```

This reads all your PDFs and creates the database.
**Cost: ~$0.10 (one time only)**

---

### 3. Test Locally (2 minutes)
```bash
# Start new API
python src/api_with_kb.py

# Test it (in another terminal)
curl http://localhost:8000/health
```

Should show: `"using_kb_docs": true`

---

### 4. Deploy to Render (5 minutes)

**Option A: Quick Test (Don't Change Render Yet)**
Just test locally first, see if you like it!

**Option B: Deploy to Render**
```bash
# Update render.yaml - change this line:
# FROM: startCommand: python src/simple_api_working.py
# TO:   startCommand: python src/api_with_kb.py

git add src/api_with_kb.py render.yaml
git commit -m "Use KB docs for accurate answers"
git push origin main
```

---

## 🎯 What You Get

### Before:
```
User: "QuickBooks error -6177"
Bot: [Generic answer from GPT's knowledge]
```

### After:
```
User: "QuickBooks error -6177"
Bot: [Exact answer from YOUR PDF: "Fix QuickBooks Error codes.pdf"]
```

**Much more accurate and company-specific!**

---

## 💰 Cost

**One-time:** $0.10 to build KB
**Monthly:** +$0.05/month (5 cents more per month)

**Total for 900 chats:**
- Before: $0.09/month
- After: $0.14/month
- **Extra: 5 cents/month for accurate answers!**

---

## ✅ Benefits

1. Uses YOUR exact SOPs and KB articles
2. More accurate company-specific answers
3. Can add new PDFs anytime
4. Answers are traceable to source docs
5. Better than generic GPT knowledge

---

## 🧪 Quick Test

After switching, ask:
- "How to fix QuickBooks error -6177?"
- "What's the disk upgrade process?"
- "How to reset password if not registered?"

Compare with current answers - you'll see the difference!

---

## 🚀 Ready?

**Step 1:** Test locally first
```bash
python src/api_with_kb.py
```

**Step 2:** If you like it, deploy to Render

**Step 3:** Enjoy accurate answers from YOUR docs!

Batao, karna hai? 😊
