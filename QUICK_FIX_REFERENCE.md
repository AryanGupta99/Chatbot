# Quick Fix Reference - SalesIQ Webhook Error

## 🚀 Immediate Actions

### 1. Test Your Webhook (30 seconds)
```bash
# If running locally
curl http://localhost:8000/webhook/salesiq/test

# If deployed on Render
curl https://your-app.onrender.com/webhook/salesiq/test
```

**Expected:** `{"status":"ok","message":"SalesIQ webhook endpoint is accessible",...}`

### 2. Run Full Test Suite (1 minute)
```bash
python test_salesiq_webhook.py
```

**Expected:** All 4 tests should pass ✅

### 3. Update SalesIQ Configuration (2 minutes)
1. Go to: SalesIQ → Settings → Developers → Webhooks
2. Set URL: `https://your-app.onrender.com/webhook/salesiq`
3. Method: POST
4. Click "Test" - should return success
5. Save

## 🔧 What Was Fixed

| Issue | Fix |
|-------|-----|
| Webhook returning errors | Now always returns HTTP 200 |
| No error handling | Added comprehensive try-catch blocks |
| Can't test webhook | Added `/webhook/salesiq/test` endpoint |
| No debugging info | Added detailed logging |
| Poor error messages | Improved user-facing error messages |

## 📋 Quick Checklist

- [ ] API server is running
- [ ] Test endpoint returns 200 OK
- [ ] Full test suite passes
- [ ] SalesIQ webhook URL is correct
- [ ] Using HTTPS in production
- [ ] SalesIQ webhook test passes

## 🆘 Still Not Working?

### Check 1: Is server running?
```bash
curl https://your-app.onrender.com/health
```

### Check 2: Are environment variables set?
- OPENAI_API_KEY must be set in .env or Render

### Check 3: Check Render logs
- Go to Render Dashboard → Your Service → Logs
- Look for errors or incoming webhook requests

### Check 4: Verify URL in SalesIQ
- Must be: `https://your-app.onrender.com/webhook/salesiq`
- Must use HTTPS (not HTTP)
- Must end with `/webhook/salesiq` (not `/webhook/zoho`)

## 📚 Full Documentation

- **Troubleshooting Guide:** `SALESIQ_WEBHOOK_TROUBLESHOOTING.md`
- **Fix Summary:** `WEBHOOK_FIX_SUMMARY.md`
- **Test Script:** `test_salesiq_webhook.py`

## 🎯 Success Indicators

✅ Test endpoint returns 200 OK
✅ Test script shows all tests passed
✅ SalesIQ webhook test succeeds
✅ Chat widget shows bot responses
✅ No errors in server logs

## 💡 Pro Tips

1. **Always test locally first** before deploying
2. **Check logs** when debugging webhook issues
3. **Use curl** to test endpoints directly
4. **Verify HTTPS** in production (Render provides this)
5. **Keep webhook URL simple** - no query parameters or fragments
