# 🚀 WhatsApp Bot Developer Instructions

## 🎯 **Project Overview**

You are implementing a WhatsApp bot for the **YeeBitz Platform** that mirrors the existing Telegram bot functionality. The backend infrastructure is **100% complete** - you only need to connect it to WhatsApp's API.

**✅ Already Implemented:**
- Database models and migrations
- All API endpoints with full business logic
- Bot command processing (start, link, status, unlink)
- Account linking system with secure tokens
- Authentication and security
- Error handling and logging

---

## 🔗 **Live Endpoints (Ready to Use)**

**Base URL**: `https://statelier-darlene-unmissed.ngrok-free.dev`

**Webhook Configuration:**
- **URL**: `https://statelier-darlene-unmissed.ngrok-free.dev/api/whatsapp/webhook`
- **Verify Token**: `whatsapp-verify-token-2024`

**Test Endpoints:**
- **Health Check**: https://statelier-darlene-unmissed.ngrok-free.dev/health
- **API Docs**: https://statelier-darlene-unmissed.ngrok-free.dev/api/docs
- **Webhook Test**: https://statelier-darlene-unmissed.ngrok-free.dev/api/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=whatsapp-verify-token-2024

---

## 🎯 **What You Need to Do (2-3 Hours Total)**

### **Phase 1: WhatsApp Business API Setup**

1. **Set up WhatsApp Business API:**
   - Create Facebook Business Account
   - Set up WhatsApp Business Account
   - Create WhatsApp Business App
   - Get access token and phone number ID

2. **Configure Webhook:**
   - **Webhook URL**: `https://statelier-darlene-unmissed.ngrok-free.dev/api/whatsapp/webhook`
   - **Verify Token**: `whatsapp-verify-token-2024`
   - **Webhook Fields**: Select `messages`

### **Phase 2: Send the Credentials to update .env**

Update these values in the backend `.env` file:

```bash
# Replace these with your actual WhatsApp API credentials:
WHATSAPP_ACCESS_TOKEN=your_actual_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_actual_phone_number_id_here
WHATSAPP_BUSINESS_ACCOUNT_ID=your_actual_business_account_id_here

# These are already configured:
WHATSAPP_WEBHOOK_URL=https://statelier-darlene-unmissed.ngrok-free.dev/api/whatsapp/webhook
WHATSAPP_WEBHOOK_SECRET=whatsapp-webhook-secret-2024
WHATSAPP_VERIFY_TOKEN=whatsapp-verify-token-2024
WHATSAPP_API_VERSION=v18.0
WHATSAPP_API_URL=https://graph.facebook.com
```

### **Phase 3: Implement Message Sending**

**Replace the placeholder function** in `/backend/src/api/whatsapp.py` at line 132:

```python
import httpx
from core.config import settings
from loguru import logger

async def send_whatsapp_message(phone_number: str, message: str):
    """Send WhatsApp message via Meta API"""
    
    url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        
    if response.status_code == 200:
        logger.info(f"WhatsApp message sent to {phone_number}")
        return response.json()
    else:
        logger.error(f"Failed to send WhatsApp message: {response.text}")
        raise Exception(f"WhatsApp API error: {response.status_code}")
```


### **Phase 4: Testing **

1. **Test webhook verification** (should already work)
2. **Send test messages to your bot:**
   - Send "start" → Should get welcome message
   - Send "link" → Should get account linking instructions
   - Complete linking via web interface
   - Send "status" → Should show linked account info
   - Send "unlink" → Should disconnect account

---

## 🤖 **Bot Commands (Already Implemented)**

| Command | What It Does | Response |
|---------|--------------|----------|
| `start`, `hi`, `hello` | Welcome message | Platform introduction + available commands |
| `link` | Generate linking token | Secure link + token for account linking |
| `status` | Check account status | Shows linked account details or "not linked" |
| `unlink` | Disconnect account | Removes connection between WhatsApp and platform |

**Example Bot Responses:**

**Welcome Message:**
```
🎓 Welcome to YeetBitz Platform!

I can help you take tests and access your study materials.

Available commands:
• Send 'link' - Link your account
• Send 'status' - Check linking status
• Send 'unlink' - Unlink your account

To get started, please link your YeeBitz account by sending 'link'
```

**Link Command:**
```
🔗 Account Linking

To link your YeeBitz account, open this link in your browser:

👉 https://statelier-darlene-unmissed.ngrok-free.dev/whatsapp/link?token=abc123xyz789

Or go to the settings page and paste this token:
abc123xyz789

⏰ This link expires in 1 hour.
🔒 For security, don't share this with others.
```

---

## 📚 **API Endpoints Reference**

### **Webhook Verification - GET `/api/whatsapp/webhook`**
- **Purpose**: WhatsApp webhook verification
- **Already working**: ✅ Test at the URL above

### **Webhook Handler - POST `/api/whatsapp/webhook`**  
- **Purpose**: Process incoming messages
- **Already implemented**: ✅ All command logic ready

### **Account Linking Endpoints**
- `GET /api/whatsapp/link?token=xyz` - Link page ✅
- `POST /api/whatsapp/link` - Complete linking ✅
- `DELETE /api/whatsapp/unlink` - Unlink account ✅
- `GET /api/whatsapp/status` - Check link status ✅

### **Admin Endpoint**
- `POST /api/whatsapp/send` - Send messages (admin/instructor only) ✅

---

## 🧪 **How to Test Your Implementation**

### **1. Test Webhook Setup**
```bash
curl "https://statelier-darlene-unmissed.ngrok-free.dev/api/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=whatsapp-verify-token-2024"
# Should return: test123
```

### **2. Test Message Processing**
Send this JSON to your webhook:
```json
{
  "object": "whatsapp_business_account", 
  "entry": [{
    "id": "business_account_id",
    "changes": [{
      "field": "messages",
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {"phone_number_id": "123"},
        "messages": [{
          "from": "+1234567890",
          "id": "msg_123", 
          "timestamp": "1699564800",
          "text": {"body": "start"},
          "type": "text"
        }]
      }
    }]
  }]
}
```

### **3. Manual Testing Flow**
1. Send "start" to your WhatsApp bot
2. Send "link" → Get linking URL
3. Open link and complete account linking
4. Send "status" → Should show linked account
5. Send "unlink" → Should disconnect account

---

## 🛡️ **Security (Optional Enhancement)**

Add webhook signature verification:

```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    received_signature = signature.replace('sha256=', '')
    return hmac.compare_digest(expected_signature, received_signature)
```

---

## 🚨 **Common Issues & Solutions**

### **Webhook Not Working**
- ✅ Check webhook URL is HTTPS (ngrok provides this)
- ✅ Verify webhook fields include "messages"
- ✅ Ensure verify token matches exactly

### **Messages Not Sending**
- ✅ Verify access token is valid and not expired
- ✅ Check phone number ID is correct
- ✅ Ensure recipient has WhatsApp

### **Bot Not Responding**
- ✅ Check backend logs for errors
- ✅ Verify webhook payload format
- ✅ Test endpoints manually first

---

## 📞 **Support & Debugging**

**Health Checks:**
- **API Health**: https://statelier-darlene-unmissed.ngrok-free.dev/health
- **Detailed Health**: https://statelier-darlene-unmissed.ngrok-free.dev/health/detailed

**API Documentation:**
- **Interactive Docs**: https://statelier-darlene-unmissed.ngrok-free.dev/api/docs

**Database Check:**
```sql
-- Check WhatsApp users
SELECT * FROM whatsapp_users;

-- Check linked accounts  
SELECT u.email, w.whatsapp_phone, w.is_linked 
FROM users u 
JOIN whatsapp_users w ON u.id = w.user_id 
WHERE w.is_linked = true;
```

---

## 🎯 **Deliverables**

When you're done, provide:

1. ✅ **WhatsApp Business API** configured with webhook
2. ✅ **Message sending function** working
3. ✅ **All bot commands** responding correctly
4. ✅ **Account linking flow** tested end-to-end
5. ✅ **Brief documentation** of any additional setup steps

---

## ⏱️ **Timeline**

- **WhatsApp API Setup**: 30 minutes
- **Add credentials**: 5 minutes  
- **Implement message sending**: 1 hour
- **Testing & debugging**: 30 minutes

**Total: 2-3 hours**

---

## 🎉 **You're Almost Done!**

The heavy lifting is complete. You just need to:
1. Connect to WhatsApp's API
2. Replace one function 
3. Test the commands

The entire backend infrastructure, database, authentication, and business logic are already built and working! 🚀

**Questions? Check the API docs or test the endpoints directly.**