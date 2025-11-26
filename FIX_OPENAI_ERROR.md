# Fix OpenAI Error - "I encountered an error"

## Problem

Bot is responding with: "I encountered an error. Please try again or contact support."

## Most Likely Cause

**OPENAI_API_KEY is not set in Render environment variables**

## Solution

### Step 1: Check if API Key is Set

Test the webhook:
```bash
curl https://acebuddy-api.onrender.com/webhook/salesiq/test
```

Look for `"openai_api_key"` in the response:
- ✅ `"openai_api_key": "configured"` - API key is set
- ❌ `"openai_api_key": "NOT SET"` - API key is missing!

### Step 2: Add OPENAI_API_KEY in Render

1. Go to: **https://dashboard.render.com**
2. Click on your service: **acebuddy-api**
3. Go to: **Environment** tab (left sidebar)
4. Look for `OPENAI_API_KEY`

**If it's missing or says "Add":**
1. Click **Add Environment Variable**
2. Key: `OPENAI_API_KEY`
3. Value: Your OpenAI API key (starts with `sk-`)
4. Click **Save Changes**
5. Service will automatically redeploy (2-3 minutes)

**If it's already there:**
1. Click the **Edit** button (pencil icon)
2. Verify the value is correct (starts with `sk-`)
3. If wrong, paste the correct key
4. Click **Save Changes**

### Step 3: Get Your OpenAI API Key

If you don't have the key:

1. Go to: **https://platform.openai.com/api-keys**
2. Log in to your OpenAI account
3. Click **Create new secret key**
4. Copy the key (starts with `sk-`)
5. Add it to Render (Step 2 above)

### Step 4: Wait for Redeploy

After adding/updating the key:
1. Render will automatically redeploy (2-3 minutes)
2. Watch the **Logs** tab for deployment progress
3. Look for: "Deploy live" message

### Step 5: Test Again

Once deployed:
```bash
# Test configuration
curl https://acebuddy-api.onrender.com/webhook/salesiq/test

# Should show: "openai_api_key": "configured"

# Test with message
curl -X POST https://acebuddy-api.onrender.com/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"Hello","visitor":{"name":"Test"}}'

# Should return proper response, not error
```

### Step 6: Test in SalesIQ Widget

1. Open your website with SalesIQ widget
2. Start a chat
3. Send: "Hello"
4. Bot should respond properly now

## Other Possible Issues

### Issue 1: Invalid API Key

**Symptoms:** Still getting errors after setting key

**Solution:**
1. Verify the key is correct (copy-paste from OpenAI dashboard)
2. Make sure there are no extra spaces
3. Key should start with `sk-`
4. Test the key at: https://platform.openai.com/playground

### Issue 2: API Key Quota Exceeded

**Symptoms:** Error mentions "rate_limit" or "quota"

**Solution:**
1. Check your OpenAI usage: https://platform.openai.com/usage
2. Add credits to your OpenAI account
3. Or upgrade your plan

### Issue 3: Wrong Model Name

**Symptoms:** Error mentions "model not found"

**Solution:**
- Current model: `gpt-4-turbo-preview`
- If you don't have GPT-4 access, change to: `gpt-3.5-turbo`
- Edit `src/simple_api.py` line with `model=`

## Check Render Logs

To see detailed error messages:

1. Go to Render dashboard
2. Click on your service
3. Click **Logs** tab
4. Look for lines starting with:
   - `[SalesIQ Webhook] ERROR:`
   - `[ERROR] OPENAI_API_KEY not set!`
   - `[ERROR] OpenAI API key issue detected!`

## Quick Checklist

- [ ] OPENAI_API_KEY is set in Render Environment
- [ ] API key starts with `sk-`
- [ ] API key is valid (test in OpenAI playground)
- [ ] Service has redeployed after adding key
- [ ] Test endpoint shows "configured"
- [ ] Webhook returns proper responses
- [ ] Bot responds in SalesIQ widget

## Summary

The error "I encountered an error" means the OpenAI API call is failing. 

**Most common fix:**
1. Add OPENAI_API_KEY to Render Environment variables
2. Wait for redeploy
3. Test again

**Check logs for specific error details!**
