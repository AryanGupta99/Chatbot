# ⚡ Quick Deploy - Get Webhook URL in 2 Minutes

## 🟢 **FASTEST WAY: Using Ngrok**

### Step 1: Download Ngrok (1 minute)

**Windows:**
```bash
# Option A: Download from https://ngrok.com/download
# Option B: Use chocolatey
choco install ngrok
```

**Mac:**
```bash
brew install ngrok
```

**Linux:**
```bash
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip
unzip ngrok-v3-stable-linux-amd64.zip
sudo mv ngrok /usr/local/bin
```

### Step 2: Sign Up & Get Token (1 minute)

1. Go to https://ngrok.com
2. Sign up (free)
3. Copy your auth token
4. Run: `ngrok config add-authtoken YOUR_TOKEN`

### Step 3: Start API (Already Running!)

The API is already running on `http://localhost:8000`

If not running, start it:
```bash
$env:OPENAI_API_KEY="your_api_key"
python src/enhanced_api.py
```

### Step 4: Create Tunnel

```bash
ngrok http 8000
```

### Step 5: Copy Your Webhook URL

You'll see output like:
```
Forwarding                     https://abc123def456.ngrok.io -> http://localhost:8000
```

**Your webhook URL is:**
```
https://abc123def456.ngrok.io/webhook/salesiq
```

---

## 🎯 **Configure SalesIQ Webhook**

1. Go to **Zoho SalesIQ** → **Settings** → **Webhooks**
2. Click **Add Webhook**
3. Paste URL: `https://abc123def456.ngrok.io/webhook/salesiq`
4. Select Event: **Message Received**
5. Click **Enable**
6. Click **Save**

---

## ✅ **Test It**

### Test 1: Health Check
```bash
curl https://abc123def456.ngrok.io/
```

### Test 2: SalesIQ Webhook
```bash
curl -X POST https://abc123def456.ngrok.io/webhook/salesiq \
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

## 🎉 **Done!**

Your API is now live and accessible from the internet!

**Webhook URL:** `https://abc123def456.ngrok.io/webhook/salesiq`

---

## 📝 **Important Notes**

### Ngrok URL Changes
- ⚠️ URL changes every time you restart ngrok
- ✅ Use ngrok pro for permanent URL
- ✅ Or use Heroku/AWS for permanent URL

### Keep Terminal Open
- ⚠️ Keep ngrok terminal open while testing
- ⚠️ Keep API terminal open while testing
- ✅ Both need to stay running

### For Production
- ❌ Don't use ngrok for production
- ✅ Use Heroku, AWS, or DigitalOcean
- ✅ See DEPLOYMENT_GUIDE.md for options

---

## 🚀 **Next: Test in SalesIQ Chat Widget**

1. Open your website with SalesIQ chat widget
2. Type: "I forgot my password"
3. AceBuddy should respond
4. Complete the workflow
5. Check if ticket would be created (once Zoho credentials added)

---

## 🆘 **Troubleshooting**

### Ngrok not working?
```bash
# Check if ngrok is installed
ngrok --version

# Check if auth token is set
ngrok config check

# Try again
ngrok http 8000
```

### API not responding?
```bash
# Check if API is running
curl http://localhost:8000

# If not, start it
python src/enhanced_api.py
```

### Webhook not receiving messages?
1. Check URL is correct in SalesIQ
2. Check webhook is enabled
3. Check ngrok terminal shows requests
4. Check API terminal shows logs

---

**Time to Deploy:** ⏱️ 2 minutes
**Status:** ✅ Ready to Test
