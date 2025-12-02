# Railway.app Deployment Guide - 5 Minutes

## Why Railway?
- ✅ $5/month (cheapest always-on option)
- ✅ No cold starts (perfect for webhooks)
- ✅ Free $5 credit to start
- ✅ Easy GitHub integration
- ✅ Fast deployment

---

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Sign Up (1 minute)
1. Go to https://railway.app
2. Click "Login" → "Login with GitHub"
3. Authorize Railway to access your GitHub
4. You get $5 free credit automatically!

### Step 2: Create Project (2 minutes)
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository: `AryanGupta99/Chatbot`
4. Railway will detect it's a Python project

### Step 3: Configure Environment Variables (1 minute)
Click on your service → "Variables" tab → Add:

```
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
TEMPERATURE=0.4
MAX_TOKENS=900
PYTHONUNBUFFERED=1
```

### Step 4: Configure Start Command (30 seconds)
1. Go to "Settings" tab
2. Find "Start Command"
3. Set to: `python src/simple_api_working.py`
4. Save

### Step 5: Deploy (30 seconds)
1. Railway automatically deploys
2. Wait for "Success" status (1-2 minutes)
3. Click "Generate Domain" to get your URL
4. Your webhook URL: `https://your-app.railway.app/webhook/salesiq`

### Step 6: Update SalesIQ (30 seconds)
1. Go to SalesIQ settings
2. Update webhook URL to Railway URL
3. Test with "Hello" message

**Done! Total time: ~5 minutes**

---

## 📋 Environment Variables Checklist

Copy these from your Render dashboard:

- [ ] `OPENAI_API_KEY` (required)
- [ ] `OPENAI_MODEL` (gpt-4o-mini)
- [ ] `OPENAI_EMBEDDING_MODEL` (text-embedding-3-small)
- [ ] `TEMPERATURE` (0.4)
- [ ] `MAX_TOKENS` (900)
- [ ] `PYTHONUNBUFFERED` (1)

Railway automatically sets `PORT`, no need to add it.

---

## 🔗 Getting Your Webhook URL

After deployment:
1. Click on your service
2. Click "Settings" tab
3. Scroll to "Domains"
4. Click "Generate Domain"
5. Your URL: `https://your-app-name.railway.app`

**Webhook endpoints:**
- Health: `https://your-app.railway.app/health`
- SalesIQ: `https://your-app.railway.app/webhook/salesiq`
- Chat: `https://your-app.railway.app/chat`

---

## 💰 Pricing

**Free Credit:** $5 (lasts ~1 month)
**After Credit:** $5/month for Hobby plan

**What You Get:**
- 512MB RAM
- 1GB storage
- Always-on (no cold starts)
- Unlimited deployments
- Custom domains
- SSL included

**Usage Estimate:**
- Your chatbot: ~$5/month
- No surprises, flat rate

---

## 🧪 Testing After Deployment

### Test 1: Health Check
```bash
curl https://your-app.railway.app/health
```

Expected:
```json
{
  "status": "healthy",
  "active_sessions": 0,
  "timestamp": "2024-12-01T..."
}
```

### Test 2: Chat Endpoint
```bash
curl -X POST https://your-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "conversation_id": "test"}'
```

Expected:
```json
{
  "response": "Hello! I'm AceBuddy. How can I assist you today?",
  "conversation_id": "test"
}
```

### Test 3: SalesIQ Webhook
Send "Hello" through SalesIQ widget

Expected: Quick response with simplified greeting

---

## 📊 Monitoring

### View Logs:
1. Click on your service
2. Go to "Deployments" tab
3. Click on latest deployment
4. View real-time logs

### Check Metrics:
1. Go to "Metrics" tab
2. See CPU, RAM, network usage
3. Monitor response times

### Set Up Alerts:
1. Go to "Settings"
2. Enable "Deploy Notifications"
3. Get notified of issues

---

## 🔄 Auto-Deploy from GitHub

Railway automatically deploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update chatbot"
git push origin main

# Railway deploys automatically in 1-2 minutes
```

---

## 🆚 Railway vs Render Comparison

| Feature | Railway | Render Free | Render Paid |
|---------|---------|-------------|-------------|
| **Cost** | $5/month | Free | $7/month |
| **Cold Starts** | None | Yes (15 min) | None |
| **RAM** | 512MB | 512MB | 512MB |
| **Webhook Ready** | ✅ Yes | ❌ No | ✅ Yes |
| **Deploy Speed** | Fast | Medium | Medium |
| **Setup** | Easy | Easy | Easy |
| **Free Credit** | $5 | N/A | N/A |

**Winner:** Railway (best value + performance)

---

## 🐛 Troubleshooting

### Deployment Failed?
1. Check logs in Railway dashboard
2. Verify `requirements.txt` is correct
3. Ensure start command is set
4. Check environment variables

### Can't Access URL?
1. Verify domain is generated
2. Check deployment status is "Success"
3. Wait 1-2 minutes after deployment
4. Try health endpoint first

### Webhook Not Working?
1. Verify URL in SalesIQ is correct
2. Check Railway logs for incoming requests
3. Test with curl first
4. Ensure OPENAI_API_KEY is set

### Out of Credit?
1. Add payment method in Railway
2. $5/month charged automatically
3. No interruption in service

---

## 🎯 Migration Checklist

Moving from Render to Railway:

- [ ] Sign up for Railway
- [ ] Create new project from GitHub
- [ ] Add environment variables
- [ ] Set start command
- [ ] Deploy and verify
- [ ] Generate domain
- [ ] Test health endpoint
- [ ] Test chat endpoint
- [ ] Update SalesIQ webhook URL
- [ ] Test SalesIQ integration
- [ ] Monitor for 24 hours
- [ ] Delete Render service (optional)

---

## 💡 Pro Tips

1. **Custom Domain:** Add your own domain in Settings → Domains
2. **Environment Groups:** Save env vars as templates for reuse
3. **Preview Deployments:** Test branches before merging
4. **Rollback:** Easy rollback to previous deployments
5. **Logs:** Download logs for debugging

---

## 📞 Support

**Railway:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

**Your Chatbot:**
- Test endpoint: `/health`
- View logs in Railway dashboard
- Check GitHub Actions for build status

---

## 🎉 Success Checklist

After deployment, verify:
- [ ] Health endpoint returns 200
- [ ] Chat endpoint works
- [ ] SalesIQ webhook responds quickly
- [ ] No cold starts
- [ ] Logs show no errors
- [ ] Greeting is simplified
- [ ] Conversational flow works

---

## 💰 Cost Breakdown

**Month 1:** FREE (using $5 credit)
**Month 2+:** $5/month

**Annual Cost:** $60/year

**Compare to:**
- Render Paid: $84/year
- Heroku: $84/year
- AWS: $84+/year

**Savings:** $24/year vs alternatives

---

## 🚀 Ready to Deploy?

1. Go to https://railway.app
2. Sign up with GitHub
3. Deploy from your repository
4. Add environment variables
5. Generate domain
6. Update SalesIQ webhook
7. Test and enjoy!

**Time:** 5 minutes
**Cost:** Free for first month, $5/month after
**Result:** Fast, reliable, always-on chatbot webhook

---

## Next Steps

1. **Deploy to Railway** (recommended)
2. **Test thoroughly** with SalesIQ
3. **Monitor for 24 hours**
4. **Keep Render as backup** (optional)
5. **Delete Render after confirming** Railway works

**Questions?** Check Railway docs or Discord community!
