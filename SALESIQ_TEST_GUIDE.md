# SalesIQ Conversational Chatbot Test Guide

## 🚀 Deployment Status

✅ **Pushed to GitHub:** Commit `2ecf0b5`
⏳ **Render Deploying:** Wait 2-3 minutes
🧪 **Ready to Test:** After Render shows "Deploy live"

## Quick Test Scenarios

### Test 1: Greeting ✅
**What to send:**
```
Hello
```

**Expected Response:**
```
Hello! I'm AceBuddy. How can I assist you today?
```

**What to check:**
- ✅ Short and simple
- ✅ No long introduction
- ✅ Friendly tone

---

### Test 2: Password Reset 🔑

**Step 1 - Initial Request:**
```
I need to reset my password
```

**Expected Response:**
```
I can help with that! Are you currently registered on our SelfCare portal at https://selfcare.acecloudhosting.com?
```

**What to check:**
- ✅ Asks clarifying question
- ✅ Short response (2-3 sentences)
- ✅ Includes SelfCare URL

**Step 2 - Follow-up (Yes):**
```
Yes, I'm registered
```

**Expected Response:**
```
Great! Here's how you can reset your password:

1. Go to the SelfCare portal: https://selfcare.acecloudhosting.com
2. Click on "Forgot Password"
3. Enter your registered email address
4. Check your email for a reset link (2-3 minutes)
5. Follow the instructions in the email

Make sure you have Google Authenticator handy if you've enrolled. Let me know if you need any help!
```

**What to check:**
- ✅ Detailed steps provided
- ✅ Numbered list
- ✅ Includes timeframe
- ✅ Helpful and complete

**Step 2 - Follow-up (No):**
```
No, I'm not registered
```

**Expected Response:**
```
No problem! Since you're not enrolled in the SelfCare portal yet, please contact our support team:
- Email: support@acecloudhosting.com
- They'll help you reset your password and get you set up on SelfCare

The support team typically responds within 2-4 hours.
```

---

### Test 3: Disk Full 💾

**Step 1 - Initial Request:**
```
My disk is full
```

**Expected Response:**
```
Let me help you with that. First, can you check how much space you currently have? Right-click on your C: drive and select Properties.
```

**What to check:**
- ✅ Asks for current space
- ✅ Provides simple instruction
- ✅ Short response

**Step 2 - Follow-up:**
```
I have only 2GB left
```

**Expected Response:**
```
Thanks for checking! Here are some quick steps to free up space:

Quick Cleanup:
1. Delete temp files: Press Windows + R, type %temp%, delete all files
2. Run Disk Cleanup: Search for "Disk Cleanup" in Start menu
3. Empty Recycle Bin

Need More Space?
We offer storage upgrades:
- 40GB: $10/month
- 80GB: $20/month
- 120GB: $30/month
- 200GB: $50/month

Upgrade requests are processed in 2-4 hours. Would you like me to help you request an upgrade?
```

**What to check:**
- ✅ Cleanup steps provided
- ✅ Upgrade options listed
- ✅ Pricing included
- ✅ Timeframe mentioned

---

### Test 4: QuickBooks Error 📊

**Step 1 - Initial Request:**
```
QuickBooks is not working
```

**Expected Response:**
```
I can assist with QuickBooks issues. What's the specific error code or message you're seeing?
```

**What to check:**
- ✅ Asks for error code
- ✅ Short and direct
- ✅ Helpful tone

**Step 2 - Follow-up:**
```
Error -6177
```

**Expected Response:**
```
Thanks for sharing that! Error -6177 indicates the Database Server Manager isn't running. Here's how to fix it:

1. Press Windows + R, type "services.msc", press Enter
2. Find "QuickBooksDBXX" (XX is your QB version)
3. Right-click and select "Start"
4. Try opening QuickBooks again

This should resolve the issue immediately. If you still see the error, let me know and I'll help you troubleshoot further!
```

**What to check:**
- ✅ Specific solution for error -6177
- ✅ Step-by-step instructions
- ✅ Clear and actionable
- ✅ Offers further help

---

### Test 5: RDP Connection 🖥️

**Step 1 - Initial Request:**
```
Can't connect to remote desktop
```

**Expected Response:**
```
I'll help you troubleshoot this. Are you connecting from Windows or Mac? And what error message are you seeing?
```

**What to check:**
- ✅ Asks about OS
- ✅ Asks about error message
- ✅ Two clarifying questions

**Step 2 - Follow-up:**
```
I'm on Mac and getting connection failed error
```

**Expected Response:**
```
Thanks for the info! Here are steps to fix the connection failed error on Mac:

1. Check your internet connection (try opening a website)
2. Open Microsoft Remote Desktop app (NOT built-in)
3. Verify server address: server.acecloudhosting.com
4. Double-check your username and password
5. Check if Mac firewall is blocking: System Preferences > Security & Privacy > Firewall

If you don't have Microsoft Remote Desktop, download it from the Mac App Store (it's free).

Still having issues? Let me know and I'll help you further!
```

**What to check:**
- ✅ Mac-specific solution
- ✅ Step-by-step instructions
- ✅ Mentions correct app
- ✅ Offers further help

---

## What Changed? 🎯

### Before ❌
- Long greeting with unnecessary text
- Immediate information dump
- All steps provided at once
- Overwhelming for users
- Not conversational

### After ✅
- Short, friendly greeting
- Asks clarifying questions first
- Provides detailed solution after understanding context
- Natural conversation flow
- User-friendly

---

## Testing Checklist

### Initial Tests:
- [ ] Test greeting message
- [ ] Test password reset flow (registered)
- [ ] Test password reset flow (not registered)
- [ ] Test disk full flow
- [ ] Test QuickBooks error flow
- [ ] Test RDP connection flow

### Verify Behavior:
- [ ] Greeting is simplified
- [ ] Bot asks questions before providing solutions
- [ ] Responses are conversational
- [ ] No information dumping
- [ ] Solutions are tailored to user's situation

### Edge Cases:
- [ ] Test with vague questions
- [ ] Test with multiple issues in one message
- [ ] Test conversation continuity
- [ ] Test escalation scenarios

---

## How to Access SalesIQ Widget

1. Go to your website where SalesIQ is installed
2. Look for the chat widget (usually bottom-right corner)
3. Click to open chat
4. Start testing!

---

## Troubleshooting

### If bot behavior hasn't changed:
1. **Clear cache:** Close and reopen browser
2. **New conversation:** Start a fresh chat session
3. **Check Render:** Verify deployment completed
4. **Check logs:** Look at Render logs for errors

### If responses are still too long:
1. **Wait:** Render might still be deploying old version
2. **Restart:** Restart Render service
3. **Verify:** Check GitHub commit is deployed

### If getting errors:
1. **Check API:** Test `/health` endpoint
2. **Check logs:** Look at Render logs
3. **Check env vars:** Verify OPENAI_API_KEY is set

---

## Success Indicators ✅

You'll know it's working when:
1. Greeting is short and simple
2. Bot asks clarifying questions first
3. Detailed solutions come after understanding context
4. Conversation feels natural
5. Users aren't overwhelmed with information

---

## Next Steps After Testing

1. ✅ Verify all test scenarios work
2. ✅ Test with real user questions
3. ✅ Monitor user feedback
4. ✅ Check conversation quality
5. ✅ Adjust prompts if needed

---

## Need Help?

If something doesn't work as expected:
1. Check Render deployment status
2. Review Render logs
3. Test API endpoints directly
4. Verify environment variables
5. Check GitHub commit is correct

---

## Status: 🚀 READY TO TEST

Wait for Render deployment to complete (2-3 minutes), then start testing with SalesIQ!
