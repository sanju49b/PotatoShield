# Troubleshooting: User Not Appearing in DynamoDB

## 🔍 Quick Checks

### 1. Check Backend is Using DynamoDB
Look at your backend console - you should see:
```
DynamoDB client initialized for region: us-east-1
✓ All DynamoDB tables initialized
```

If you see SQLite messages instead, DynamoDB is NOT enabled!

### 2. Check Registration in Backend Console
When you register from frontend, backend console should show:
```
User created: your@email.com
```

If you don't see this, the registration might have failed.

### 3. Check for Errors
Look for error messages in:
- **Backend console** (terminal running `python main.py`)
- **Browser console** (F12 → Console tab)
- **Network tab** (F12 → Network tab → Check API response)

## 🧪 Debug Steps

### Step 1: Verify Backend is Using DynamoDB

**Check backend terminal:**
```powershell
# Should see:
DynamoDB client initialized for region: us-east-1
```

**If you see SQLite messages:**
```powershell
# Restart backend with DynamoDB:
cd api
$env:USE_DYNAMODB="true"
python main.py
```

### Step 2: Test Registration Directly

**Run the debug script:**
```bash
cd api
python debug_registration.py test@example.com password123
```

This will:
- ✅ Test direct registration
- ✅ Test API registration
- ✅ Verify user appears in DynamoDB

### Step 3: Check API Response

**In browser (F12 → Network tab):**
1. Register a user from frontend
2. Look for `POST /api/auth/register` request
3. Check the response:
   - Status should be `200`
   - Response should have `"success": true`
   - Should include `user_id` and `email`

### Step 4: Check Backend Logs

**When registering, backend console should show:**
```
INFO: POST /api/auth/register
User created: your@email.com
```

**If you see errors:**
- Check the error message
- Verify AWS credentials
- Check DynamoDB permissions

## 🔧 Common Issues

### Issue 1: Backend Not Using DynamoDB
**Symptom**: Backend console shows SQLite messages

**Fix:**
```powershell
cd api
$env:USE_DYNAMODB="true"
python main.py
```

### Issue 2: Registration Fails Silently
**Symptom**: No error, but user not in DynamoDB

**Check:**
1. Browser console (F12) for errors
2. Network tab for API response
3. Backend console for errors

**Fix:** Run debug script to see what's happening:
```bash
python debug_registration.py your@email.com yourpassword
```

### Issue 3: Wrong AWS Region
**Symptom**: Tables exist but user not appearing

**Check:**
- AWS Console region matches `AWS_REGION` env var
- Backend shows correct region: `DynamoDB client initialized for region: us-east-1`

### Issue 4: Duplicate Email
**Symptom**: Registration says "Email already exists"

**This is normal!** The user already exists. Check DynamoDB with:
```bash
cd api
python check_user_in_dynamodb.py your@email.com
```

## 📊 Verify User in DynamoDB

### Method 1: AWS Console
1. Go to DynamoDB Console
2. Click `potato-shield-users` table
3. Click "Explore table items"
4. Look for your email (primary key)

### Method 2: Command Line
```bash
cd api
python check_user_in_dynamodb.py your@email.com
```

### Method 3: List All Users
```bash
cd api
python check_user_in_dynamodb.py
```

## 🎯 Quick Test

1. **Stop backend** (Ctrl+C)
2. **Restart with DynamoDB:**
   ```powershell
   cd api
   $env:USE_DYNAMODB="true"
   python main.py
   ```
3. **Register from frontend**
4. **Check backend console** - Should see "User created: ..."
5. **Refresh DynamoDB console** - User should appear

## 📝 What to Check

- [ ] Backend console shows "DynamoDB client initialized"
- [ ] Backend console shows "User created: ..." when registering
- [ ] No errors in backend console
- [ ] No errors in browser console (F12)
- [ ] API response shows `"success": true`
- [ ] AWS region matches in backend and console
- [ ] DynamoDB tables exist in AWS Console

## 🆘 Still Not Working?

Run the debug script and share the output:
```bash
cd api
python debug_registration.py your@email.com yourpassword
```

This will show exactly what's happening!

