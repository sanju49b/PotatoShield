# Verify Email in AWS SES - Step by Step

## 📧 Verify `sanjubandaru14@gmail.com` in AWS SES

### Step 1: Go to AWS SES Console
1. Open: https://console.aws.amazon.com/ses/
2. Make sure you're in the correct region: **us-east-1** (top right)

### Step 2: Create Email Identity
1. Click **"Verified identities"** in the left sidebar
2. Click **"Create identity"** button (top right)
3. Select **"Email address"** (not domain)
4. Enter email: `sanjubandaru14@gmail.com`
5. Click **"Create identity"**

### Step 3: Verify Email
1. Check your email inbox: `sanjubandaru14@gmail.com`
2. Look for email from: **AWS Email Verification**
3. Subject: **"AWS Email Verification Request"**
4. **Click the verification link** in the email
5. You'll be redirected to AWS confirming verification

### Step 4: Confirm Verification
1. Go back to AWS SES Console
2. Click "Verified identities"
3. You should see: `sanjubandaru14@gmail.com` with status **"Verified"** ✅

### Step 5: Set Environment Variable & Restart Backend

**Windows PowerShell:**
```powershell
cd C:\Users\satya\Desktop\Potato-Shield\api
$env:SES_SENDER_EMAIL="sanjubandaru14@gmail.com"
$env:USE_DYNAMODB="true"
python main.py
```

### Step 6: Verify Setup Again
```bash
cd api
python check_ses_setup.py
```

Should now show:
```
✅ SES_SENDER_EMAIL: sanjubandaru14@gmail.com
✅ SES client initialized
✅ sanjubandaru14@gmail.com is verified  ← Should be ✅ now!
✅ All checks passed!
```

## ✅ Test Email Sending

After verification:
1. Register a new user from frontend
2. Check backend console - Should see: `✅ OTP email sent successfully`
3. Check email inbox - OTP should arrive
4. Enter OTP - Should work!

## 🐛 If Email Not Received

### Check Spam Folder
- Sometimes AWS emails go to spam
- Mark as "Not Spam" if found

### Check Email Settings
- Make sure you can receive emails at that address
- Check if email filters are blocking AWS emails

### Sandbox Mode
If your AWS account is in sandbox mode:
- You can only send to **verified emails**
- You can verify recipient emails too
- Or request production access in SES Console

## 📝 Quick Checklist

- [ ] Email verified in AWS SES Console
- [ ] SES_SENDER_EMAIL environment variable set
- [ ] Backend restarted with environment variable
- [ ] `check_ses_setup.py` shows ✅ for all checks
- [ ] Test registration sends email successfully

---

**Once verified, emails will be sent automatically!** 📧✅

