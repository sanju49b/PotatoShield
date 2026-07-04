# Manual Testing Guide - DynamoDB Integration

## ✅ What's Running

### Backend
- **URL**: http://localhost:8000
- **Status**: Running with DynamoDB enabled
- **Health Check**: http://localhost:8000/api/health

### Frontend
- **URL**: http://localhost:3000
- **Status**: Running (if started)
- **Backend**: Connected to http://localhost:8000

## 🧪 Manual Test Steps

### 1. Open Frontend
```
http://localhost:3000
```

### 2. Register/Login
- **Register** a new user with email and password
- Or **Login** if you already have an account
- **Verify**: Backend console should show DynamoDB operations

### 3. Set Up Field
- Enter **location** (or use "GET LOCATION" button)
- Enter **sowing date**
- Click "Save Field"
- **Verify**: Check AWS DynamoDB → `potato-shield-fields` table

### 4. Test Chat
- Send a message: "Hello, where am I from?"
- **Verify**: 
  - Message appears in chat
  - Assistant responds with your location
  - Backend console shows conversation/message creation

### 5. Send More Messages
- Send 2-3 more messages
- **Verify**: All messages appear in chat
- **Verify**: Check AWS DynamoDB → `potato-shield-messages` table

## 📊 Verify in AWS DynamoDB Console

1. Go to: https://console.aws.amazon.com/dynamodb/
2. Click "Tables"
3. Check these tables have data:
   - `potato-shield-users` - Your user account
   - `potato-shield-fields` - Your field data
   - `potato-shield-conversations` - Your chat sessions
   - `potato-shield-messages` - All your messages

## 🔍 What to Look For

### Backend Console
Should show:
```
DynamoDB client initialized for region: us-east-1
✓ All DynamoDB tables initialized
User created: your@email.com
Field created: field-id
Conversation created: conv-id
Message added: msg-id
```

### AWS DynamoDB Console
- All 5 tables exist
- Tables contain your data
- You can query by email (users table)

## ✅ Success Indicators

- ✅ Can register/login
- ✅ Can set up field
- ✅ Can send messages
- ✅ Messages saved and retrieved
- ✅ Data visible in AWS DynamoDB Console
- ✅ Backend console shows DynamoDB operations

## 🐛 If Something Fails

### Backend Issues
- Check backend terminal for errors
- Verify `USE_DYNAMODB=true` is set
- Check AWS credentials

### Frontend Issues
- Check browser console (F12)
- Verify backend is running: http://localhost:8000/api/health
- Check network tab for API calls

### DynamoDB Issues
- Check AWS Console for table existence
- Verify IAM permissions
- Check AWS region matches

## 📝 Quick Commands

### Check Backend Health
```bash
curl http://localhost:8000/api/health
```

### Restart Backend with DynamoDB
```powershell
cd api
$env:USE_DYNAMODB="true"
python main.py
```

### Restart Frontend
```bash
cd frontend
npm run dev
```

---

**Happy Testing!** 🚀

If everything works, your data is being saved to DynamoDB and ready for Vercel deployment!

