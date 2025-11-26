# ⚡ Zoho Desk Integration - Quick Start

## 5-Minute Setup

### Step 1: Get Zoho Credentials (2 min)

1. Log in to **Zoho Desk**
2. Go to **Settings** → **API**
3. Copy your **Organization ID**
4. Create API token (or use existing)
5. Go to **Settings** → **Departments**
6. Copy your **Department ID**

### Step 2: Configure Environment (1 min)

Add to `.env`:
```bash
ZOHO_DESK_API_KEY=your_api_key_here
ZOHO_DESK_ORG_ID=your_org_id_here
ZOHO_DESK_DEPARTMENT_ID=your_department_id_here
```

### Step 3: Create Config File (1 min)

Create `config/zoho_desk_config.json`:
```json
{
  "department_id": "your_department_id",
  "default_assignee": "assignee_id_optional",
  "ticket_source": "SalesIQ",
  "custom_fields": {}
}
```

### Step 4: Configure SalesIQ Webhook (1 min)

1. Go to **Zoho SalesIQ** → **Settings** → **Webhooks**
2. Add webhook: `https://your-domain.com/webhook/salesiq`
3. Select: **Message Received** event
4. Enable webhook

### Step 5: Test Connection

```bash
curl http://localhost:8000/zoho/test
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Connected to Zoho Desk successfully"
}
```

---

## How It Works (Simple Flow)

```
Customer in SalesIQ Chat
        ↓
"I forgot my password"
        ↓
AceBuddy detects workflow
        ↓
Asks for username
        ↓
Verifies identity
        ↓
Creates ticket in Zoho Desk
        ↓
Customer sees: "Ticket ID: TKT-123456"
        ↓
Support team gets notification
        ↓
Support team resolves
        ↓
Ticket closed
```

---

## What Happens Automatically

### When Customer Sends Message

1. ✅ Message received via SalesIQ webhook
2. ✅ AceBuddy processes message
3. ✅ Workflow detected (if applicable)
4. ✅ Customer guided through steps

### When Workflow Completes

1. ✅ Contact created/found in Zoho Desk
2. ✅ Ticket created with all details
3. ✅ Chat linked to ticket
4. ✅ Customer notified with ticket ID
5. ✅ Support team notified
6. ✅ Chat history added as comments

---

## Customer Experience

### In SalesIQ Chat

```
Customer: "I forgot my password"

Bot: "What's your username or email?"
Customer: "john.doe@company.com"

Bot: "What's your registered phone? (last 4 digits)"
Customer: "1234"

Bot: "✅ Your request has been logged!

Ticket ID: TKT-123456
Ticket Number: 1000001

Our support team has been notified and will assist you shortly.
You'll receive updates via email at john.doe@company.com."
```

### In Customer Email

```
Subject: Your Support Ticket #1000001

Hello John,

Your support request has been received and logged in our system.

Ticket Details:
- Ticket ID: TKT-123456
- Ticket Number: 1000001
- Subject: Password Reset
- Status: Open
- Priority: Medium

Expected Resolution Time: 2-4 hours

Our support team will contact you shortly.

Best regards,
AceBuddy Support Team
```

### In Zoho Desk (Support Team)

```
Ticket #1000001
Subject: Password Reset - John Doe
Status: Open
Priority: Medium
Customer: john.doe@company.com

Chat History:
- Customer: "I forgot my password"
- Bot: "What's your username or email?"
- Customer: "john.doe@company.com"
- Bot: "What's your registered phone? (last 4 digits)"
- Customer: "1234"

Workflow: password_reset
Source: AceBuddy (SalesIQ)
Created: 2025-11-26 16:50:00

Action: Process password reset
```

---

## API Endpoints Quick Reference

### Create Ticket
```bash
POST /zoho/ticket/create
```

### Get Ticket
```bash
GET /zoho/ticket/{ticket_id}
```

### Add Comment
```bash
POST /zoho/ticket/{ticket_id}/comment
```

### Update Status
```bash
PATCH /zoho/ticket/{ticket_id}/status
```

### Test Connection
```bash
GET /zoho/test
```

### SalesIQ Webhook
```bash
POST /webhook/salesiq
```

---

## Supported Workflows

All 13 automation workflows create tickets:

1. ✅ Disk Space Upgrade
2. ✅ Password Reset
3. ✅ User Management
4. ✅ Monitor Setup
5. ✅ Printer Issues
6. ✅ Server Slowness
7. ✅ RDP Connection
8. ✅ Server Reboot
9. ✅ QB MFA
10. ✅ Email Issues
11. ✅ QB Issues
12. ✅ Windows Update
13. ✅ Account Locked

---

## Ticket Priority Mapping

| Workflow | Priority |
|----------|----------|
| Server Reboot | High |
| Account Locked | High |
| Server Slowness | High |
| RDP Connection | High |
| Password Reset | Medium |
| Email Issues | Medium |
| QB Issues | Medium |
| Printer Issues | Medium |
| Disk Upgrade | Low |
| Monitor Setup | Low |
| User Management | Low |
| QB MFA | Medium |
| Windows Update | Medium |

---

## Troubleshooting

### Tickets Not Creating?

1. Check API key: `curl http://localhost:8000/zoho/test`
2. Check environment variables in `.env`
3. Check Department ID is correct
4. Check API logs for errors

### Webhook Not Working?

1. Verify webhook URL is accessible
2. Check SalesIQ webhook is enabled
3. Check firewall allows incoming requests
4. Test with: `curl -X POST http://localhost:8000/webhook/salesiq ...`

### Customer Not Notified?

1. Check email configuration
2. Verify customer email is correct
3. Check spam filters
4. Check SMTP credentials

---

## Testing

### Test 1: Connection
```bash
curl http://localhost:8000/zoho/test
```

### Test 2: Create Ticket
```bash
curl -X POST http://localhost:8000/zoho/ticket/create \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Test",
    "user_id": "test@company.com",
    "metadata": {
      "subject": "Test",
      "priority": "Low",
      "workflow_type": "test"
    }
  }'
```

### Test 3: SalesIQ Webhook
```bash
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "test_123",
    "visitor_id": "visitor_456",
    "visitor_email": "test@company.com",
    "visitor_name": "Test User",
    "message": "I forgot my password"
  }'
```

---

## Next Steps

1. ✅ Configure credentials
2. ✅ Set up webhook
3. ✅ Test connection
4. ✅ Test ticket creation
5. ✅ Train support team
6. ✅ Monitor metrics
7. ✅ Optimize workflows

---

## Support

**Need Help?**
- Check: `ZOHO_DESK_INTEGRATION_GUIDE.md`
- Test: `/zoho/test` endpoint
- Logs: Check application logs
- Docs: See full integration guide

---

**Status:** ✅ Ready to Deploy
**Version:** 1.0.0
