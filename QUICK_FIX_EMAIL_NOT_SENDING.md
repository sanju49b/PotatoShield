# Quick Fix: Email Not Sending

## 🔍 Problem

You're seeing: `Warning: Email may not have been sent to sanjubandaru14@gmail.com, but OTP is stored`

This means:
- ✅ OTP is generated and stored
- ❌ Email is NOT being sent via AWS SES

## ✅ Quick Fix

### Step 1: Set SES_SENDER_EMAIL

**Windows PowerShell:**
```powershell
$env:SES_SENDER_EMAIL="your-verified-email@example.com"
```

**Windows CMD:**
```cmd
set SES_SENDER_EMAIL=your-verified-email@example.com
```

**Important**: The email must be verified in AWS SES first!

### Step 2: Verify Email in AWS SES

1. Go to: https://console.aws.amazon.com/ses/
2. Click "Verified identities" in left sidebar
3. Click "Create identity"
4. Select "Email address"
5. Enter your email (e.g., `noreply@yourdomain.com` or your personal email)
6. Click "Create identity"
7. **Check your email inbox** for verification link
8. **Click the verification link**

### Step 3: Restart Backend

After setting the environment variable:

```powershell
# Stop current backend (Ctrl+C)
# Then restart:
cd api
$env:SES_SENDER_EMAIL="your-verified-email@example.com"
$env:USE_DYNAMODB="true"
python main.py
```

### Step 4: Check SES Setup

Run this to verify everything:
```bash
cd api
python check_ses_setup.py
```

You should see:
```
✅ SES_SENDER_EMAIL: your-email@example.com
✅ SES client initialized
✅ your-email@example.com is verified
✅ All checks passed!
```

## 🧪 Temporary Workaround (For Testing)

While setting up SES, the OTP is shown in:
1. **Backend console** - Check the terminal running `python main.py`
2. **API response** - Check browser console (F12 → Network → Response)

The OTP will be printed like:
```
⚠️  OTP email failed, but OTP stored. Code: 123456
```

## 📝 Example Setup

```powershell
# 1. Verify email in AWS SES Console first
# 2. Then set environment variable:
$env:SES_SENDER_EMAIL="sanjubandaru14@gmail.com"  # Use your verified email
$env:AWS_REGION="us-east-1"

# 3. Restart backend
python main.py
```

## ✅ Success Indicators

After fixing:
- Backend console shows: `✅ OTP email sent successfully to sanjubandaru14@gmail.com`
- You receive email in inbox (check spam too)
- No more warnings about email not being sent

## 🐛 Common Issues

### "SES_SENDER_EMAIL not set"
**Fix**: Set the environment variable before starting backend

### "MessageRejected" or "Email address not verified"
**Fix**: Verify the sender email in AWS SES Console

### "AccountSendingPausedException"
**Fix**: Your AWS account might be in sandbox mode. Check SES console.

### Email goes to spam
**Fix**: 
- Check spam folder
- Mark as "Not Spam"
- Future emails should go to inbox

---

**Once SES is configured, emails will be sent automatically!** 📧

