# 🔗 Zoho Desk Integration Guide

## Overview

AceBuddy now integrates seamlessly with **Zoho Desk** to automatically create tickets from SalesIQ chat conversations. When a customer initiates a support request through the SalesIQ chat widget, AceBuddy:

1. ✅ Detects the request type
2. ✅ Guides the customer through the workflow
3. ✅ Creates a ticket in Zoho Desk automatically
4. ✅ Notifies the customer with ticket details
5. ✅ Links the chat to the ticket
6. ✅ Notifies the support team

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SalesIQ Chat Widget                      │
│                   (Customer Facing)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              AceBuddy Hybrid Chatbot                        │
│  • Detects workflow type                                   │
│  • Guides customer through steps                           │
│  • Collects required information                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           SalesIQ Handler & Zoho Desk Integration          │
│  • Creates contact if needed                               │
│  • Creates ticket in Zoho Desk                             │
│  • Links chat to ticket                                    │
│  • Sends notifications                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    ┌────────┐      ┌──────────┐    ┌──────────┐
    │ Zoho   │      │ Support  │    │ Customer │
    │ Desk   │      │ Team     │    │ (Email)  │
    │Ticket  │      │(Notified)│    │(Notified)│
    └────────┘      └──────────┘    └──────────┘
```

---

## 🔧 Setup & Configuration

### 1. Get Zoho Desk API Credentials

1. Go to **Zoho Desk** → **Settings** → **API**
2. Create a new API token or use existing one
3. Get your **Organization ID**
4. Get your **Department ID** (where tickets will be created)

### 2. Set Environment Variables

```bash
# .env file
ZOHO_DESK_API_KEY=your_api_key_here
ZOHO_DESK_ORG_ID=your_org_id_here
ZOHO_DESK_DEPARTMENT_ID=your_department_id_here
ZOHO_DESK_DEFAULT_ASSIGNEE=assignee_id_here
```

### 3. Create Configuration File

Create `config/zoho_desk_config.json`:

```json
{
  "department_id": "your_department_id",
  "default_assignee": "assignee_id",
  "ticket_source": "SalesIQ",
  "custom_fields": {
    "automation_source": "AceBuddy",
    "integration_type": "SalesIQ"
  }
}
```

### 4. Configure SalesIQ Webhook

In **Zoho SalesIQ**:
1. Go to **Settings** → **Webhooks**
2. Add webhook URL: `https://your-domain.com/webhook/salesiq`
3. Select events: **Message Received**
4. Enable webhook

---

## 📡 API Endpoints

### SalesIQ Webhook (Incoming Messages)

```bash
POST /webhook/salesiq
```

**Request:**
```json
{
  "chat_id": "chat_123",
  "visitor_id": "visitor_456",
  "visitor_email": "customer@company.com",
  "visitor_name": "John Doe",
  "visitor_phone": "555-1234",
  "message": "I forgot my password"
}
```

**Response:**
```json
{
  "status": "success",
  "response": "What's your username or email?",
  "ticket_created": false,
  "escalate": false,
  "timestamp": "2025-11-26T16:50:00Z"
}
```

### Create Zoho Desk Ticket

```bash
POST /zoho/ticket/create
```

**Request:**
```json
{
  "query": "I need to upgrade my disk storage",
  "user_id": "john@company.com",
  "metadata": {
    "subject": "Disk Space Upgrade Request",
    "priority": "Medium",
    "workflow_type": "disk_upgrade"
  }
}
```

**Response:**
```json
{
  "success": true,
  "ticket_id": "TKT-123456",
  "ticket_number": "1000001",
  "timestamp": "2025-11-26T16:50:00Z"
}
```

### Get Ticket Details

```bash
GET /zoho/ticket/{ticket_id}
```

**Response:**
```json
{
  "success": true,
  "ticket": {
    "id": "TKT-123456",
    "ticketNumber": "1000001",
    "subject": "Disk Space Upgrade Request",
    "status": "Open",
    "priority": "Medium",
    "email": "john@company.com"
  }
}
```

### Add Comment to Ticket

```bash
POST /zoho/ticket/{ticket_id}/comment
```

**Request:**
```json
{
  "comment": "Customer confirmed 100GB upgrade plan",
  "is_internal": false
}
```

**Response:**
```json
{
  "success": true,
  "comment_id": "CMT-789",
  "timestamp": "2025-11-26T16:50:00Z"
}
```

### Update Ticket Status

```bash
PATCH /zoho/ticket/{ticket_id}/status
```

**Request:**
```json
{
  "status": "Closed"
}
```

**Response:**
```json
{
  "success": true,
  "status": "Closed",
  "timestamp": "2025-11-26T16:50:00Z"
}
```

### Test Zoho Connection

```bash
GET /zoho/test
```

**Response:**
```json
{
  "success": true,
  "message": "Connected to Zoho Desk successfully",
  "timestamp": "2025-11-26T16:50:00Z"
}
```

### Get SalesIQ Session Info

```bash
GET /salesiq/session/{chat_id}
```

**Response:**
```json
{
  "success": true,
  "session": {
    "chat_id": "chat_123",
    "visitor_name": "John Doe",
    "visitor_email": "john@company.com",
    "ticket_id": "TKT-123456",
    "message_count": 5,
    "created_at": "2025-11-26T16:45:00Z"
  }
}
```

### Close SalesIQ Session

```bash
POST /salesiq/session/{chat_id}/close
```

**Response:**
```json
{
  "success": true,
  "message": "Session closed",
  "timestamp": "2025-11-26T16:50:00Z"
}
```

---

## 🎯 Complete Workflow Example

### Step 1: Customer Initiates Chat

```
Customer: "I forgot my password"
```

### Step 2: SalesIQ Sends Webhook

```json
{
  "chat_id": "chat_123",
  "visitor_id": "visitor_456",
  "visitor_email": "john@company.com",
  "visitor_name": "John Doe",
  "message": "I forgot my password"
}
```

### Step 3: AceBuddy Detects Workflow

- Detects "password" trigger
- Starts password_reset workflow
- Responds to customer

### Step 4: Customer Provides Details

```
Bot: "What's your username or email?"
Customer: "john.doe@company.com"

Bot: "What's your registered phone? (last 4 digits)"
Customer: "1234"
```

### Step 5: Ticket Created in Zoho Desk

**Automatically:**
1. Creates/finds contact in Zoho Desk
2. Creates ticket with all details
3. Links SalesIQ chat to ticket
4. Adds chat history as comments

**Ticket Details:**
- Subject: "Password Reset - John Doe"
- Description: Chat history + workflow details
- Status: Open
- Priority: Medium
- Custom Fields:
  - workflow_type: password_reset
  - automation_source: AceBuddy
  - salesiq_chat_id: chat_123

### Step 6: Customer Notified

```
Bot: "✅ Your request has been logged!

Ticket ID: TKT-123456
Ticket Number: 1000001

Our support team has been notified and will assist you shortly.
You'll receive updates via email at john@company.com."
```

### Step 7: Support Team Notified

**Email to Support Team:**
```
Subject: New Ticket - Password Reset - John Doe

Ticket ID: TKT-123456
Ticket Number: 1000001
Customer: John Doe (john@company.com)
Priority: Medium
Status: Open

Workflow: Password Reset
Source: AceBuddy (SalesIQ)

Chat History:
- Customer: "I forgot my password"
- Bot: "What's your username or email?"
- Customer: "john.doe@company.com"
- Bot: "What's your registered phone? (last 4 digits)"
- Customer: "1234"

Action Required: Process password reset request
```

---

## 📊 Ticket Information Flow

### What Gets Stored in Zoho Desk

1. **Contact Information**
   - Name
   - Email
   - Phone
   - Created automatically if new

2. **Ticket Details**
   - Subject (workflow type + customer name)
   - Description (formatted workflow data)
   - Status (Open)
   - Priority (based on workflow type)
   - Department (configured)

3. **Custom Fields**
   - workflow_type: password_reset, disk_upgrade, etc.
   - automation_source: AceBuddy
   - salesiq_chat_id: Link to SalesIQ chat
   - salesiq_visitor_id: Visitor identifier

4. **Chat History**
   - All messages stored as comments
   - Visible to support team
   - Marked as internal/external

5. **Workflow Data**
   - Collected information
   - User responses
   - Validation results

---

## 🔔 Notification System

### Customer Receives

1. **In SalesIQ Chat:**
   ```
   ✅ Your request has been logged!
   
   Ticket ID: TKT-123456
   Ticket Number: 1000001
   
   Our support team has been notified and will assist you shortly.
   You'll receive updates via email at john@company.com.
   ```

2. **Via Email:**
   - Ticket confirmation
   - Ticket number
   - Expected resolution time
   - Support team contact info

### Support Team Receives

1. **In Zoho Desk:**
   - New ticket notification
   - Full chat history
   - Customer information
   - Workflow details

2. **Via Email:**
   - Ticket alert
   - Customer details
   - Priority level
   - Action required

---

## 🎯 Workflow-Specific Ticket Creation

### Password Reset Workflow

**Ticket Created With:**
- Subject: "Password Reset - [Customer Name]"
- Priority: Medium
- Category: Account Management
- Details: Username, email, verification status

**Support Team Action:**
- Verify identity
- Reset password
- Send temporary password
- Update ticket status

### Disk Upgrade Workflow

**Ticket Created With:**
- Subject: "Disk Space Upgrade - [Customer Name]"
- Priority: Low
- Category: Infrastructure
- Details: Selected plan, current usage, approval status

**Support Team Action:**
- Get POC approval
- Process upgrade
- Provision storage
- Notify customer

### Server Slowness Workflow

**Ticket Created With:**
- Subject: "Server Performance Issue - [Customer Name]"
- Priority: High
- Category: Infrastructure
- Details: CPU/RAM/Disk metrics, diagnostics

**Support Team Action:**
- Investigate root cause
- Apply fixes
- Monitor performance
- Update ticket

---

## 🔐 Security & Privacy

### Data Protection

- ✅ All API calls use HTTPS
- ✅ API key stored in environment variables
- ✅ No sensitive data in logs
- ✅ Chat history encrypted in Zoho Desk
- ✅ Customer email verified before ticket creation

### Access Control

- ✅ Only authorized support team can view tickets
- ✅ Customer can only see their own tickets
- ✅ Internal comments hidden from customers
- ✅ Audit trail of all changes

### Compliance

- ✅ GDPR compliant data handling
- ✅ Data retention policies
- ✅ Customer consent for ticket creation
- ✅ Privacy policy integration

---

## 🧪 Testing

### Test Connection

```bash
curl http://localhost:8000/zoho/test
```

### Test Ticket Creation

```bash
curl -X POST http://localhost:8000/zoho/ticket/create \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Test ticket",
    "user_id": "test@company.com",
    "metadata": {
      "subject": "Test Ticket",
      "priority": "Low",
      "workflow_type": "test"
    }
  }'
```

### Test SalesIQ Webhook

```bash
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "test_chat_123",
    "visitor_id": "test_visitor_456",
    "visitor_email": "test@company.com",
    "visitor_name": "Test User",
    "message": "I forgot my password"
  }'
```

---

## 📈 Monitoring & Analytics

### Track Metrics

- Tickets created per day
- Average resolution time
- Customer satisfaction
- Workflow completion rate
- Escalation rate

### Dashboard Queries

```bash
# Get all tickets created by AceBuddy
GET /zoho/tickets?source=AceBuddy

# Get tickets by workflow type
GET /zoho/tickets?workflow_type=password_reset

# Get open tickets
GET /zoho/tickets?status=Open
```

---

## 🚀 Deployment Checklist

- [ ] Zoho Desk API credentials obtained
- [ ] Environment variables configured
- [ ] Configuration file created
- [ ] SalesIQ webhook configured
- [ ] API endpoints tested
- [ ] Ticket creation tested
- [ ] Email notifications configured
- [ ] Support team trained
- [ ] Customer communication updated
- [ ] Monitoring set up

---

## 🆘 Troubleshooting

### Tickets Not Creating

**Check:**
1. Zoho Desk API key is valid
2. Organization ID is correct
3. Department ID exists
4. API endpoint is accessible

**Test:**
```bash
curl http://localhost:8000/zoho/test
```

### Webhook Not Triggering

**Check:**
1. SalesIQ webhook URL is correct
2. Webhook is enabled in SalesIQ
3. API is accessible from internet
4. Firewall allows incoming requests

### Customer Not Receiving Notifications

**Check:**
1. Email configuration is correct
2. SMTP credentials are valid
3. Email address is correct
4. Spam filters not blocking

### Chat Not Linking to Ticket

**Check:**
1. chat_id is being passed correctly
2. visitor_id is being passed correctly
3. Custom fields are configured in Zoho Desk

---

## 📞 Support

**Status:** ✅ **PRODUCTION READY**

**Files:**
- `src/zoho_desk_integration.py` - Zoho Desk API integration
- `src/salesiq_handler.py` - SalesIQ message handling
- `src/enhanced_api.py` - API endpoints

**Documentation:**
- This file: Complete integration guide
- API endpoints: `/workflows`, `/stats`
- Test endpoints: `/zoho/test`

---

## 🎓 Example Scenarios

### Scenario 1: Password Reset via SalesIQ

1. Customer opens SalesIQ chat
2. Types: "I forgot my password"
3. AceBuddy detects workflow
4. Asks for username
5. Asks for verification
6. Creates ticket in Zoho Desk
7. Customer sees: "Ticket ID: TKT-123456"
8. Support team gets notification
9. Support team resets password
10. Customer receives new password via email

### Scenario 2: Disk Upgrade via SalesIQ

1. Customer: "My disk is full"
2. AceBuddy: Shows upgrade options
3. Customer: Selects 100GB plan
4. Ticket created in Zoho Desk
5. POC gets approval request
6. POC approves
7. Support team provisions storage
8. Customer notified of completion

### Scenario 3: Server Issue via SalesIQ

1. Customer: "Server is slow"
2. AceBuddy: Asks for metrics
3. Customer: Provides CPU/RAM/Disk %
4. High priority ticket created
5. Support team investigates
6. Issue resolved
7. Ticket closed
8. Customer satisfaction survey sent

---

**Version:** 1.0.0
**Last Updated:** 2025-11-26
**Status:** ✅ Production Ready
