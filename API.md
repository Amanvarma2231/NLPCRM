# NLPCRM API Documentation

## Overview

NLPCRM provides a RESTful API for managing contacts, integrations, and AI-powered features.

**Base URL**: `http://localhost:5000`

**Authentication**: Session-based (login required for most endpoints)

---

## Authentication

### Login
```http
POST /login
Content-Type: application/x-www-form-urlencoded

email=admin@nlpcrm.com&password=admin@2026
```

**Response**: Redirects to `/dashboard` with session cookie

### Logout
```http
GET /logout
```

**Response**: Redirects to `/login` and clears session

---

## Contacts API

### Get All Contacts
```http
GET /contacts
```

**Response**: HTML page with contacts list

### Add Contact
```http
POST /contacts/add
Content-Type: application/x-www-form-urlencoded

name=John Doe
email=john@example.com
phone=+1234567890
company=TechCorp
job_title=CEO
sentiment=Positive
importance_score=8
urgency=High
summary=Interested in enterprise plan
source=Manual Input
```

**Response**: Redirects to `/contacts`

### Delete Contact
```http
POST /contacts/delete/<email>
```

**Response**: Redirects to `/contacts`

### Batch Delete Contacts
```http
POST /contacts/batch-delete
Content-Type: application/json

{
  "emails": ["john@example.com", "jane@example.com"]
}
```

**Response**:
```json
{
  "success": true,
  "deleted": 2
}
```

### Export Contacts
```http
GET /contacts/export
```

**Response**: CSV file download

---

## AI & NLP API

### Process Text (Extract Contact Info)
```http
POST /process-text
Content-Type: application/json

{
  "text": "Hi, I'm Sarah from CloudScale. Email: sarah@cloudscale.io. We need a CRM solution urgently."
}
```

**Response**:
```json
{
  "success": true,
  "extracted": "{\"name\": \"Sarah\", \"email\": \"sarah@cloudscale.io\", \"company\": \"CloudScale\", \"urgency\": \"High\", ...}"
}
```

### AI Assistant Query
```http
POST /ai-assistant/query
Content-Type: application/json

{
  "query": "Show me all high-interest leads from TechCorp"
}
```

**Response**:
```json
{
  "success": true,
  "answer": "I found 3 high-interest leads from TechCorp...",
  "results": [...],
  "count": 3,
  "is_analysis": false
}
```

---

## Email API

### Test Email Connection
```http
POST /email/test-connection
```

**Response**:
```json
{
  "smtp": {
    "ok": true,
    "message": "SMTP connection OK (smtp.gmail.com:587)"
  },
  "pop3": {
    "ok": true,
    "message": "POP3 connection OK — 5 message(s) on server."
  }
}
```

### Send Email
```http
POST /email/send
Content-Type: application/json

{
  "to": "recipient@example.com",
  "subject": "Follow-up",
  "body": "Hi, following up on our conversation..."
}
```

**Response**:
```json
{
  "success": true,
  "message": "Email sent successfully to recipient@example.com"
}
```

### Fetch Inbox
```http
GET /email/inbox?max=10
```

**Response**:
```json
{
  "success": true,
  "count": 5,
  "messages": [
    {
      "id": "1",
      "from": "sender@example.com",
      "subject": "Meeting Request",
      "text": "Full email body...",
      "snippet": "First 200 chars...",
      "source": "Email (POP3)"
    }
  ]
}
```

---

## Sync & Integration API

### Sync All Sources
```http
POST /sync-all
```

**Description**: Syncs contacts from WhatsApp and Email

**Response**:
```json
{
  "success": true,
  "synced_count": 5,
  "email_active": true
}
```

---

## Webhook Endpoints

### WhatsApp Webhook
```http
GET /webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=nlpcrm_verify_token&hub.challenge=CHALLENGE_STRING
```

**Response**: Returns challenge string for verification

```http
POST /webhooks/whatsapp
Content-Type: application/json

{
  "entry": [
    {
      "changes": [
        {
          "value": {
            "messages": [
              {
                "text": {
                  "body": "Message content"
                }
              }
            ]
          }
        }
      ]
    }
  ]
}
```

**Response**:
```json
{
  "status": "received"
}
```

### Zoom Webhook
```http
POST /webhooks/zoom
Content-Type: application/json

{
  "transcript": "Meeting transcript content..."
}
```

**Response**:
```json
{
  "status": "received"
}
```

### Teams Webhook
```http
POST /webhooks/teams
Content-Type: application/json

{
  "message": {
    "content": "Teams message content..."
  }
}
```

**Response**:
```json
{
  "status": "received"
}
```

---

## Settings API

### Get Settings
```http
GET /settings
```

**Response**: HTML page with settings form

### Update Settings
```http
POST /settings
Content-Type: application/x-www-form-urlencoded

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your_password
...
```

**Response**: Redirects to `/settings`

---

## Dashboard & Views

### Dashboard
```http
GET /
GET /dashboard
```

**Query Parameters**:
- `source` (optional): Filter by source (e.g., `whatsapp`, `email`, `teams`)

### Source Views

#### Email Source
```http
GET /sources/email
```

#### WhatsApp Source
```http
GET /sources/whatsapp
```

#### Outlook/Teams Source
```http
GET /sources/outlook
```

### Activity Log
```http
GET /activity
```

### Pipeline View
```http
GET /pipeline
```

### AI Engine
```http
GET /ai-engine
```

### Entities View
```http
GET /entities
```

### Integrations
```http
GET /integrations
```

---

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Bad Request",
  "details": "Error description"
}
```

### 401 Unauthorized
```json
{
  "status": "error",
  "message": "Unauthorized Access"
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Internal Server Error"
}
```

---

## Rate Limiting

Currently, basic rate limiting is implemented via Flask-Limiter. Future versions will include more granular controls.

---

## Data Models

### Contact Object
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "company": "TechCorp",
  "job_title": "CEO",
  "source": "Email",
  "interest": "High",
  "sentiment": "Positive",
  "importance_score": 8.5,
  "urgency": "High",
  "summary": "Interested in enterprise plan",
  "created_at": "2026-01-15T10:30:00",
  "email2": "[{\"label\": \"Work\", \"value\": \"john.work@example.com\"}]",
  "social_media": "[{\"label\": \"LinkedIn\", \"value\": \"linkedin.com/in/johndoe\"}]"
}
```

### Message Object
```json
{
  "id": "1",
  "from": "sender@example.com",
  "subject": "Meeting Request",
  "text": "Full message body",
  "snippet": "First 200 characters",
  "source": "Email (POP3)"
}
```

---

## Best Practices

1. **Always use HTTPS in production**
2. **Include CSRF token for POST requests** (except webhooks)
3. **Handle rate limiting gracefully**
4. **Validate all inputs**
5. **Use proper error handling**

---

## Support

For API support, contact:
- **Email**: amangurauli@gmail.com
- **GitHub**: [@Amanvarma2231](https://github.com/Amanvarma2231)

---

**Version**: 3.1.0  
**Last Updated**: January 2026
