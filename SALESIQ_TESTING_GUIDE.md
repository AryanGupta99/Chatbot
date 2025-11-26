# 🧪 SalesIQ Testing Guide - Live Chat Widget Testing

## 🎯 Overview

This guide shows how to test AceBuddy integration with SalesIQ chat widget in real-time.

---

## 📋 Prerequisites

- ✅ API deployed with public URL (webhook URL)
- ✅ SalesIQ webhook configured
- ✅ SalesIQ chat widget installed on your website
- ✅ API running and accessible

---

## 🚀 Step 1: Verify Webhook Configuration

### In Zoho SalesIQ

1. Go to **Settings** → **Webhooks**
2. Find your webhook
3. Verify:
   - ✅ URL: `https://your-url/webhook/salesiq`
   - ✅ Event: Message Received
   - ✅ Status: Enabled
   - ✅ Active: Yes

### Test Webhook

```bash
curl -X POST https://your-webhook-url/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "test_123",
    "visitor_id": "visitor_456",
    "visitor_email": "test@company.com",
    "visitor_name": "Test User",
    "message": "Hello"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "response": "Hello! I'm AceBuddy...",
  "escalate": false
}
```

---

## 🧪 Step 2: Test in SalesIQ Chat Widget

### Test Scenario 1: Greeting

**In SalesIQ Chat Widget:**
```
You: "Hello"
```

**Expected Response:**
```
AceBuddy: "Hello! I'm AceBuddy, your AI support assistant. 
I'm here to help you with QuickBooks, Remote Desktop, Email, 
Server issues, and more. What can I help you with today?"
```

### Test Scenario 2: Password Reset Workflow

**In SalesIQ Chat Widget:**
```
You: "I forgot my password"
```

**Expected Response:**
```
AceBuddy: "What's your username or email?"
```

**Continue:**
```
You: "john.doe@company.com"

AceBuddy: "What's your registered phone number? (last 4 digits)"

You: "1234"

AceBuddy: "✅ Your request has been logged!

Ticket ID: TKT-123456
Ticket Number: 1000001

Our support team has been notified and will assist you shortly.
You'll receive updates via email at john.doe@company.com."
```

### Test Scenario 3: Disk Upgrade Workflow

**In SalesIQ Chat Widget:**
```
You: "My disk is full"
```

**Expected Response:**
```
AceBuddy: "Your disk is low. Upgrade options:
• 200 GB – $120/month
• 100 GB – $60/month
• 80 GB – $50/month
• 60 GB – $40/month
• 40 GB – $28/month"
```

**Continue:**
```
You: "100GB"

AceBuddy: "Your upgrade request has been sent to your POC for approval.
Ticket ID: TKT-123457
We'll notify you once approved"
```

### Test Scenario 4: Server Slowness Workflow

**In SalesIQ Chat Widget:**
```
You: "My server is running slow"
```

**Expected Response:**
```
AceBuddy: "Open Task Manager (Ctrl+Shift+Esc)
What's your CPU percentage? (1-100)"
```

**Continue:**
```
You: "85"

AceBuddy: "High CPU detected. Close unused applications and restart.
Did that help?"

You: "Yes"

AceBuddy: "Great! Your issue is resolved."
```

---

## 📊 Monitoring During Testing

### Terminal 1: API Logs

Keep this terminal open to see API logs:

```bash
# You should see logs like:
# INFO:     127.0.0.1:60390 - "POST /webhook/salesiq HTTP/1.1" 200 OK
# INFO:     127.0.0.1:60395 - "POST /webhook/salesiq HTTP/1.1" 200 OK
```

### Terminal 2: Ngrok Logs

Keep ngrok terminal open to see webhook requests:

```bash
# You should see requests like:
# POST /webhook/salesiq                    200 OK
# POST /webhook/salesiq                    200 OK
```

### Check Logs

```bash
# If using Heroku
heroku logs --tail

# If using AWS
sudo journalctl -u acebuddy -f

# If using DigitalOcean
# Check in dashboard
```

---

## ✅ Test Checklist

### Basic Functionality
- [ ] Chat widget loads
- [ ] Can type messages
- [ ] AceBuddy responds
- [ ] Responses are relevant
- [ ] Workflow detection works

### Workflow Tests
- [ ] Password reset workflow works
- [ ] Disk upgrade workflow works
- [ ] Server slowness workflow works
- [ ] RDP connection workflow works
- [ ] Email issues workflow works
- [ ] Printer issues workflow works
- [ ] User management workflow works
- [ ] Monitor setup workflow works
- [ ] QB issues workflow works
- [ ] Account locked workflow works

### Response Quality
- [ ] Responses are helpful
- [ ] Responses are accurate
- [ ] Responses are timely
- [ ] Responses are formatted well
- [ ] Quick actions appear (when applicable)

### Session Management
- [ ] Chat history maintained
- [ ] Multiple messages work
- [ ] Session persists
- [ ] Can continue conversation

### Error Handling
- [ ] Invalid input handled
- [ ] Errors don't crash
- [ ] Fallback responses work
- [ ] Escalation works

---

## 🐛 Debugging Issues

### Issue: No Response from AceBuddy

**Check:**
1. Is webhook URL correct in SalesIQ?
2. Is webhook enabled?
3. Is API running?
4. Check API logs for errors
5. Test with curl command

**Fix:**
```bash
# Test webhook
curl -X POST https://your-webhook-url/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"test","visitor_id":"test","visitor_email":"test@test.com","visitor_name":"Test","message":"Hello"}'
```

### Issue: Wrong Response

**Check:**
1. Is workflow detection working?
2. Check API logs for workflow type
3. Verify trigger keywords
4. Check RAG engine is working

**Fix:**
```bash
# Check if workflow detected
# Look for "workflow_type" in logs
```

### Issue: Slow Response

**Check:**
1. Is API overloaded?
2. Is network slow?
3. Is OpenAI API slow?
4. Check API response time

**Fix:**
```bash
# Check API health
curl https://your-webhook-url/health
```

### Issue: Webhook Not Triggering

**Check:**
1. Is webhook URL correct?
2. Is webhook enabled in SalesIQ?
3. Is firewall blocking?
4. Check ngrok logs

**Fix:**
```bash
# Check ngrok is forwarding
# Look for POST requests in ngrok terminal
```

---

## 📈 Performance Testing

### Test Response Time

```bash
# Measure response time
time curl -X POST https://your-webhook-url/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"test","visitor_id":"test","visitor_email":"test@test.com","visitor_name":"Test","message":"Hello"}'
```

**Expected:** < 2 seconds

### Test Multiple Messages

Send 10 messages in quick succession:

```bash
for i in {1..10}; do
  curl -X POST https://your-webhook-url/webhook/salesiq \
    -H "Content-Type: application/json" \
    -d "{\"chat_id\":\"test_$i\",\"visitor_id\":\"visitor_$i\",\"visitor_email\":\"test@test.com\",\"visitor_name\":\"Test\",\"message\":\"Message $i\"}"
done
```

**Expected:** All succeed without errors

---

## 🎯 Test Scenarios by Workflow

### 1. Password Reset
```
Message: "I forgot my password"
Expected: Workflow starts, asks for username
```

### 2. Disk Upgrade
```
Message: "My disk is full"
Expected: Shows upgrade options
```

### 3. Server Slowness
```
Message: "Server is slow"
Expected: Asks for CPU/RAM/Disk metrics
```

### 4. RDP Connection
```
Message: "Can't connect to RDP"
Expected: Asks for error message
```

### 5. Email Issues
```
Message: "Email won't sync"
Expected: Asks for issue type
```

### 6. Printer Issues
```
Message: "Printer is offline"
Expected: Asks for issue type
```

### 7. User Management
```
Message: "Add new user"
Expected: Asks for user details
```

### 8. Monitor Setup
```
Message: "How to set up monitors"
Expected: Asks for setup type
```

### 9. QB Issues
```
Message: "QuickBooks won't start"
Expected: Asks for issue type
```

### 10. Account Locked
```
Message: "My account is locked"
Expected: Asks for username
```

---

## 📊 Logging & Monitoring

### Enable Debug Logging

Add to `.env`:
```bash
LOG_LEVEL=DEBUG
```

### View Logs

**Ngrok:**
```bash
# Terminal shows all requests
# Or go to http://127.0.0.1:4040
```

**API:**
```bash
# Terminal shows all logs
# Look for workflow_type, confidence, source
```

### Log Format

```
INFO:     127.0.0.1:60390 - "POST /webhook/salesiq HTTP/1.1" 200 OK
{
  "status": "success",
  "response": "What's your username?",
  "workflow_type": "password_reset",
  "confidence": "high",
  "source": "automation_workflow"
}
```

---

## 🎉 Success Criteria

✅ **All tests pass if:**
- Chat widget responds to messages
- Workflows are detected correctly
- Responses are helpful and accurate
- Session history is maintained
- No errors in logs
- Response time < 2 seconds
- Multiple messages work
- All 13 workflows work

---

## 📝 Test Report Template

```
Date: 2025-11-26
Tester: Your Name
Environment: Ngrok / Heroku / AWS

Test Results:
- Greeting: ✅ PASS
- Password Reset: ✅ PASS
- Disk Upgrade: ✅ PASS
- Server Slowness: ✅ PASS
- RDP Connection: ✅ PASS
- Email Issues: ✅ PASS
- Printer Issues: ✅ PASS
- User Management: ✅ PASS
- Monitor Setup: ✅ PASS
- QB Issues: ✅ PASS
- Account Locked: ✅ PASS

Performance:
- Average Response Time: 1.2 seconds
- Max Response Time: 2.1 seconds
- Error Rate: 0%

Issues Found:
- None

Recommendations:
- Ready for production
```

---

## 🚀 Next Steps

1. ✅ Deploy API with public URL
2. ✅ Configure SalesIQ webhook
3. ✅ Test all workflows
4. ✅ Monitor logs
5. ✅ Add Zoho Desk credentials
6. ✅ Test ticket creation
7. ✅ Go live!

---

**Status:** ✅ Ready to Test
**Version:** 1.0.0
