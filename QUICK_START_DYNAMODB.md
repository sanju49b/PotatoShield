# Quick Start: Frontend + DynamoDB Integration

## ✅ Everything is Already Integrated!

The frontend is **fully integrated** with DynamoDB. Just start the backend with DynamoDB enabled!

## 🚀 Quick Start (3 Steps)

### Step 1: Start Backend with DynamoDB

**Windows:**
```powershell
cd api
$env:USE_DYNAMODB="true"
python main.py
```

**Or use the helper script:**
```cmd
cd api
start_with_dynamodb.bat
```

### Step 2: Start Frontend

```bash
cd frontend
npm run dev
```

### Step 3: Test It!

1. Open: http://localhost:3000
2. Register a new user
3. Set up a field (location + sowing date)
4. Start chatting
5. **Check AWS DynamoDB Console** - All your data is there! 🎉

## 📊 What Gets Saved to DynamoDB

When you use the frontend, these operations automatically save to DynamoDB:

| Action | DynamoDB Table |
|--------|---------------|
| Register/Login | `potato-shield-users` |
| Set up field | `potato-shield-fields` |
| Create chat | `potato-shield-conversations` |
| Send message | `potato-shield-messages` |
| OTP verification | `potato-shield-otp` |

## 🔍 Verify It's Working

### Check Backend Console
You should see:
```
DynamoDB client initialized for region: us-east-1
✓ Table potato-shield-users exists
✓ Table potato-shield-conversations exists
...
```

### Check AWS Console
1. Go to [AWS DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
2. Click "Tables"
3. You should see all 5 tables
4. Click on a table → "Explore table items" to see your data!

## 🧪 Test End-to-End

### Test 1: User Registration
1. Open frontend → Register
2. Check `potato-shield-users` table in AWS Console
3. ✅ Your user should be there!

### Test 2: Field Creation
1. After login → Set up field
2. Check `potato-shield-fields` table
3. ✅ Your field should be there!

### Test 3: Chat Messages
1. Send a message in chat
2. Check `potato-shield-messages` table
3. ✅ Your message should be there!

## 📝 API Flow

```
Frontend (React/Next.js)
    ↓ HTTP Requests
Backend API (FastAPI)
    ↓ USE_DYNAMODB=true
DynamoDB Service
    ↓
AWS DynamoDB Tables
```

## 🔧 Troubleshooting

### "Cannot connect to backend"
- Make sure backend is running on port 8000
- Check: `http://localhost:8000/api/health`

### "Unauthorized" errors
- Make sure you're logged in
- Check `auth_token` in localStorage

### Data not appearing in DynamoDB
- Verify `USE_DYNAMODB=true` is set
- Check AWS credentials
- Check backend console for errors

### Tables not created
- Tables are created automatically on first use
- Check AWS IAM permissions
- Verify AWS region matches

## 🎯 Summary

✅ **Frontend**: No changes needed - already integrated!  
✅ **Backend**: Set `USE_DYNAMODB=true` to enable DynamoDB  
✅ **All Data**: Automatically saves to DynamoDB  
✅ **Ready for Production**: Works perfectly for Vercel deployment  

**That's it!** Just start the backend with DynamoDB enabled and everything works! 🚀

