

# 🚀 WhatsApp Bot Complete Integration Guide

## 📋 **Quick Start Summary**

✅ **Infrastructure Ready**: Database, API endpoints, models implemented and deployed  
✅ **Migration Applied**: WhatsApp users table created successfully  
✅ **ngrok Configured**: Public tunneling for local development  
✅ **Endpoints Live**: All API routes available at `/api/whatsapp/*`

---

## 🎯 **Getting Started - Local Development Setup**

### **Step 1: Start Your Backend Server**
```bash
cd /home/vil/code/pensiveverse/edutech-platform/backend
source venv/bin/activate
cd src
python main.py
```
Backend runs on `http://localhost:8000`

### **Step 2: Start ngrok Tunnel** 
```bash
cd /home/vil/code/pensiveverse/edutech-platform/backend
./ngrok http 8000
```

You'll see output like:
```
ngrok by @inconshreveable

Session Status    online
Version           3.30.0
Region            United States (us)
Forwarding        https://abc123def.ngrok.io -> http://localhost:8000
Forwarding        http://abc123def.ngrok.io -> http://localhost:8000

Web Interface     http://127.0.0.1:4040
```

### **Step 3: Update Environment Variables**
Update your `.env` file with the ngrok URL:
```bash
WHATSAPP_WEBHOOK_URL=https://abc123def.ngrok.io/api/whatsapp/webhook
```




### **Step 4: Test Your Setup**
```bash
# Health Check
curl https://abc123def.ngrok.io/health

# Webhook Verification Test
curl "https://abc123def.ngrok.io/api/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=whatsapp-verify-token-2024"
# Should return: test123

# API Documentation
# Visit: https://abc123def.ngrok.io/api/docs
```

---

## 🏗️ **WhatsApp Business API Setup**

### **Prerequisites:**
1. **Facebook Business Account** - Create at business.facebook.com
2. **WhatsApp Business Account** - Link to Facebook Business
3. **WhatsApp Business App** - Create in Facebook Developer Console
4. **Phone Number** - Verify and add to WhatsApp Business

### **Required Permissions:**
- `whatsapp_business_messaging`
- `whatsapp_business_management`

### **Environment Variables** 
Add these to your `.env` file:

```bash



---

## 📚 **API Endpoints Reference**

### **1. Webhook Verification - GET `/api/whatsapp/webhook`**

**Purpose**: Verify WhatsApp webhook endpoint during setup

**Query Parameters**:
```typescript
{
  "hub.mode": "subscribe",
  "hub.challenge": "challenge_string", 
  "hub.verify_token": "your_verify_token"
}
```

**Response**:
- **200**: Returns the challenge string (Plain text)
- **403**: Invalid verification token

**Example**:
```bash
curl "https://your-ngrok-url.ngrok.io/api/whatsapp/webhook?hub.mode=subscribe&hub.challenge=12345&hub.verify_token=whatsapp-verify-token-2024"
```

---