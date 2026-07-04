# Request AWS SES Production Access

## 🎯 Why You Need Production Access

**Current Problem**: AWS SES is in **Sandbox Mode**
- ❌ Can only send to **verified emails**
- ❌ New users can't register (their emails aren't verified)
- ✅ Only works for testing

**After Production Access**:
- ✅ Can send to **ANY email address**
- ✅ New users can register normally
- ✅ Production-ready

## 📝 Step-by-Step: Request Production Access

### Step 1: Go to AWS SES Console
1. Open: https://console.aws.amazon.com/ses/
2. Make sure you're in the correct region: **us-east-1**

### Step 2: Open Account Dashboard
1. Click **"Account dashboard"** in the left sidebar
2. Scroll down to **"Sending limits"** section

### Step 3: Request Production Access
1. Click **"Request production access"** button
2. Fill out the form:

**Mail Type**: 
- Select: **Transactional**

**Website URL**: 
- Enter: Your app URL (e.g., `https://potato-shield.vercel.app` or `http://localhost:3000` for testing)

**Use Case Description**:
```
User authentication OTP emails for Potato Shield application. 
We need to send one-time password (OTP) codes to users for email verification during registration and login.
```

**Additional Details** (optional):
```
- Sending OTP codes for email verification
- Users register with email and receive OTP via email
- OTP expires in 10 minutes
- Average volume: Low to medium (estimated < 1000 emails/day)
- Compliance: We follow email best practices and include unsubscribe options
```

**Expected sending volume**:
- Select: **Low** (or appropriate for your use case)

**Acknowledge**:
- ✅ Check: "I understand that I will be able to send emails to any email address after my request is approved"

3. Click **"Submit"**

### Step 4: Wait for Approval
- Approval usually takes **24-48 hours**
- You'll receive an email when approved
- Check AWS Console for status

### Step 5: After Approval
1. Go back to SES Console → Account dashboard
2. You should see: **"Production access: Enabled"** ✅
3. Now you can send to ANY email!

## 🧪 While Waiting for Approval

For development/testing, you can:

### Option 1: Use OTP from Console
- OTP is shown in backend console
- OTP is shown in frontend if email fails
- Use these for testing

### Option 2: Verify Test Emails
- Verify a few test email addresses in SES
- Use those for testing

### Option 3: Development Mode
- Set `ENVIRONMENT=development` 
- OTP will always be included in API response

## ✅ After Production Access

Once approved:
1. **No changes needed** to code
2. **Restart backend** (if needed)
3. **Test registration** - should work with any email
4. **Emails will be sent** to all users

## 📊 Expected Timeline

- **Request submitted**: Immediate
- **AWS review**: 24-48 hours
- **Approval**: Usually approved for OTP use cases
- **After approval**: Works immediately

## 🎯 Why This is Necessary

For a production app:
- ✅ Users register with any email
- ✅ OTP sent automatically
- ✅ No need to verify each user's email in SES
- ✅ Scalable for thousands of users

---

**Request production access now to enable registration for all users!** 🚀

