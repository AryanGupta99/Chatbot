# 🚀 Deployment Summary - Get Live in 5 Minutes

## 📋 What You Have

✅ **Complete AceBuddy System**
- Hybrid chatbot (Zobot + RAG)
- 13 automation workflows
- Zoho Desk integration
- SalesIQ webhook support
- Full API with 8+ endpoints

---

## 🎯 Your Goal

Get a **public webhook URL** to integrate with SalesIQ chat widget and test live.

---

## ⚡ **FASTEST PATH: Ngrok (2 Minutes)**

### 1. Install Ngrok
```bash
# Windows
choco install ngrok

# Mac
brew install ngrok

# Linux
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip
unzip ngrok-v3-stable-linux-amd64.zip
sudo mv ngrok /usr/local/bin
```

### 2. Sign Up & Get Token
- Go to https://ngrok.com
- Sign up (free)
- Copy auth token
- Run: `ngrok config add-authtoken YOUR_TOKEN`

### 3. Start API (Already Running!)
```bash
# Terminal 1: API is already running on localhost:8000
# If not, start it:
$env:OPENAI_API_KEY="your_api_key"
python src/enhanced_api.py
```

### 4. Create Tunnel
```bash
# Terminal 2: Create public URL
ngrok http 8000
```

### 5. Copy Webhook URL
```
https://abc123def456.ngrok.io/webhook/salesiq
```

### 6. Configure SalesIQ
1. Go to **Zoho SalesIQ** → **Settings** → **Webhooks**
2. Add webhook: `https://abc123def456.ngrok.io/webhook/salesiq`
3. Event: **Message Received**
4. Enable: **Yes**
5. Save

### 7. Test
```bash
curl https://abc123def456.ngrok.io/webhook/salesiq \
  -X POST \
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

## 🎉 **Done! You're Live!**

Your webhook URL is now live and accessible from the internet.

**Webhook URL:** `https://abc123def456.ngrok.io/webhook/salesiq`

---

## 🧪 Test in SalesIQ Chat Widget

1. Open your website with SalesIQ chat widget
2. Type: "I forgot my password"
3. AceBuddy responds: "What's your username or email?"
4. Type: "john.doe@company.com"
5. AceBuddy responds: "What's your phone? (last 4 digits)"
6. Type: "1234"
7. AceBuddy responds: "✅ Your request has been logged! Ticket ID: TKT-123456"

---

## 📊 What Happens

```
Customer in SalesIQ Chat
    ↓
Types: "I forgot my password"
    ↓
Webhook sends to: https://your-url/webhook/salesiq
    ↓
AceBuddy processes message
    ↓
Detects password_reset workflow
    ↓
Guides customer through steps
    ↓
Collects information
    ↓
(Once Zoho credentials added)
Creates ticket in Zoho Desk
    ↓
Customer notified with ticket ID
    ↓
Support team notified
```

---

## 🔄 Other Deployment Options

### Heroku (10 minutes)
```bash
heroku create acebuddy-app
git push heroku main
# URL: https://acebuddy-app.herokuapp.com/webhook/salesiq
```

### AWS EC2 (30 minutes)
- Launch instance
- Install dependencies
- Deploy code
- Configure Nginx
- Set up SSL

### DigitalOcean (15 minutes)
- Connect GitHub
- Configure app
- Deploy
- Get URL

See **DEPLOYMENT_GUIDE.md** for detailed instructions.

---

## 📝 Important Notes

### Ngrok URL Changes
- ⚠️ URL changes when you restart ngrok
- ✅ Use ngrok pro for permanent URL
- ✅ Or use Heroku/AWS for permanent URL

### Keep Terminals Open
- ⚠️ Keep ngrok terminal open
- ⚠️ Keep API terminal open
- ✅ Both must stay running

### For Production
- ❌ Don't use ngrok for production
- ✅ Use Heroku, AWS, or DigitalOcean
- ✅ See DEPLOYMENT_GUIDE.md

---

## 🧪 Test Scenarios

### Test 1: Greeting
```
You: "Hello"
Bot: "Hello! I'm AceBuddy..."
```

### Test 2: Password Reset
```
You: "I forgot my password"
Bot: "What's your username?"
You: "john.doe@company.com"
Bot: "What's your phone? (last 4 digits)"
You: "1234"
Bot: "✅ Your request has been logged!"
```

### Test 3: Disk Upgrade
```
You: "My disk is full"
Bot: "Upgrade options: 200GB, 100GB, 80GB, 60GB, 40GB"
You: "100GB"
Bot: "Request sent to POC for approval"
```

### Test 4: Server Slowness
```
You: "Server is slow"
Bot: "What's your CPU percentage?"
You: "85"
Bot: "High CPU. Close unused apps."
```

---

## ✅ Verification Checklist

- [ ] Ngrok installed
- [ ] Ngrok auth token set
- [ ] API running on localhost:8000
- [ ] Ngrok tunnel created
- [ ] Webhook URL copied
- [ ] SalesIQ webhook configured
- [ ] Webhook enabled in SalesIQ
- [ ] Test curl command works
- [ ] SalesIQ chat widget responds
- [ ] All workflows work

---

## 📞 Support

**Need Help?**

1. **Check Logs**
   - API terminal: Shows all requests
   - Ngrok terminal: Shows webhook calls

2. **Test Webhook**
   ```bash
   curl https://your-url/webhook/salesiq -X POST \
     -H "Content-Type: application/json" \
     -d '{"chat_id":"test","visitor_id":"test","visitor_email":"test@test.com","visitor_name":"Test","message":"Hello"}'
   ```

3. **Check Health**
   ```bash
   curl https://your-url/
   ```

4. **See Documentation**
   - DEPLOYMENT_GUIDE.md - Full deployment options
   - SALESIQ_TESTING_GUIDE.md - Testing guide
   - ZOHO_DESK_INTEGRATION_GUIDE.md - Zoho integration

---

## 🎯 Next Steps

1. ✅ Deploy with Ngrok (2 min)
2. ✅ Configure SalesIQ webhook (2 min)
3. ✅ Test in chat widget (1 min)
4. ✅ Add Zoho Desk credentials (later)
5. ✅ Test ticket creation (later)
6. ✅ Go live!

---

## 📊 Timeline

| Step | Time | Status |
|------|------|--------|
| Install Ngrok | 1 min | ⏳ |
| Sign up & get token | 1 min | ⏳ |
| Create tunnel | 1 min | ⏳ |
| Configure SalesIQ | 2 min | ⏳ |
| Test | 1 min | ⏳ |
| **Total** | **5 min** | ⏳ |

---

## 🚀 You're Ready!

Everything is set up and ready to deploy. Just follow the 5 steps above and you'll have a live webhook URL in 5 minutes.

**Let's go!** 🎉

---

**Status:** ✅ Ready to Deploy
**Version:** 1.0.0
**Last Updated:** 2025-11-26
