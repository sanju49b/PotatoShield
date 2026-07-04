# Frontend-DynamoDB Integration Guide

## ✅ Status: Already Integrated!

The frontend is **already fully integrated** with DynamoDB! Here's how it works:

### How It Works

1. **Frontend** → Makes API calls to backend (via `frontend/lib/api.ts`)
2. **Backend** → Automatically uses DynamoDB when `USE_DYNAMODB=true` is set
3. **All data** → Stored in DynamoDB (users, conversations, messages, fields, OTP)

### No Frontend Changes Needed! 🎉

The frontend doesn't need any changes because:
- ✅ All API calls go through `frontend/lib/api.ts`
- ✅ Backend automatically switches between SQLite/DynamoDB
- ✅ Same API endpoints work for both backends
- ✅ Frontend just makes HTTP requests - backend handles the storage

## How to Run with DynamoDB

### Step 1: Start Backend with DynamoDB

**Windows:**
```powershell
cd api
.\start_with_dynamodb.bat
```

**Or manually:**
```powershell
cd api
$env:USE_DYNAMODB="true"
$env:AWS_REGION="us-east-1"
python main.py
```

**Linux/Mac:**
```bash
cd api
chmod +x start_with_dynamodb.sh
./start_with_dynamodb.sh
```

**Or manually:**
```bash
cd api
export USE_DYNAMODB=true
export AWS_REGION=us-east-1
python main.py
```

### Step 2: Start Frontend

```bash
cd frontend
npm run dev
```

### Step 3: Test the Integration

1. **Open browser**: http://localhost:3000
2. **Register/Login**: Create a new account or login
3. **Set up field**: Enter location and sowing date
4. **Start chatting**: Send messages and see them saved to DynamoDB

## Verify Data in DynamoDB

### Check AWS Console

1. Go to [AWS DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
2. Click "Tables" → You should see:
   - `potato-shield-users` - Your user account
   - `potato-shield-conversations` - Your chat sessions
   - `potato-shield-messages` - All your messages
   - `potato-shield-fields` - Your field data
   - `potato-shield-otp` - OTP codes (if using OTP auth)

### What Gets Saved to DynamoDB

✅ **User Registration/Login** → `potato-shield-users` table
✅ **Field Setup** → `potato-shield-fields` table  
✅ **Chat Conversations** → `potato-shield-conversations` table
✅ **Chat Messages** → `potato-shield-messages` table
✅ **OTP Codes** → `potato-shield-otp` table

## API Endpoints (All Save to DynamoDB)

### Authentication
- `POST /api/auth/register` → Saves user to DynamoDB
- `POST /api/auth/login` → Reads user from DynamoDB
- `POST /api/auth/send-otp` → Saves OTP to DynamoDB
- `POST /api/auth/verify-otp` → Verifies OTP from DynamoDB

### Fields
- `POST /api/fields` → Saves field to DynamoDB
- `GET /api/memory/long-term` → Reads fields from DynamoDB

### Conversations
- `POST /api/conversations` → Creates conversation in DynamoDB
- `GET /api/conversations` → Lists conversations from DynamoDB
- `GET /api/conversations/{id}/messages` → Reads messages from DynamoDB
- `POST /api/conversations/{id}/messages` → Saves message to DynamoDB

## Frontend API Client

The frontend uses `frontend/lib/api.ts` which includes:

```typescript
// Authentication
authAPI.register()      // → Saves to DynamoDB
authAPI.login()         // → Reads from DynamoDB
authAPI.sendOTP()       // → Saves OTP to DynamoDB
authAPI.verifyOTP()     // → Verifies from DynamoDB

// Fields
fieldAPI.create()       // → Saves to DynamoDB

// Conversations
conversationAPI.create()        // → Creates in DynamoDB
conversationAPI.getAll()        // → Reads from DynamoDB
conversationAPI.getMessages()  // → Reads from DynamoDB
conversationAPI.addMessage()   // → Saves to DynamoDB
```

## Testing End-to-End

### 1. Test User Registration
```bash
# Frontend will automatically call:
POST http://localhost:8000/api/auth/register
# This saves to: potato-shield-users table
```

### 2. Test Field Creation
```bash
# Frontend will automatically call:
POST http://localhost:8000/api/fields
# This saves to: potato-shield-fields table
```

### 3. Test Chat
```bash
# Frontend will automatically call:
POST http://localhost:8000/api/conversations
POST http://localhost:8000/api/conversations/{id}/messages
# These save to: potato-shield-conversations and potato-shield-messages tables
```

## Environment Variables

### Backend (api/)
```
USE_DYNAMODB=true          # Enable DynamoDB
AWS_REGION=us-east-1       # AWS region
AWS_ACCESS_KEY_ID=xxx      # AWS credentials
AWS_SECRET_ACCESS_KEY=xxx  # AWS credentials
SES_SENDER_EMAIL=xxx       # For OTP emails
```

### Frontend (frontend/)
```
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend URL
```

## Troubleshooting

### Frontend can't connect to backend?
- Check backend is running: `http://localhost:8000/api/health`
- Check `NEXT_PUBLIC_API_URL` in frontend
- Check CORS settings in backend

### Data not saving to DynamoDB?
- Verify `USE_DYNAMODB=true` is set
- Check AWS credentials are correct
- Check backend logs for errors
- Verify tables exist in AWS Console

### Authentication errors?
- Check DynamoDB tables exist
- Verify user has password_hash (not OTP-only)
- Check server logs

## Summary

✅ **Frontend**: No changes needed - already integrated!
✅ **Backend**: Automatically uses DynamoDB when `USE_DYNAMODB=true`
✅ **All Operations**: Save to DynamoDB (users, fields, conversations, messages)
✅ **Ready to Deploy**: Works perfectly for Vercel deployment

Just start the backend with `USE_DYNAMODB=true` and everything will save to DynamoDB! 🚀

