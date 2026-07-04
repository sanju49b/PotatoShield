# Setup AWS SES Email Sending

## 🎯 Quick Setup Guide

### Step 1: Verify Your Email in AWS SES

1. **Go to AWS SES Console**: https://console.aws.amazon.com/ses/
2. **Click "Verified identities"** (left sidebar)
3. **Click "Create identity"**
4. **Select "Email address"**
5. **Enter your email**: `sanjubandaru14@gmail.com` (or any email you want to use)
6. **Click "Create identity"**
7. **Check your email inbox** for verification email
8. **Click the verification link** in the email

### Step 2: Set Environment Variable

**Before starting backend, set:**

**Windows PowerShell:**
```powershell
$env:SES_SENDER_EMAIL="sanjubandaru14@gmail.com"  # Your verified email
$env:AWS_REGION="us-east-1"
```

**Windows CMD:**
```cmd
set SES_SENDER_EMAIL=sanjubandaru14@gmail.com
set AWS_REGION=us-east-1
```

### Step 3: Verify Setup

```bash
cd api
python check_ses_setup.py
```

Should show:
```
✅ SES_SENDER_EMAIL: sanjubandaru14@gmail.com
✅ SES client initialized
✅ sanjubandaru14@gmail.com is verified
✅ All checks passed!
```

### Step 4: Restart Backend

```powershell
cd api
$env:SES_SENDER_EMAIL="sanjubandaru14@gmail.com"
$env:USE_DYNAMODB="true"
python main.py
```

## ✅ Test

1. **Register a new user** from frontend
2. **Check backend console** - Should see:
   ```
   ✅ OTP email sent successfully to user@example.com
   ```
3. **Check email inbox** - OTP should arrive
4. **Enter OTP** - Should verify successfully

## 🐛 If Still Not Working

### Check Backend Console
Look for error messages like:
- `MessageRejected` → Email not verified
- `MailFromDomainNotVerified` → Domain not verified
- `AccountSendingPausedException` → Account in sandbox mode

### Sandbox Mode
If your AWS account is in SES sandbox mode:
- You can only send to verified emails
- Request production access in SES Console
- Or verify each recipient email

### Temporary Workaround
While setting up SES:
- OTP is printed in backend console
- OTP is included in API response if email fails
- Check browser console (F12 → Network → Response) for OTP

## 📧 Email Content

The OTP email will have:
- Subject: "Your Potato Shield OTP Code"
- Body: 6-digit OTP code
- Expires in 10 minutes

---

**After verifying email in SES and setting SES_SENDER_EMAIL, emails will be sent!** 📨

