# 🚀 Render Deployment Guide - Complete Setup

## Overview

Render is a modern cloud platform perfect for deploying Python applications. It's free to start and automatically handles HTTPS, scaling, and deployments.

---

## 📋 Prerequisites

- ✅ GitHub repository created (you have this!)
- ✅ Render account (free at https://render.com)
- ✅ All code pushed to GitHub

---

## 🎯 Step 1: Push Code to GitHub

You've already created the repo. Now push all your code:

```bash
# In your project directory
git add .
git commit -m "Add AceBuddy chatbot with Zoho Desk integration"
git push -u origin main
```

**Verify on GitHub:**
- Go to https://github.com/AryanGupta99/Chatbot
- You should see all your files

---

## 🔧 Step 2: Create Render Configuration Files

### Create `Procfile`

Create a file named `Procfile` in your root directory:

```
web: python src/enhanced_api.py
```

### Create `render.yaml`

Create a file named `render.yaml` in your root directory:

```yaml
services:
  - type: web
    name: acebuddy-api
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python src/enhanced_api.py
    envVars:
      - key: OPENAI_API_KEY
        scope: build,runtime
      - key: API_HOST
        value: 0.0.0.0
      - key: API_PORT
        value: 8000
```

### Update `requirements.txt`

Make sure your `requirements.txt` has all dependencies:

```bash
pip freeze > requirements.txt
```

**Key packages needed:**
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
openai==1.3.0
chromadb==0.4.10
requests==2.31.0
python-dotenv==1.0.0
```

---

## 📝 Step 3: Create `.env.production`

Create a file named `.env.production` (don't commit this, just for reference):

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Zoho Desk (add later)
ZOHO_DESK_API_KEY=your_key_here
ZOHO_DESK_ORG_ID=your_org_id_here
ZOHO_DESK_DEPARTMENT_ID=your_dept_id_here
```

---

## 🌐 Step 4: Create Render Account & Connect GitHub

### 1. Sign Up for Render

1. Go to https://render.com
2. Click **Sign up**
3. Choose **GitHub** as sign-up method
4. Authorize Render to access your GitHub

### 2. Connect GitHub Repository

1. Go to https://dashboard.render.com
2. Click **New +**
3. Select **Web Service**
4. Choose **GitHub** as repository source
5. Search for **Chatbot** repository
6. Click **Connect**

---

## ⚙️ Step 5: Configure Render Service

### Basic Settings

1. **Name:** `acebuddy-api`
2. **Environment:** `Python 3`
3. **Region:** Choose closest to you (e.g., `us-east-1`)
4. **Plan:** `Free` (or Starter if you want more resources)

### Build & Deploy

1. **Build Command:**
   ```
   pip install -r requirements.txt
   ```

2. **Start Command:**
   ```
   python src/enhanced_api.py
   ```

### Environment Variables

Click **Add Environment Variable** and add:

```
OPENAI_API_KEY = your_api_key_here
API_HOST = 0.0.0.0
API_PORT = 8000
```

**Important:** Don't commit `.env` file to GitHub. Add to `.gitignore`:

```bash
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
git push
```

---

## 🚀 Step 6: Deploy

### Option A: Automatic Deployment (Recommended)

1. In Render dashboard, click **Create Web Service**
2. Render will automatically deploy when you push to GitHub
3. Wait for deployment to complete (2-3 minutes)

### Option B: Manual Deployment

1. In Render dashboard, click your service
2. Click **Manual Deploy**
3. Select **Deploy latest commit**
4. Wait for deployment

---

## ✅ Step 7: Get Your Webhook URL

Once deployment is complete:

1. Go to your service in Render dashboard
2. Copy the **URL** (e.g., `https://acebuddy-api.onrender.com`)
3. Your webhook URL is:
   ```
   https://acebuddy-api.onrender.com/webhook/salesiq
   ```

---

## 🧪 Step 8: Test Deployment

### Test 1: Health Check

```bash
curl https://acebuddy-api.onrender.com/
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "AceBuddy Hybrid RAG API",
  "version": "2.0.0"
}
```

### Test 2: Webhook

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

**Expected Response:**
```json
{
  "status": "success",
  "response": "What's your username or email?",
  "ticket_created": false
}
```

---

## 🔗 Step 9: Configure SalesIQ Webhook

1. Go to **Zoho SalesIQ** → **Settings** → **Webhooks**
2. Click **Add Webhook**
3. Paste URL: `https://acebuddy-api.onrender.com/webhook/salesiq`
4. Select Event: **Message Received**
5. Enable: **Yes**
6. Click **Save**

---

## 📊 Step 10: Monitor Deployment

### View Logs

1. Go to your service in Render dashboard
2. Click **Logs** tab
3. See real-time logs of your API

### Common Log Messages

```
# Deployment starting
Building Docker image...

# Dependencies installing
Installing collected packages...

# API starting
INFO:     Uvicorn running on http://0.0.0.0:8000

# Webhook received
INFO:     127.0.0.1:60390 - "POST /webhook/salesiq HTTP/1.1" 200 OK
```

---

## 🔐 Security Best Practices

### 1. Never Commit `.env`

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.production" >> .gitignore
```

### 2. Use Render Environment Variables

- Never put secrets in code
- Always use Render's environment variable system
- Rotate API keys regularly

### 3. Enable HTTPS

- Render automatically provides HTTPS
- All traffic is encrypted
- No additional configuration needed

---

## 📈 Scaling & Performance

### Free Plan Limits

- ✅ 750 hours/month (always on)
- ✅ Automatic HTTPS
- ✅ Automatic deployments
- ⚠️ Spins down after 15 min of inactivity
- ⚠️ Limited to 512 MB RAM

### Upgrade to Starter Plan

If you need:
- Always-on service (no spin-down)
- More RAM (1 GB)
- Better performance

Click **Settings** → **Plan** → **Upgrade to Starter**

---

## 🔄 Continuous Deployment

### Automatic Deployments

Every time you push to GitHub:

1. Render detects the push
2. Builds your application
3. Deploys automatically
4. Updates your live URL

### Manual Deployments

If you need to redeploy:

1. Go to your service
2. Click **Manual Deploy**
3. Select **Deploy latest commit**

---

## 🆘 Troubleshooting

### Deployment Failed

**Check:**
1. Go to **Logs** tab
2. Look for error messages
3. Common issues:
   - Missing dependencies in `requirements.txt`
   - Wrong start command
   - Missing environment variables

**Fix:**
```bash
# Update requirements.txt
pip freeze > requirements.txt

# Push to GitHub
git add requirements.txt
git commit -m "Update requirements"
git push

# Render will auto-redeploy
```

### API Not Responding

**Check:**
1. Is service running? (Check status in dashboard)
2. Are environment variables set?
3. Check logs for errors

**Fix:**
1. Click **Manual Deploy**
2. Check logs for errors
3. Update environment variables if needed

### Webhook Not Receiving Messages

**Check:**
1. Is webhook URL correct?
2. Is webhook enabled in SalesIQ?
3. Check Render logs for POST requests

**Test:**
```bash
curl -X POST https://your-render-url/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"test","visitor_id":"test","visitor_email":"test@test.com","visitor_name":"Test","message":"Hello"}'
```

---

## 📝 Environment Variables Reference

### Required

```
OPENAI_API_KEY = your_openai_api_key
```

### Optional (with defaults)

```
API_HOST = 0.0.0.0
API_PORT = 8000
OPENAI_MODEL = gpt-4-turbo-preview
CHROMA_PERSIST_DIRECTORY = ./data/chroma
```

### For Zoho Desk (add later)

```
ZOHO_DESK_API_KEY = your_zoho_key
ZOHO_DESK_ORG_ID = your_org_id
ZOHO_DESK_DEPARTMENT_ID = your_dept_id
```

---

## 🎯 Deployment Checklist

- [ ] GitHub repository created
- [ ] All code pushed to GitHub
- [ ] `Procfile` created
- [ ] `requirements.txt` updated
- [ ] `.env` added to `.gitignore`
- [ ] Render account created
- [ ] GitHub connected to Render
- [ ] Environment variables set in Render
- [ ] Deployment completed
- [ ] Health check passes
- [ ] Webhook URL obtained
- [ ] SalesIQ webhook configured
- [ ] Webhook test passes
- [ ] Chat widget responds

---

## 🚀 Your Webhook URL

Once deployed, your webhook URL will be:

```
https://acebuddy-api.onrender.com/webhook/salesiq
```

(Replace `acebuddy-api` with your actual service name)

---

## 📞 Support

**Render Documentation:**
- https://render.com/docs

**Common Issues:**
- Check **Logs** tab in Render dashboard
- Verify environment variables are set
- Ensure `requirements.txt` has all dependencies
- Check GitHub repository is connected

---

## 🎉 Next Steps

1. ✅ Push code to GitHub
2. ✅ Create Render account
3. ✅ Connect GitHub repository
4. ✅ Set environment variables
5. ✅ Deploy
6. ✅ Get webhook URL
7. ✅ Configure SalesIQ
8. ✅ Test in chat widget
9. ✅ Add Zoho Desk credentials
10. ✅ Go live!

---

**Status:** ✅ Ready to Deploy
**Platform:** Render
**Time to Deploy:** ⏱️ 10 minutes
**Cost:** 💰 Free (with option to upgrade)
