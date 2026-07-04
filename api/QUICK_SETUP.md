# Quick AWS SES Setup

Since you're already logged into AWS via terminal, follow these steps:

## 1. Verify Your Sender Email in AWS SES

```bash
# Go to AWS SES Console and verify your email
# Or use AWS CLI:
aws sesv2 create-email-identity --email-identity your-email@example.com
```

Then check your email and click the verification link.

## 2. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

## 3. Set Environment Variables

Since you're already authenticated with AWS CLI, the credentials are automatically picked up. Just set:

```bash
export SES_SENDER_EMAIL=your-verified-email@example.com
export AWS_REGION=us-east-1  # or your preferred region
```

Or create a `.env` file:
```bash
SES_SENDER_EMAIL=your-verified-email@example.com
AWS_REGION=us-east-1
ENVIRONMENT=production
```

## 4. Test It

```bash
python main.py
```

Then try sending an OTP from the frontend. Check your email inbox!

## Troubleshooting

If emails don't send:
1. Check AWS SES console - make sure your email is verified
2. Check CloudWatch logs for errors
3. If in Sandbox mode, you can only send to verified emails

The system will automatically fall back to console logging if SES fails, so the app will still work.

