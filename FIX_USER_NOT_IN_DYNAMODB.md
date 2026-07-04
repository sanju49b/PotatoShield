# Fix: User Not Appearing in DynamoDB

## 🔍 Most Likely Issue

The backend is **NOT using DynamoDB** - it's probably using SQLite instead!

## ✅ Quick Fix

### Step 1: Stop Backend
Press `Ctrl+C` in the terminal where backend is running

### Step 2: Restart with DynamoDB Enabled

**Windows PowerShell:**
```powershell
cd api
$env:USE_DYNAMODB="true"
$env:AWS_REGION="us-east-1"
python main.py
```

**Windows CMD:**
```cmd
cd api
set USE_DYNAMODB=true
set AWS_REGION=us-east-1
python main.py
```

### Step 3: Verify Backend is Using DynamoDB

Look at backend console - you should see:
```
DynamoDB client initialized for region: us-east-1
✓ Table potato-shield-users exists
✓ Table potato-shield-conversations exists
...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**If you see SQLite messages instead**, DynamoDB is NOT enabled!

### Step 4: Register User Again

1. Go to frontend: http://localhost:3000
2. Register a new user
3. **Check backend console** - Should see:
   ```
   User created: your@email.com
   ```
4. **Refresh DynamoDB Console** - User should appear!

## 🧪 Test Registration

Run this to test if registration works with DynamoDB:

```bash
cd api
python debug_registration.py your@email.com yourpassword
```

This will:
- ✅ Test direct registration
- ✅ Test API registration  
- ✅ Verify user appears in DynamoDB

## 📊 Verify in DynamoDB

After registering with DynamoDB enabled:

1. Go to AWS DynamoDB Console
2. Click `potato-shield-users` table
3. Click "Explore table items"
4. Click "Run" button (to refresh)
5. Your new user should appear!

## 🔍 Check Backend Console

When you register, backend console should show:
```
INFO:     POST /api/auth/register
User created: your@email.com
```

If you see errors or SQLite messages, DynamoDB is not enabled!

## ✅ Success Indicators

- [ ] Backend console shows "DynamoDB client initialized"
- [ ] Backend console shows "User created: ..." when registering
- [ ] No SQLite messages in backend console
- [ ] User appears in DynamoDB Console after registration
- [ ] Can query user by email in DynamoDB

## 🎯 Quick Test

```bash
# 1. Check current users
cd api
python check_user_in_dynamodb.py

# 2. Test registration
python debug_registration.py test@example.com password123

# 3. Check again
python check_user_in_dynamodb.py
```

If the user appears after step 2, DynamoDB is working!

