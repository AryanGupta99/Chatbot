# 🚀 Deployment Guide - AceBuddy with Zoho Desk Integration

## Overview

This guide covers deploying AceBuddy to get a public webhook URL for SalesIQ integration.

---

## 🎯 Deployment Options

### Option 1: **Ngrok** (Fastest - Local Testing)
- ✅ Instant public URL
- ✅ Perfect for testing
- ✅ No server needed
- ⏱️ Takes 2 minutes

### Option 2: **Heroku** (Easy - Cloud Hosting)
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Easy deployment
- ⏱️ Takes 10 minutes

### Option 3: **AWS/GCP/Azure** (Production)
- ✅ Scalable
- ✅ Professional
- ✅ Full control
- ⏱️ Takes 30 minutes

### Option 4: **Your Own Server** (VPS)
- ✅ Full control
- ✅ Cost-effective
- ✅ Custom domain
- ⏱️ Takes 20 minutes

---

## 🟢 **OPTION 1: NGROK (Recommended for Testing)**

### Step 1: Install Ngrok

**Windows:**
```bash
# Download from https://ngrok.com/download
# Or use chocolatey
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

### Step 2: Sign Up for Ngrok

1. Go to https://ngrok.com
2. Sign up (free account)
3. Get your auth token
4. Run: `ngrok config add-authtoken YOUR_TOKEN`

### Step 3: Start API Server

```bash
# Terminal 1: Start the API
$env:OPENAI_API_KEY="your_api_key"
python src/enhanced_api.py
```

API will run on: `http://localhost:8000`

### Step 4: Create Ngrok Tunnel

```bash
# Terminal 2: Create tunnel
ngrok http 8000
```

**Output:**
```
ngrok                                       (Ctrl+C to quit)

Session Status                online
Account                       your_email@example.com
Version                        3.0.0
Region                         us (United States)
Latency                        45ms
Web Interface                  http://127.0.0.1:4040

Forwarding                     https://abc123def456.ngrok.io -> http://localhost:8000
```

### Step 5: Get Your Webhook URL

```
https://abc123def456.ngrok.io/webhook/salesiq
```

### Step 6: Configure SalesIQ Webhook

1. Go to **Zoho SalesIQ** → **Settings** → **Webhooks**
2. Add webhook: `https://abc123def456.ngrok.io/webhook/salesiq`
3. Select: **Message Received** event
4. Enable webhook

### Step 7: Test

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

**✅ Done! Your API is now accessible from the internet.**

---

## 🟡 **OPTION 2: HEROKU (Easy Cloud Deployment)**

### Step 1: Install Heroku CLI

**Windows:**
```bash
choco install heroku-cli
```

**Mac:**
```bash
brew tap heroku/brew && brew install heroku
```

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

### Step 2: Login to Heroku

```bash
heroku login
```

### Step 3: Create Heroku App

```bash
# Create app
heroku create acebuddy-app

# Or use existing app
heroku apps:create acebuddy-app --region us
```

### Step 4: Create Procfile

Create `Procfile` in root directory:

```
web: python src/enhanced_api.py
```

### Step 5: Create requirements.txt

```bash
pip freeze > requirements.txt
```

### Step 6: Set Environment Variables

```bash
heroku config:set OPENAI_API_KEY=your_api_key
heroku config:set API_HOST=0.0.0.0
heroku config:set API_PORT=5000
```

### Step 7: Deploy

```bash
git init
git add .
git commit -m "Initial deployment"
git push heroku main
```

### Step 8: Get Your URL

```bash
heroku open
```

**Your webhook URL:**
```
https://acebuddy-app.herokuapp.com/webhook/salesiq
```

### Step 9: Configure SalesIQ Webhook

1. Go to **Zoho SalesIQ** → **Settings** → **Webhooks**
2. Add webhook: `https://acebuddy-app.herokuapp.com/webhook/salesiq`
3. Select: **Message Received** event
4. Enable webhook

### Step 10: Monitor Logs

```bash
heroku logs --tail
```

---

## 🔵 **OPTION 3: AWS EC2 (Production)**

### Step 1: Launch EC2 Instance

1. Go to **AWS Console** → **EC2**
2. Click **Launch Instance**
3. Select: **Ubuntu 22.04 LTS**
4. Instance type: **t3.micro** (free tier)
5. Configure security group:
   - Allow HTTP (80)
   - Allow HTTPS (443)
   - Allow SSH (22)

### Step 2: Connect to Instance

```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

### Step 3: Install Dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

### Step 4: Clone Repository

```bash
git clone your-repo-url
cd acebuddy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5: Configure Nginx

Create `/etc/nginx/sites-available/acebuddy`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/acebuddy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Set Up SSL (HTTPS)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Step 7: Create Systemd Service

Create `/etc/systemd/system/acebuddy.service`:

```ini
[Unit]
Description=AceBuddy API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/acebuddy
Environment="OPENAI_API_KEY=your_api_key"
Environment="API_HOST=127.0.0.1"
Environment="API_PORT=8000"
ExecStart=/home/ubuntu/acebuddy/venv/bin/python src/enhanced_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 8: Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable acebuddy
sudo systemctl start acebuddy
```

### Step 9: Get Your URL

```
https://your-domain.com/webhook/salesiq
```

---

## 🟣 **OPTION 4: DigitalOcean App Platform (Simple)**

### Step 1: Connect GitHub

1. Go to **DigitalOcean** → **Apps**
2. Click **Create App**
3. Connect your GitHub repository

### Step 2: Configure App

1. Select Python as runtime
2. Set build command: `pip install -r requirements.txt`
3. Set run command: `python src/enhanced_api.py`

### Step 3: Set Environment Variables

1. Add `OPENAI_API_KEY`
2. Add `API_HOST=0.0.0.0`
3. Add `API_PORT=8080`

### Step 4: Deploy

Click **Deploy** and wait for deployment to complete.

### Step 5: Get Your URL

```
https://your-app-name.ondigitalocean.app/webhook/salesiq
```

---

## 📋 **Quick Comparison**

| Option | Setup Time | Cost | Best For | HTTPS |
|--------|-----------|------|----------|-------|
| Ngrok | 2 min | Free | Testing | ✅ |
| Heroku | 10 min | Free/Paid | Quick Deploy | ✅ |
| AWS EC2 | 30 min | Free/Paid | Production | ✅ |
| DigitalOcean | 15 min | $5+/mo | Production | ✅ |
| Your Server | 20 min | Variable | Full Control | ✅ |

---

## 🧪 **Testing Your Deployment**

### Test 1: Health Check

```bash
curl https://your-webhook-url/
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "AceBuddy Hybrid RAG API",
  "version": "2.0.0"
}
```

### Test 2: Test Connection

```bash
curl https://your-webhook-url/zoho/test
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Connected to Zoho Desk successfully"
}
```

### Test 3: SalesIQ Webhook

```bash
curl -X POST https://your-webhook-url/webhook/salesiq \
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
  "ticket_created": false,
  "escalate": false
}
```

---

## 🔐 **Security Checklist**

- [ ] API key stored in environment variables (not in code)
- [ ] HTTPS enabled (not HTTP)
- [ ] Firewall configured (only necessary ports open)
- [ ] Rate limiting enabled
- [ ] CORS configured properly
- [ ] Webhook secret validated
- [ ] Logs monitored
- [ ] Backups configured

---

## 📊 **Monitoring & Logs**

### Ngrok
```bash
# View logs in terminal
# Or go to http://127.0.0.1:4040
```

### Heroku
```bash
heroku logs --tail
```

### AWS EC2
```bash
sudo journalctl -u acebuddy -f
```

### DigitalOcean
```bash
# View in dashboard
# Or use: doctl apps logs <app-id>
```

---

## 🚨 **Troubleshooting**

### Webhook Not Receiving Messages

1. Check webhook URL is correct
2. Check webhook is enabled in SalesIQ
3. Check firewall allows incoming requests
4. Check logs for errors
5. Test with curl command

### API Not Responding

1. Check API is running: `curl http://localhost:8000`
2. Check port is correct
3. Check environment variables are set
4. Check logs for errors
5. Restart API service

### HTTPS Certificate Issues

1. Check certificate is valid
2. Check domain is correct
3. Check certificate is not expired
4. Renew certificate if needed

---

## 📝 **Environment Variables Needed**

```bash
# Required
OPENAI_API_KEY=your_api_key

# Optional (will use defaults)
API_HOST=0.0.0.0
API_PORT=8000
OPENAI_MODEL=gpt-4-turbo-preview
CHROMA_PERSIST_DIRECTORY=./data/chroma

# For Zoho Desk (add later)
ZOHO_DESK_API_KEY=your_key
ZOHO_DESK_ORG_ID=your_org_id
ZOHO_DESK_DEPARTMENT_ID=your_dept_id
```

---

## 🎯 **Next Steps After Deployment**

1. ✅ Get webhook URL
2. ✅ Configure SalesIQ webhook
3. ✅ Test with curl
4. ✅ Test in SalesIQ chat widget
5. ✅ Add Zoho Desk credentials
6. ✅ Test ticket creation
7. ✅ Monitor logs
8. ✅ Optimize performance

---

## 📞 **Support**

**Need Help?**
- Check logs for errors
- Test with curl commands
- Verify environment variables
- Check firewall/security groups
- Review deployment guide

---

**Status:** ✅ Ready to Deploy
**Version:** 1.0.0
