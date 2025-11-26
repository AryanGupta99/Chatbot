# Deploy to Render - Quick Guide

## ✅ Local Testing Complete

All webhook tests passed successfully! Ready to deploy.

## Deployment Steps

### Step 1: Push to GitHub (2 minutes)

```bash
# Add all changes
git add .

# Commit with message
git commit -m "Fixed SalesIQ webhook - ready for deployment"

# Push to GitHub
git push origin main
```

### Step 2: Render Auto-Deploy (5-10 minutes)

Render will automatically detect the push and deploy:

1. Go to: https://dashboard.render.com
2. Find your service
3. Watch the deployment logs
4. Wait for "Deploy live" message

### Step 3: Verify Deployment (1 minute)

Test the deployed webhook:

```bash
# Replace YOUR-APP-NAME with your actual Render app name
curl https://YOUR-APP-NAME.onrender.com/webhook/salesiq/test
```

Expected response:
```json
{
  "status": "ok",
  "message": "SalesIQ webhook endpoint is accessible",
  "timestamp": "..."
}
```

### Step 4: Configure SalesIQ (3 minutes)

1. Log in to Zoho SalesIQ: https://salesiq.zoho.com
2. Go to **Settings** → **Developers** → **Webhooks**
3. Click **Add Webhook** or edit existing
4. Configure:
   - **Name:** AceBuddy Chatbot
   - **URL:** `https://YOUR-APP-NAME.onrender.com/webhook/salesiq`
   - **Method:** POST
   - **Events:** Select "Message Received"
5. Click **Test** button - should return success
6. **Save**

### Step 5: Test in Chat Widget (2 minutes)

1. Open your website with SalesIQ widget
2. Start a chat
3. Send a message like "Hello" or "I need help with password reset"
4. Bot should respond immediately
5. Check Render logs to see incoming requests

## Environment Variables on Render

Make sure these are set in Render Dashboard → Your Service → Environment:

```
OPENAI_API_KEY=sk-...
API_HOST=0.0.0.0
API_PORT=8000
```

## Troubleshooting

### If webhook test fails:

1. **Check Render logs:**
   - Go to Render Dashboard → Your Service → Logs
   - Look for errors or startup issues

2. **Verify URL:**
   - Make sure using HTTPS (not HTTP)
   - URL should be: `https://YOUR-APP-NAME.onrender.com/webhook/salesiq`

3. **Test health endpoint:**
   ```bash
   curl https://YOUR-APP-NAME.onrender.com/health
   ```

4. **Check environment variables:**
   - Ensure OPENAI_API_KEY is set
   - Verify it's a valid key

### If SalesIQ shows error:

1. **Check webhook URL in SalesIQ:**
   - Must match your Render URL exactly
   - Must use HTTPS
   - Must end with `/webhook/salesiq`

2. **Test webhook manually:**
   ```bash
   curl -X POST https://YOUR-APP-NAME.onrender.com/webhook/salesiq \
     -H "Content-Type: application/json" \
     -d '{"chat_id":"test","visitor_id":"v1","message":"hi","visitor_name":"Test","visitor_email":"test@test.com"}'
   ```

3. **Check Render logs:**
   - Should see incoming POST requests
   - Should see `[SalesIQ Webhook] Received payload:` messages

## Quick Reference

| What | URL |
|------|-----|
| Webhook Endpoint | `https://YOUR-APP-NAME.onrender.com/webhook/salesiq` |
| Test Endpoint | `https://YOUR-APP-NAME.onrender.com/webhook/salesiq/test` |
| Health Check | `https://YOUR-APP-NAME.onrender.com/health` |
| API Docs | `https://YOUR-APP-NAME.onrender.com/docs` |

## Success Indicators

✅ Render deployment shows "Deploy live"
✅ Test endpoint returns 200 OK
✅ Health check shows "healthy"
✅ SalesIQ webhook test passes
✅ Chat widget receives bot responses
✅ Render logs show incoming requests

## Files Changed

- `src/enhanced_api.py` - Enhanced webhook endpoint
- `src/salesiq_handler.py` - Improved error handling
- `src/vector_store.py` - Fixed unicode and collection errors

## What Was Fixed

1. ✅ Webhook always returns HTTP 200 (even on errors)
2. ✅ Better error handling and logging
3. ✅ Fixed unicode encoding issues
4. ✅ Fixed collection already exists error
5. ✅ Added test endpoint for quick verification

## Ready to Deploy!

Everything is tested and working locally. Just push to GitHub and Render will handle the rest!

```bash
git add .
git commit -m "Fixed SalesIQ webhook - all tests passing"
git push origin main
```

Then watch the magic happen in Render! 🚀
