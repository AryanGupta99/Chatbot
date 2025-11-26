# ⚡ Render Quick Start - Deploy in 10 Minutes

## 🎯 Your Goal

Deploy AceBuddy to Render and get a public webhook URL for SalesIQ.

---

## ✅ Step 1: Prepare Your Code (2 minutes)

### 1.1 Update `requirements.txt`

```bash
pip freeze > requirements.txt
```

### 1.2 Create `Procfile`

Create file named `Procfile` (no extension):

```
web: python src/enhanced_api.py
```

### 1.3 Add to `.gitignore`

```bash
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

### 1.4 Push to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

---

## 🌐 Step 2: Create Render Account (2 minutes)

1. Go to https://render.com
2. Click **Sign up**
3. Choose **GitHub** as sign-up method
4. Authorize Render to access your GitHub

---

## 🚀 Step 3: Deploy on Render (3 minutes)

### 3.1 Create Web Service

1. Go to https://dashboard.render.com
2. Click **New +**
3. Select **Web Service**
4. Choose **GitHub** as repository source

### 3.2 Connect Repository

1. Search for **Chatbot** repository
2. Click **Connect**

### 3.3 Configure Service

**Name:** `acebuddy-api`

**Environment:** `Python 3`

**Region:** Choose closest to you

**Plan:** `Free`

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
python src/enhanced_api.py
```

### 3.4 Add Environment Variables

Click **Add Environment Variable** for each:

```
OPENAI_API_KEY = your_api_key_here
API_HOST = 0.0.0.0
API_PORT = 8000
```

### 3.5 Deploy

Click **Create Web Service**

Wait for deployment (2-3 minutes)

---

## ✅ Step 4: Get Your Webhook URL (1 minute)

Once deployment completes:

1. Go to your service in Render dashboard
2. Copy the **URL** (e.g., `https://acebuddy-api.onrender.com`)
3. Your webhook URL is:

```
https://acebuddy-api.onrender.com/webhook/salesiq
```

---

## 🧪 Step 5: Test Deployment (1 minute)

### Test Health Check

```bash
curl https://acebuddy-api.onrender.com/
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "AceBuddy Hybrid RAG API"
}
```

### Test Webhook

```bash
curl -X POST https://acebuddy-api.onrender.com/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "test_123",
    "visitor_id": "visitor_456",
    "visitor_email": "test@company.com",
    "visitor_name": "Test User",
    "message": "I forgot my password"
  }'
```

**Expected:**
```json
{
  "status": "success",
  "response": "What's your username or email?"
}
```

---

## 🔗 Step 6: Configure SalesIQ Webhook (1 minute)

1. Go to **Zoho SalesIQ** → **Settings** → **Webhooks**
2. Click **Add Webhook**
3. Paste URL: `https://acebuddy-api.onrender.com/webhook/salesiq`
4. Event: **Message Received**
5. Enable: **Yes**
6. Save

---

## 🎉 Done!

Your API is now live on Render!

**Webhook URL:** `https://acebuddy-api.onrender.com/webhook/salesiq`

---

## 📊 What Happens Now

```
Customer in SalesIQ Chat
    ↓
Types: "I forgot my password"
    ↓
Webhook sends to Render
    ↓
AceBuddy processes
    ↓
Bot responds: "What's your username?"
    ↓
Customer continues conversation
    ↓
Ticket created (once Zoho credentials added)
```

---

## 🧪 Test in SalesIQ Chat Widget

1. Open your website with SalesIQ chat
2. Type: "I forgot my password"
3. AceBuddy should respond
4. Complete the workflow
5. See ticket ID in response

---

## 📈 Monitor Your Deployment

### View Logs

1. Go to your service in Render dashboard
2. Click **Logs** tab
3. See real-time logs

### Check Status

1. Dashboard shows service status
2. Green = Running
3. Red = Error

---

## 🔄 Auto-Deployments

Every time you push to GitHub:

```bash
git add .
git commit -m "Your message"
git push origin main
```

Render automatically:
1. Detects the push
2. Builds your app
3. Deploys to production
4. Updates your live URL

---

## ⚠️ Important Notes

### Free Plan

- ✅ Always on (750 hours/month)
- ✅ Automatic HTTPS
- ✅ Auto-deployments
- ⚠️ Spins down after 15 min inactivity
- ⚠️ Limited to 512 MB RAM

### Upgrade to Starter

If you need always-on service:

1. Go to **Settings** → **Plan**
2. Click **Upgrade to Starter**
3. $7/month for always-on

---

## 🆘 Troubleshooting

### Deployment Failed

1. Check **Logs** tab
2. Look for error messages
3. Common: Missing dependencies

**Fix:**
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### API Not Responding

1. Check service status (green = running)
2. Check environment variables are set
3. Check logs for errors

### Webhook Not Working

1. Test with curl command
2. Check webhook URL is correct
3. Check webhook is enabled in SalesIQ

---

## 📝 Environment Variables

### Required

```
OPENAI_API_KEY = your_api_key
```

### Optional

```
API_HOST = 0.0.0.0
API_PORT = 8000
```

### For Zoho Desk (later)

```
ZOHO_DESK_API_KEY = your_key
ZOHO_DESK_ORG_ID = your_org_id
ZOHO_DESK_DEPARTMENT_ID = your_dept_id
```

---

## ✅ Deployment Checklist

- [ ] `requirements.txt` updated
- [ ] `Procfile` created
- [ ] `.env` in `.gitignore`
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] GitHub connected
- [ ] Environment variables set
- [ ] Deployment completed
- [ ] Health check passes
- [ ] Webhook URL obtained
- [ ] SalesIQ webhook configured
- [ ] Webhook test passes

---

## 🎯 Next Steps

1. ✅ Deploy to Render (10 min)
2. ✅ Get webhook URL
3. ✅ Configure SalesIQ
4. ✅ Test in chat widget
5. ✅ Add Zoho Desk credentials
6. ✅ Test ticket creation
7. ✅ Go live!

---

**Time to Deploy:** ⏱️ 10 minutes
**Cost:** 💰 Free
**Status:** ✅ Ready to Go Live
