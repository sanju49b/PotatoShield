# Fix: AWS SES Sandbox Mode - Email Not Verified

## 🔍 Problem

You're seeing this error:
```
AWS SES Error (MessageRejected): Email address is not verified. 
The following identities failed the check in region US-EAST-1: saidivyasreesandu@gmail.com
```

This means AWS SES is in **Sandbox Mode** - you can only send emails **TO verified email addresses**.

## ✅ Solutions

### Option 1: Verify Recipient Email (Quick Fix for Testing)

1. **Go to AWS SES Console**: https://console.aws.amazon.com/ses/
2. **Click "Verified identities"**
3. **Click "Create identity"**
4. **Select "Email address"**
5. **Enter**: `saidivyasreesandu@gmail.com` (the recipient email)
6. **Click "Create identity"**
7. **Check email inbox** and click verification link

Now you can send OTPs to this email!

### Option 2: Request Production Access (Best for Production)

This allows sending to ANY email address:

1. **Go to AWS SES Console**: https://console.aws.amazon.com/ses/
2. **Click "Account dashboard"** (left sidebar)
3. **Scroll to "Sending limits"**
4. **Click "Request production access"**
5. **Fill out the form**:
   - Use case: "User authentication OTP emails"
   - Website URL: Your app URL
   - Description: "Sending OTP codes for email verification in user authentication flow"
6. **Submit request**
7. **Wait for approval** (usually 24-48 hours)

### Option 3: Verify Both Sender and Recipient (Quick Testing)

For testing, verify both:
- ✅ Sender: `sanjubandaru14@gmail.com` (already need this)
- ✅ Recipient: `saidivyasreesandu@gmail.com` (for testing)

## 🔧 Current Setup

Make sure you have:

1. **Sender email verified**: `sanjubandaru14@gmail.com`
2. **Environment variable set**: `SES_SENDER_EMAIL=sanjubandaru14@gmail.com`
3. **Recipient email verified** (if in sandbox mode): Any email you want to send to

## 🧪 Quick Test

After verifying recipient email:

1. **Restart backend** (if needed)
2. **Register with** `saidivyasreesandu@gmail.com`
3. **Check backend console** - Should see: `✅ OTP email sent successfully`
4. **Check email inbox** - OTP should arrive!

## 📝 Sandbox Mode Rules

In AWS SES Sandbox Mode:
- ✅ Can send **FROM** verified sender email
- ✅ Can send **TO** verified recipient emails
- ❌ Cannot send to unverified emails
- ✅ Can verify up to 10,000 email addresses

After production access:
- ✅ Can send to **ANY** email address
- ✅ No need to verify recipients

## 🎯 Recommended Action

For **development/testing**:
- Verify the recipient email you're testing with
- Or verify multiple test emails

For **production**:
- Request production access
- This allows sending to any email

---

**Verify the recipient email in SES Console to start receiving OTPs!** 📧✅

