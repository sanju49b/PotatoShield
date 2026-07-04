# DynamoDB Integration for Potato Shield

## Overview

Potato Shield now supports AWS DynamoDB for production deployments on Vercel. This provides:
- ✅ **Serverless database** - No database server to manage
- ✅ **Cost-effective** - Pay only for what you use (mostly free tier)
- ✅ **Scalable** - Auto-scales with your traffic
- ✅ **Fast** - Low latency globally
- ✅ **Reliable** - 99.99% uptime SLA

## Quick Start

### 1. Enable DynamoDB

Set environment variable:
```bash
export USE_DYNAMODB=true
```

Or in Vercel dashboard:
```
USE_DYNAMODB=true
```

### 2. Configure AWS Credentials

Set these environment variables:
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### 3. Test the Integration

```bash
cd api
python test_dynamodb.py
```

## Architecture

### Tables Created Automatically

1. **potato-shield-users** - User accounts (email as key)
2. **potato-shield-conversations** - Chat conversations
3. **potato-shield-messages** - Individual chat messages
4. **potato-shield-fields** - User's potato fields
5. **potato-shield-otp** - OTP codes for authentication

### Memory System

- **Short-term memory**: Recent conversation context (last 6 messages)
- **Long-term memory**: Persistent user data, fields, conversations
- **Automatic switching**: Uses SQLite locally, DynamoDB in production

## Cost Estimate

### Free Tier (Forever)
- 25 GB storage
- 25 write units/month
- 25 read units/month

### Paid Tier (after free tier)
- **Storage**: $0.25/GB/month
- **Writes**: $1.25 per million requests
- **Reads**: $0.25 per million requests

**Typical small app**: $0-5/month (mostly stays in free tier)

## Features

### ✅ OTP Authentication
- Email-based OTP verification
- Stored in DynamoDB with expiration
- Integrated with AWS SES

### ✅ User Management
- Email/password registration
- Email lookup by primary key (fast)
- User ID lookup via GSI (also fast)

### ✅ Conversation History
- All chats saved in DynamoDB
- Queryable by user_id
- Messages linked to conversations

### ✅ Field Management
- Location and sowing date storage
- Queryable by user_id
- Supports multiple fields per user

## Deployment to Vercel

1. **Set Environment Variables** in Vercel dashboard:
   ```
   USE_DYNAMODB=true
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=xxx
   AWS_SECRET_ACCESS_KEY=xxx
   SES_SENDER_EMAIL=noreply@yourdomain.com
   ```

2. **Deploy**:
   ```bash
   vercel --prod
   ```

3. **Tables are created automatically** on first API call

## Local Development

By default, uses SQLite (no DynamoDB needed):
```bash
# No setup needed - works out of the box
python api/main.py
```

To test DynamoDB locally:
```bash
export USE_DYNAMODB=true
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
python api/main.py
```

## Querying Users by Email

The DynamoDB implementation makes it easy to query users by email (primary key):

```python
from src.memory.long_term_memory import LongTermMemory

memory = LongTermMemory()
user = memory.get_user_by_email("user@example.com")
```

This is a direct primary key lookup - very fast and cost-effective!

## Migration from SQLite

If you have existing SQLite data:

1. Export data from SQLite
2. Import to DynamoDB (migration script TBD)
3. Set `USE_DYNAMODB=true`
4. Deploy

## Monitoring

- **AWS CloudWatch**: Monitor DynamoDB metrics
- **AWS Console**: View tables and usage
- **Cost Explorer**: Track spending

## Troubleshooting

### Tables not created?
- Check AWS credentials
- Verify IAM permissions
- Check AWS region

### Authentication errors?
- Verify DynamoDB tables exist
- Check user has password_hash (not OTP-only)
- Review server logs

### High costs?
- Check CloudWatch metrics
- Review query patterns
- Consider adding caching

## Support

For issues, check:
1. `api/test_dynamodb.py` - Run tests
2. `api/DYNAMODB_SETUP.md` - Detailed setup guide
3. AWS CloudWatch logs
4. Server console output

