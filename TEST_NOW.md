# Testing DynamoDB Integration - Live Test

## ✅ Backend Started with DynamoDB
- Running on: http://localhost:8000
- DynamoDB enabled: ✓
- Check health: http://localhost:8000/api/health

## ✅ Frontend Started
- Running on: http://localhost:3000
- Connected to backend: http://localhost:8000

## 🧪 Test Steps

### 1. Open Frontend
- Go to: http://localhost:3000
- You should see the login page

### 2. Register a New User
- Enter email and password
- Click "Register"
- **Check**: Backend console should show DynamoDB operations
- **Verify**: Check AWS DynamoDB Console → `potato-shield-users` table

### 3. Set Up Field (if redirected)
- Enter location (or use "GET LOCATION" button)
- Enter sowing date
- Click "Save Field"
- **Check**: Backend console should show field creation
- **Verify**: Check AWS DynamoDB Console → `potato-shield-fields` table

### 4. Start Chatting
- Type a message
- Send it
- **Check**: Backend console should show:
  - Conversation creation in `potato-shield-conversations`
  - Message saved in `potato-shield-messages`
- **Verify**: Check AWS DynamoDB Console → both tables

### 5. Check Conversation History
- Messages should appear in chat
- **Verify**: Check `potato-shield-messages` table in AWS Console

## 📊 What to Verify in AWS Console

1. Go to: https://console.aws.amazon.com/dynamodb/
2. Click "Tables" in left sidebar
3. You should see these tables:
   - `potato-shield-users` - Your user account
   - `potato-shield-conversations` - Chat sessions
   - `potato-shield-messages` - All messages
   - `potato-shield-fields` - Your fields
   - `potato-shield-otp` - OTP codes (if using OTP)

4. Click on any table → "Explore table items"
5. You should see your data!

## 🔍 Check Backend Console

You should see logs like:
```
DynamoDB client initialized for region: us-east-1
✓ Table potato-shield-users exists
User created: test@example.com
Field created: field-id-123
Conversation created: conv-id-456
Message added: msg-id-789
```

## 🐛 If Something Doesn't Work

### Backend not starting?
- Check AWS credentials are set
- Check `USE_DYNAMODB=true` is set
- Check port 8000 is not in use

### Frontend can't connect?
- Check backend is running: http://localhost:8000/api/health
- Check CORS settings
- Check browser console for errors

### Data not saving?
- Check backend console for errors
- Verify AWS credentials
- Check DynamoDB tables exist in AWS Console

## ✅ Success Indicators

- ✅ Backend console shows "DynamoDB client initialized"
- ✅ You can register/login
- ✅ You can set up fields
- ✅ You can send messages
- ✅ Data appears in AWS DynamoDB Console

**Everything is working!** 🎉

