# SalesIQ Webhook Error - Troubleshooting Guide

## Error: "Error while contacting webhook server"

This error occurs when SalesIQ cannot successfully communicate with your webhook endpoint.

## Quick Fixes Applied

### 1. Enhanced Error Handling
- Added comprehensive try-catch blocks
- Webhook now always returns HTTP 200 (even on errors)
- Added detailed logging for debugging

### 2. Improved Response Format
- Standardized response structure
- Added proper error messages
- Included timestamps for tracking

### 3. Added Test Endpoint
- GET `/webhook/salesiq/test` - Test if webhook is accessible

## Common Causes & Solutions

### 1. **Webhook URL Not Accessible**

**Problem:** SalesIQ cannot reach your server

**Solutions:**
- Ensure your API is deployed and running
- Check if the URL is publicly accessible (not localhost)
- Verify firewall/security group settings allow incoming traffic on port 8000

**Test:**
```bash
curl https://your-domain.com/webhook/salesiq/test
```

Expected response:
```json
{
  "status": "ok",
  "message": "SalesIQ webhook endpoint is accessible",
  "timestamp": "2025-11-26T..."
}
```

### 2. **Wrong Webhook URL in SalesIQ**

**Problem:** URL configured in SalesIQ is incorrect

**Check:**
1. Go to SalesIQ Settings → Developers → Webhooks
2. Verify the URL is: `https://your-domain.com/webhook/salesiq`
3. Ensure it's HTTPS (not HTTP) if using Render/production

### 3. **SSL/HTTPS Issues**

**Problem:** Certificate errors or HTTP instead of HTTPS

**Solutions:**
- Use HTTPS in production (Render provides this automatically)
- Ensure SSL certificate is valid
- Don't use self-signed certificates with SalesIQ

### 4. **Server Not Running**

**Problem:** API server is down or crashed

**Check:**
```bash
# Check if server is running
curl https://your-domain.com/health

# Check Render logs
# Go to Render Dashboard → Your Service → Logs
```

### 5. **Payload Format Issues**

**Problem:** SalesIQ sends unexpected payload format

**Debug:**
- Check server logs for `[SalesIQ Webhook] Received payload:`
- Verify the payload structure matches expected format

## Testing the Webhook

### Test 1: Check Endpoint Accessibility
```bash
curl https://your-domain.com/webhook/salesiq/test
```

### Test 2: Send Test Payload
```bash
curl -X POST https://your-domain.com/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "test123",
    "visitor_id": "visitor123",
    "message": "Hello",
    "visitor_name": "Test User",
    "visitor_email": "test@example.com"
  }'
```

Expected response:
```json
{
  "status": "success",
  "message": "...",
  "data": {
    "ticket_created": false,
    "escalate": false
  },
  "timestamp": "..."
}
```

### Test 3: Check Health
```bash
curl https://your-domain.com/health
```

## SalesIQ Configuration Steps

### 1. Configure Webhook in SalesIQ

1. Log in to Zoho SalesIQ
2. Go to **Settings** → **Developers** → **Webhooks**
3. Click **Add Webhook**
4. Configure:
   - **Name:** AceBuddy Chatbot
   - **URL:** `https://your-domain.com/webhook/salesiq`
   - **Method:** POST
   - **Events:** Select "Message Received" or "Chat Started"
5. Save

### 2. Test from SalesIQ

1. Go to **Settings** → **Developers** → **Webhooks**
2. Find your webhook
3. Click **Test** button
4. Check if it returns success

### 3. Enable Bot in Chat Widget

1. Go to **Settings** → **Bots**
2. Create or edit your bot
3. In bot flow, add **Webhook Action**
4. Configure to call your webhook URL
5. Map response fields

## Debugging Checklist

- [ ] API server is running (`/health` returns 200)
- [ ] Webhook endpoint is accessible (`/webhook/salesiq/test` returns 200)
- [ ] URL in SalesIQ matches your deployed URL
- [ ] Using HTTPS (not HTTP) in production
- [ ] Firewall allows incoming traffic on port 8000
- [ ] Check server logs for errors
- [ ] Test with curl command works
- [ ] SalesIQ webhook test passes

## Server Logs to Check

Look for these log messages:

```
[SalesIQ Webhook] Received payload: {...}
[SalesIQ Webhook] Sending response: {...}
[SalesIQ Handler] Error processing message: ...
```

## If Still Not Working

### 1. Check Render Deployment

```bash
# View logs
# Go to Render Dashboard → Your Service → Logs

# Check environment variables
# Go to Render Dashboard → Your Service → Environment
```

### 2. Verify Environment Variables

Ensure these are set in `.env` or Render:
```
OPENAI_API_KEY=sk-...
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Restart the Service

On Render:
1. Go to your service
2. Click **Manual Deploy** → **Deploy latest commit**

Or locally:
```bash
python -m uvicorn src.enhanced_api:app --host 0.0.0.0 --port 8000
```

### 4. Check API Response Time

SalesIQ has a timeout (usually 10-30 seconds). If your API is slow:
- Optimize RAG queries
- Reduce `top_k_results` in config
- Add caching

### 5. Use Simple Response First

Test with a simple static response to isolate the issue:

```python
@app.post("/webhook/salesiq")
async def salesiq_webhook(request: Request):
    return {
        "status": "success",
        "message": "Hello from webhook!",
        "timestamp": datetime.now().isoformat()
    }
```

## Contact Support

If the issue persists:
1. Check Render logs for errors
2. Test webhook with curl
3. Verify SalesIQ webhook configuration
4. Check if OpenAI API key is valid

## Quick Command Reference

```bash
# Test webhook accessibility
curl https://your-domain.com/webhook/salesiq/test

# Test webhook with payload
curl -X POST https://your-domain.com/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"test","visitor_id":"v1","message":"hi"}'

# Check API health
curl https://your-domain.com/health

# Check API root
curl https://your-domain.com/
```

## Success Indicators

✅ `/webhook/salesiq/test` returns 200 OK
✅ `/health` returns healthy status
✅ Test curl with payload returns success
✅ SalesIQ webhook test passes
✅ Chat widget shows bot responses
✅ No errors in server logs
