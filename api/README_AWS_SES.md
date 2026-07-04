# AWS SES Email Integration

This application uses AWS SES (Simple Email Service) to send OTP verification emails.

## Setup Instructions

### 1. Verify Your Email in AWS SES

Before sending emails, you need to verify your sender email address in AWS SES:

1. Go to AWS Console → SES (Simple Email Service)
2. Navigate to "Verified identities"
3. Click "Create identity"
4. Choose "Email address"
5. Enter your sender email (e.g., `noreply@yourdomain.com`)
6. Click "Create identity"
7. Check your email and click the verification link

### 2. Configure AWS Credentials

You have three options:

#### Option A: Environment Variables (Recommended for local development)
```bash
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export SES_SENDER_EMAIL=noreply@yourdomain.com
```

#### Option B: AWS Credentials File
Create/edit `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = your_access_key_id
aws_secret_access_key = your_secret_access_key
```

And `~/.aws/config`:
```ini
[default]
region = us-east-1
```

#### Option C: IAM Role (For EC2/ECS/Lambda)
If running on AWS infrastructure, use IAM roles instead of access keys.

### 3. Set Environment Variables

Create a `.env` file in the `api/` directory:
```bash
AWS_REGION=us-east-1
SES_SENDER_EMAIL=noreply@yourdomain.com
ENVIRONMENT=production
```

### 4. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 5. Test the Integration

1. Start the API server:
```bash
python main.py
```

2. Send a test OTP:
```bash
curl -X POST http://localhost:8000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com"}'
```

3. Check your email inbox for the OTP code.

## AWS SES Sandbox Mode

If your AWS account is in **Sandbox mode** (default for new accounts):
- You can only send emails to verified email addresses
- You can send up to 200 emails per day
- You can send 1 email per second

To move out of Sandbox mode:
1. Go to AWS SES Console
2. Click "Account dashboard"
3. Click "Request production access"
4. Fill out the form explaining your use case

## Troubleshooting

### Error: "Email address is not verified"
- Solution: Verify your sender email in AWS SES console

### Error: "MessageRejected"
- Solution: The recipient email might not be verified (if in Sandbox mode)
- Solution: Check if your account is in Sandbox mode

### Error: "AccountSendingPausedException"
- Solution: Your account sending has been paused. Check AWS SES console and contact AWS support if needed.

### Fallback Behavior
If AWS SES fails, the system will:
1. Log the error
2. Still store the OTP in the database
3. Print a fallback message to console
4. Return success (so the frontend flow continues)

In production, you should monitor these errors and set up CloudWatch alarms.

## Production Best Practices

1. **Use IAM Roles**: Don't use access keys in production. Use IAM roles instead.
2. **Monitor Bounce/Complaint Rates**: Keep bounce rate < 5% and complaint rate < 0.1%
3. **Set Up SNS Notifications**: Configure SNS for bounce and complaint notifications
4. **Use Dedicated IPs**: For high-volume sending, request dedicated IPs
5. **Implement Rate Limiting**: Add rate limiting to prevent abuse
6. **Log Monitoring**: Set up CloudWatch logs and alarms

## Cost

AWS SES is very affordable:
- First 62,000 emails/month: FREE
- After that: $0.10 per 1,000 emails
- No monthly fees or setup costs

