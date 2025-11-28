# Manual Render Deployment Check

## ✅ Code Deployed Successfully

Both commits pushed to GitHub:
1. `6641d3d` - Fixed SalesIQ webhook with all tests passing
2. `e74447d` - Fixed render.yaml to use enhanced_api.py

## What You Need to Do Now

### Step 1: Check Render Dashboard (IMPORTANT!)

1. Go to: **https://dashboard.render.com**
2. Log in with your account
3. Find your service (should be named **acebuddy-api**)

### Step 2: Check Deployment Status

Look for the deployment status:

**If you see "Building" or "Deploying":**
- ⏳ Wait for it to complete (usually 5-10 minutes)
- Watch the logs for any errors

**If you see "Deploy live" with green checkmark:**
- ✅ Deployment successful!
- Proceed to Step 3

**If you see "Deploy failed" with red X:**
- ❌ Click on it to see error logs
- Common issues below

### Step 3: Get Your Service URL

At the top of your service page, you'll see your URL:
- It might be: `https://acebuddy-api.onrender.com`
- Or: `https://acebuddy-api-XXXX.onrender.com` (with random suffix)

**Copy this URL - you'll need it for SalesIQ!**

### Step 4: Test Your Deployed Webhook

Replace `YOUR-URL` with your actual Render URL:

```bash
# Test 1: Root endpoint
curl https://YOUR-URL/

# Expected: {"status":"healthy","service":"AceBuddy Hybrid RAG API",...}

# Test 2: Health check
curl https://YOUR-URL/health

# Expected: {"status":"healthy","rag_engine":{...},...}

# Test 3: Webhook test endpoint
curl https://YOUR-URL/webhook/salesiq/test

# Expected: {"status":"ok","message":"SalesIQ webhook endpoint is accessible",...}

# Test 4: Webhook with message
curl -X POST https://YOUR-URL/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"test","visitor_id":"v1","message":"Hello","visitor_name":"Test","visitor_email":"test@test.com"}'

# Expected: {"status":"success","message":"Hello! I'm AceBuddy...",...}
```

### Step 5: Configure SalesIQ

Once all tests pass:

1. Go to: **https://salesiq.zoho.com**
2. Navigate to: **Settings** → **Developers** → **Webhooks**
3. Click **Add Webhook** (or edit existing)
4. Fill in:
   - **Name:** AceBuddy Chatbot
   - **URL:** `https://YOUR-URL/webhook/salesiq` (use your actual Render URL)
   - **Method:** POST
   - **Content-Type:** application/json
   - **Events:** Select "Message Received" or "Chat Started"
5. Click **Test** button
   - Should show success message
   - If it fails, check Render logs
6. Click **Save**

### Step 6: Test in SalesIQ Chat Widget

1. Open your website with SalesIQ widget
2. Click to start a chat
3. Type: "Hello"
4. Bot should respond within 2-3 seconds
5. Try: "I need to reset my password"
6. Bot should ask for your username/email

## Common Issues & Solutions

### Issue 1: Render Shows "Deploy Failed"

**Check the logs for:**

**Error: "ModuleNotFoundError"**
- Solution: Missing dependency in requirements.txt
- Check if all packages are listed

**Error: "Port already in use"**
- Solution: Render handles ports automatically, ignore this

**Error: "OPENAI_API_KEY not found"**
- Solution: Add environment variable in Render
- Go to: Your Service → Environment → Add Variable
- Key: `OPENAI_API_KEY`
- Value: Your OpenAI API key (starts with sk-)

**Error: "Collection already exists"**
- Solution: Already fixed in code, should work now

### Issue 2: Service Returns 404

**Possible causes:**
1. Service still deploying (wait longer)
2. Wrong URL (check Render dashboard for correct URL)
3. Service crashed (check logs)

**Solution:**
- Check Render logs for errors
- Verify service is "Running"
- Try restarting the service manually

### Issue 3: Webhook Test in SalesIQ Fails

**Check:**
1. Is Render service running? (green "Running" status)
2. Does `/webhook/salesiq/test` work when you curl it?
3. Is the URL in SalesIQ exactly matching your Render URL?
4. Are you using HTTPS (not HTTP)?

**Solution:**
- Test webhook URL directly with curl first
- Check Render logs for incoming requests
- Verify no typos in SalesIQ webhook URL

### Issue 4: Bot Doesn't Respond in Chat

**Check:**
1. Is webhook configured correctly in SalesIQ?
2. Are you testing on the right website?
3. Check Render logs - do you see incoming requests?

**Solution:**
- Verify webhook is enabled in SalesIQ
- Check webhook events are set to "Message Received"
- Look for `[SalesIQ Webhook] Received payload:` in Render logs

## Environment Variables to Verify in Render

Go to: **Your Service → Environment**

Make sure these exist:
```
OPENAI_API_KEY=sk-...  (your actual key)
API_HOST=0.0.0.0
API_PORT=8000
PYTHON_VERSION=3.11.9
PYTHONUNBUFFERED=1
```

If `OPENAI_API_KEY` is missing:
1. Click **Add Environment Variable**
2. Key: `OPENAI_API_KEY`
3. Value: Your OpenAI API key
4. Click **Save**
5. Service will redeploy automatically

## What to Look For in Render Logs

**Successful startup looks like:**
```
Installing dependencies...
pip install -r requirements.txt
...
[OK] Loaded existing collection: acebuddy_kb
INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

**When webhook receives a message:**
```
[SalesIQ Webhook] Received payload: {'chat_id': '...', 'message': '...'}
[SalesIQ Webhook] Sending response: {'status': 'success', 'message': '...'}
INFO: POST /webhook/salesiq HTTP/1.1 200 OK
```

## Quick Checklist

- [ ] Render dashboard shows "Deploy live" (green)
- [ ] Service status shows "Running"
- [ ] Root endpoint (/) returns JSON with service info
- [ ] Health endpoint (/health) returns healthy status
- [ ] Webhook test endpoint returns "ok"
- [ ] OPENAI_API_KEY is set in environment variables
- [ ] Webhook URL configured in SalesIQ
- [ ] Webhook test in SalesIQ passes
- [ ] Bot responds in chat widget

## Need the Exact Service URL?

Your service URL should be one of these:
- `https://acebuddy-api.onrender.com`
- `https://acebuddy-api-XXXX.onrender.com` (with random suffix)

**To find it:**
1. Go to Render dashboard
2. Click on your service
3. Look at the top - you'll see the URL

## Final Test Command

Once you have your URL, run this complete test:

```bash
# Replace YOUR-URL with your actual Render URL
export URL="https://YOUR-URL"

echo "Testing root..."
curl $URL/

echo "\nTesting health..."
curl $URL/health

echo "\nTesting webhook endpoint..."
curl $URL/webhook/salesiq/test

echo "\nTesting webhook with message..."
curl -X POST $URL/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"test","visitor_id":"v1","message":"Hello","visitor_name":"Test","visitor_email":"test@test.com"}'
```

All four should return 200 OK with JSON responses.

## Summary

1. ✅ Code is deployed to GitHub
2. ⏳ Render should be deploying now
3. 👉 **YOU NEED TO:** Check Render dashboard for deployment status
4. 👉 **YOU NEED TO:** Get your service URL from Render
5. 👉 **YOU NEED TO:** Test the webhook endpoints
6. 👉 **YOU NEED TO:** Configure SalesIQ with your Render URL
7. 👉 **YOU NEED TO:** Test in chat widget

The code is tested and working - just need to verify Render deployment and configure SalesIQ!
