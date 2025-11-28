# Check Render Deployment Status

## Code Successfully Pushed ✅

Your code has been pushed to GitHub successfully!

Commit: `6641d3d - Fixed SalesIQ webhook - all tests passing, ready for production`

## Next Steps - Check Render Dashboard

### 1. Go to Render Dashboard
Visit: https://dashboard.render.com

### 2. Find Your Service
Look for your chatbot service (might be named something like):
- `chatbot-rag-api`
- `acebuddy-api`
- Or whatever name you gave it

### 3. Check Deployment Status

You should see one of these:
- **🟡 Building** - Wait for it to complete (5-10 minutes)
- **🟢 Deploy live** - Deployment successful!
- **🔴 Deploy failed** - Click to see error logs

### 4. Get Your Service URL

Once deployed, your service URL will be shown at the top, something like:
- `https://your-service-name.onrender.com`

### 5. Test Your Webhook

Replace `YOUR-SERVICE-NAME` with your actual service name:

```bash
# Test endpoint
curl https://YOUR-SERVICE-NAME.onrender.com/webhook/salesiq/test

# Should return:
# {"status":"ok","message":"SalesIQ webhook endpoint is accessible",...}
```

### 6. Configure SalesIQ

Once the webhook test works:

1. Go to: https://salesiq.zoho.com
2. Navigate to: **Settings** → **Developers** → **Webhooks**
3. Click **Add Webhook** or edit existing
4. Configure:
   - **Name:** AceBuddy Chatbot
   - **URL:** `https://YOUR-SERVICE-NAME.onrender.com/webhook/salesiq`
   - **Method:** POST
   - **Events:** Message Received
5. Click **Test** - should return success
6. **Save**

### 7. Test in Chat Widget

1. Open your website with SalesIQ widget
2. Start a chat
3. Send: "Hello"
4. Bot should respond immediately

## Troubleshooting

### If Render Shows "Deploy Failed"

1. Click on the failed deployment
2. Check the logs for errors
3. Common issues:
   - Missing environment variables (OPENAI_API_KEY)
   - Build errors
   - Port configuration

### If Service URL Returns 404

- Service might still be deploying (wait 5-10 minutes)
- Check if service is running in Render dashboard
- Verify the URL is correct

### If Webhook Test Fails

1. Make sure service is deployed and running
2. Test the health endpoint first: `/health`
3. Check Render logs for incoming requests
4. Verify OPENAI_API_KEY is set in Render environment variables

## Environment Variables to Check in Render

Go to: Your Service → Environment

Make sure these are set:
```
OPENAI_API_KEY=sk-...
API_HOST=0.0.0.0
API_PORT=8000
```

## Quick Test Commands

```bash
# Replace YOUR-SERVICE-NAME with your actual Render service name

# Test root
curl https://YOUR-SERVICE-NAME.onrender.com/

# Test health
curl https://YOUR-SERVICE-NAME.onrender.com/health

# Test webhook endpoint
curl https://YOUR-SERVICE-NAME.onrender.com/webhook/salesiq/test

# Test with message
curl -X POST https://YOUR-SERVICE-NAME.onrender.com/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"test","visitor_id":"v1","message":"Hello","visitor_name":"Test","visitor_email":"test@test.com"}'
```

## What to Look For in Render Logs

When deployment is successful, you should see:
```
[OK] Loaded existing collection: acebuddy_kb
INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

## SalesIQ Configuration Summary

Once your Render service is live:

**Webhook URL:** `https://YOUR-SERVICE-NAME.onrender.com/webhook/salesiq`
**Method:** POST
**Content-Type:** application/json

The webhook will:
- Receive messages from SalesIQ
- Process with RAG engine
- Detect intents (password reset, server issues, etc.)
- Return responses
- Create tickets when needed

## Need Help?

If you see errors in Render logs, check:
1. Environment variables are set correctly
2. OPENAI_API_KEY is valid
3. All dependencies in requirements.txt
4. Python version matches (3.12)

The code is tested and working locally - any issues are likely configuration-related on Render.
