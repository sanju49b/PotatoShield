# AWS DynamoDB Setup for Vercel Deployment

## Overview

This application uses AWS DynamoDB for storing all persistent data when deployed to Vercel. DynamoDB is cost-effective with **PAY_PER_REQUEST** billing mode.

## Cost Analysis

### DynamoDB Pricing (Pay-Per-Request)
- **Free Tier**: 25 GB storage, 25 write units, 25 read units (forever free)
- **After Free Tier**: 
  - Write: $1.25 per million requests
  - Read: $0.25 per million requests
  - Storage: $0.25 per GB/month

**For a small app**: ~$0-5/month (mostly free tier)

## Setup Instructions

### 1. Create DynamoDB Tables

Tables are created automatically on first run, but you can also create them manually:

```bash
# Tables will be auto-created, but you can verify in AWS Console
# Go to: AWS Console → DynamoDB → Tables
```

### 2. Set Environment Variables

For **Vercel Deployment**, add these in Vercel dashboard:

```
USE_DYNAMODB=true
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
SES_SENDER_EMAIL=noreply@yourdomain.com
```

For **Local Development**, create `.env` file:

```env
USE_DYNAMODB=true
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
SES_SENDER_EMAIL=noreply@yourdomain.com
```

### 3. IAM Permissions Required

Your AWS user/role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:DescribeTable",
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/potato-shield-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
```

## DynamoDB Tables Created

### 1. `potato-shield-users`
- **Key**: email (partition key)
- **GSI**: user_id-index (for lookups by user_id)
- **Stores**: User accounts, emails, password hashes

### 2. `potato-shield-conversations`
- **Key**: conversation_id (partition key)
- **GSI**: user_id-index (for querying user's conversations)
- **Stores**: Chat sessions/conversations

### 3. `potato-shield-messages`
- **Key**: message_id (partition key)
- **GSI**: conversation_id-index (for querying messages in a conversation)
- **Stores**: All chat messages

### 4. `potato-shield-fields`
- **Key**: field_id (partition key)
- **GSI**: user_id-index (for querying user's fields)
- **Stores**: User's potato fields (location, sowing date, etc.)

### 5. `potato-shield-otp`
- **Key**: email (partition key)
- **Stores**: OTP codes for email verification

## Querying Users by Email

You can easily query users by email:

```python
# Get user by email (primary key lookup - very fast)
user = db.get_user_by_email("user@example.com")

# Get user by user_id (GSI lookup - also fast)
user = db.get_user_by_id("user-id-123")
```

## Migration from SQLite

If you have existing SQLite data:

1. Export data from SQLite
2. Import to DynamoDB using migration script (to be created)
3. Switch to DynamoDB by setting `USE_DYNAMODB=true`

## Testing Locally

```bash
# Set environment variable
export USE_DYNAMODB=true

# Start server
python main.py
```

Tables will be created automatically on first run.

## Monitoring

- **AWS CloudWatch**: Monitor DynamoDB metrics
- **AWS Console**: View tables, items, and usage
- **Cost Explorer**: Track spending (should be minimal)

## Benefits

✅ **Serverless**: No database server to manage  
✅ **Scalable**: Auto-scales with traffic  
✅ **Cost-effective**: Pay only for what you use  
✅ **Fast**: Low latency, global distribution  
✅ **Reliable**: 99.99% uptime SLA  
✅ **Vercel Compatible**: Works perfectly with serverless functions

