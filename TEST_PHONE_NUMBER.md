# Test Phone Number on Render & SalesIQ

## ✅ Deployed to GitHub
**Commit:** `e49fafa`
**Changes:** Added support phone number 1-888-415-5240

## ⏳ Render Deployment
**Status:** Deploying now (2-3 minutes)
**Check:** https://dashboard.render.com

---

## 🧪 Quick Tests for SalesIQ

### Test 1: Ask for Phone Number
```
You: "What's your phone number?"
Expected: "Phone: 1-888-415-5240"
```

### Test 2: Ask for Contact Info
```
You: "How do I contact support?"
Expected: "Phone: 1-888-415-5240 | Email: support@acecloudhosting.com"
```

### Test 3: Ask for Support Number
```
You: "Give me the support number"
Expected: "1-888-415-5240"
```

### Test 4: Password Reset (Not Registered)
```
You: "I need to reset my password"
Bot: "Are you registered on SelfCare?"
You: "No"
Expected: Should include "1-888-415-5240" in response
```

### Test 5: Disk Upgrade Request
```
You: "I need more disk space"
Bot: "How much space do you need?"
You: "200GB"
Expected: Should include "1-888-415-5240" for upgrade request
```

---

## ✅ What to Verify

When testing on SalesIQ, check that:
- [ ] Phone number appears when asked directly
- [ ] Format is correct: 1-888-415-5240
- [ ] Appears with email: support@acecloudhosting.com
- [ ] Shows in escalation scenarios
- [ ] Included in password reset (not registered)
- [ ] Included in upgrade requests

---

## 📊 Expected Responses

### Direct Contact Request
```
User: "What's your phone number?"
Bot: "You can reach our support team at:
     Phone: 1-888-415-5240
     Email: support@acecloudhosting.com
     How can I help you today?"
```

### Full Contact Info
```
User: "How do I contact support?"
Bot: "You can reach our support team in a few ways:
     1. Phone: Call us at 1-888-415-5240
     2. Email: Send a message to support@acecloudhosting.com
     3. Chat: You can chat with us right here!
     How can I assist you today?"
```

### Quick Number Request
```
User: "Give me the support number"
Bot: "You can reach our support team at 1-888-415-5240. 
     How can I assist you today?"
```

---

## 🔍 Where Phone Number Appears

The bot will provide **1-888-415-5240** when:
1. ✅ User asks "what's your phone number?"
2. ✅ User asks "how to contact support?"
3. ✅ User needs to escalate an issue
4. ✅ User is not registered on SelfCare
5. ✅ User needs upgrades (disk, RAM, etc.)
6. ✅ User has complex issues requiring human support

---

## 🚀 Testing Steps

### Step 1: Wait for Render Deployment
1. Go to https://dashboard.render.com
2. Find "acebuddy-api" service
3. Check "Events" tab
4. Wait for "Deploy live" status (~2-3 minutes)

### Step 2: Test on SalesIQ Widget
1. Open your website with SalesIQ widget
2. Start a new chat
3. Try the test scenarios above
4. Verify phone number appears correctly

### Step 3: Verify Format
Check that phone number is:
- ✅ Complete: 1-888-415-5240
- ✅ Formatted correctly (with dashes)
- ✅ Accompanied by email when appropriate
- ✅ Easy to read and copy

---

## 🐛 Troubleshooting

### If phone number doesn't appear:
1. **Wait:** Render might still be deploying old version
2. **Clear cache:** Close and reopen browser/SalesIQ
3. **New chat:** Start a fresh conversation
4. **Check Render:** Verify deployment shows "Deploy live"
5. **Check logs:** Look at Render logs for errors

### If format is wrong:
1. Check that you're seeing the latest deployment
2. Verify commit `e49fafa` is deployed
3. Restart Render service if needed

---

## 📞 Contact Format Reference

**Full Format:**
```
Chat | Phone: 1-888-415-5240 | Email: support@acecloudhosting.com
```

**Phone Only:**
```
Phone: 1-888-415-5240
```

**In Sentence:**
```
Contact support@acecloudhosting.com or call 1-888-415-5240
```

---

## ✅ Success Checklist

After Render deploys, verify:
- [ ] Phone number appears when asked directly
- [ ] Number is correct: 1-888-415-5240
- [ ] Format is consistent
- [ ] Appears in escalation scenarios
- [ ] Works in conversational flow
- [ ] Easy for users to find and use

---

## 🎯 Quick Verification

**Fastest test:**
```
Just send: "What's your phone number?"
Should get: "1-888-415-5240"
```

If you see the phone number, everything is working! ✅

---

## Status: 🚀 DEPLOYED

**Next:** Wait 2-3 minutes for Render, then test on SalesIQ!
