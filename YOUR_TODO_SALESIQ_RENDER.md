# Your TODO - SalesIQ & Render Configuration

## ✅ What I've Done

1. Fixed all webhook code (tested locally - 100% success)
2. Pushed to GitHub (2 commits)
3. Fixed render.yaml to use enhanced_api.py

## 👉 What You Need to Do

### Step 1: Check Render Deployment (5 min)

1. Go to: **https://dashboard.render.com**
2. Find service: **acebuddy-api**
3. Wait for **"Deploy live"** status (green checkmark)
4. Copy your service URL (shown at top)
   - Example: `https://acebuddy-api.onrender.com`

### Step 2: Test Webhook (1 min)

Replace `YOUR-URL` with your actual Render URL:

```bash
curl https://YOUR-URL/webhook/salesiq/test
```

**Expected response:**
```json
{"status":"ok","message":"SalesIQ webhook endpoint is accessible",...}
```

If you get this, proceed to Step 3. If not, check Render logs.

### Step 3: Configure SalesIQ (3 min)

1. Go to: **https://salesiq.zoho.com**
2. Navigate: **Settings** → **Developers** → **Webhooks**
3. Click **Add Webhook** (or edit existing)
4. Fill in:
   - **Name:** AceBuddy Chatbot
   - **URL:** `https://YOUR-URL/webhook/salesiq` (your Render URL)
   - **Method:** POST
   - **Content-Type:** application/json
   - **Events:** Check "Message Received"
5. Click **Test** button (should show success)
6. Click **Save**

### Step 4: Test in Chat Widget (1 min)

1. Open your website with SalesIQ widget
2. Start a chat
3. Type: **"Hello"**
4. Bot should respond within 2-3 seconds
5. Try: **"I need to reset my password"**
6. Bot should ask for username/email

## Quick Troubleshooting

### If Render deployment fails:
- Check logs for errors
- Verify OPENAI_API_KEY is set in Environment variables
- Try manual redeploy

### If webhook test fails:
- Verify service is running (green status)
- Check URL is correct (no typos)
- Must use HTTPS (not HTTP)

### If SalesIQ test fails:
- Verify webhook URL matches Render URL exactly
- Check Render logs for incoming requests
- Ensure webhook is enabled

### If bot doesn't respond:
- Check webhook is saved and enabled in SalesIQ
- Verify events include "Message Received"
- Check Render logs for incoming POST requests

## Environment Variables in Render

Make sure these are set (Settings → Environment):
- `OPENAI_API_KEY` = your OpenAI key (sk-...)
- `API_HOST` = 0.0.0.0
- `API_PORT` = 8000

## Success Indicators

✅ Render shows "Deploy live" (green)
✅ `/webhook/salesiq/test` returns 200 OK
✅ SalesIQ webhook test passes
✅ Bot responds in chat widget

## That's It!

The code is ready. Just:
1. Wait for Render to deploy
2. Get your URL
3. Configure SalesIQ
4. Test

Total time: ~10 minutes
