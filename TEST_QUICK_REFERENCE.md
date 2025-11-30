# Quick Test Reference Card

## 🚀 Status
✅ Pushed to GitHub (Commit: 2ecf0b5)
⏳ Render deploying (2-3 minutes)

## Quick Tests for SalesIQ

### 1️⃣ Greeting
```
Send: "Hello"
Expect: "Hello! I'm AceBuddy. How can I assist you today?"
```

### 2️⃣ Password Reset
```
Send: "I need to reset my password"
Expect: Asks if registered on SelfCare (short response)

Send: "Yes"
Expect: Detailed reset steps
```

### 3️⃣ Disk Full
```
Send: "My disk is full"
Expect: Asks to check current space (short response)

Send: "I have 2GB left"
Expect: Cleanup steps + upgrade options
```

### 4️⃣ QuickBooks
```
Send: "QuickBooks error"
Expect: Asks for error code (short response)

Send: "Error -6177"
Expect: Specific solution for -6177
```

### 5️⃣ RDP Connection
```
Send: "Can't connect to remote desktop"
Expect: Asks about OS and error (short response)

Send: "Mac, connection failed"
Expect: Mac-specific troubleshooting steps
```

## What to Verify ✅
- Short greeting (no long intro)
- Asks questions first (2-3 sentences)
- Detailed solutions after clarification
- Natural conversation flow
- No information dumping

## Before vs After

**Before:** Long greeting + immediate info dump
**After:** Short greeting + clarifying questions + tailored solutions

## Ready to Test!
Open SalesIQ widget and try the scenarios above.
