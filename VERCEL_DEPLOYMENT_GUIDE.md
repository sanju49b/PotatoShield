# Vercel Multi-User Deployment Guide

## Overview

This guide explains how to deploy Potato Shield to Vercel with multi-user support. The application has been updated to support multiple concurrent users using DynamoDB for session and state management.

## Key Changes for Vercel

### ✅ Completed Fixes

1. **DynamoDB Session Management**
   - Added `potato-shield-sessions` table to DynamoDB
   - Sessions are stored in DynamoDB instead of in-memory
   - Supports multiple concurrent users across serverless functions

2. **OTP Storage**
   - OTPs stored in DynamoDB (no in-memory fallback for production)
   - Works across multiple function invocations

3. **Serverless-Compatible Data Collection**
   - Removed threading (not supported in serverless)
   - Progress messages collected and yielded (works on Vercel)

4. **Session Expiration**
   - Sessions expire after 24 hours
   - Automatic cleanup of expired sessions

## Environment Variables

Set these in Vercel dashboard:

```bash
USE_DYNAMODB=true
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

## Deployment Steps

### 1. Setup DynamoDB

1. Create AWS account (if not already)
2. Create IAM user with DynamoDB permissions
3. Get access key and secret key
4. Tables will be created automatically on first run

### 2. Configure Vercel

1. Go to Vercel project settings
2. Add environment variables:
   - `USE_DYNAMODB=true`
   - `AWS_REGION=us-east-1`
   - `AWS_ACCESS_KEY_ID=...`
   - `AWS_SECRET_ACCESS_KEY=...`

### 3. Deploy

```bash
vercel deploy --prod
```

## How It Works

### Session Management

- **Local Development**: Uses in-memory `active_sessions` dict
- **Vercel Production**: Uses DynamoDB `potato-shield-sessions` table
- Sessions are automatically checked on each request
- Expired sessions are automatically cleaned up

### Multi-User Support

- Each user gets a unique session token
- Sessions are stored in DynamoDB (shared across all function invocations)
- Multiple users can use the app simultaneously
- No session conflicts between users

### Data Collection Progress

- Progress messages are collected during data collection
- Messages are yielded after collection completes
- Works reliably on serverless (no threading required)

## Testing

### Test Multi-User Support

1. Open app in two different browsers
2. Login with two different accounts
3. Both users should be able to use the app simultaneously
4. Sessions should persist across page refreshes

### Test Session Expiration

1. Login to the app
2. Wait 24 hours (or modify expiration time)
3. Session should expire and require re-login

## Troubleshooting

### Sessions Not Working

- Check `USE_DYNAMODB=true` is set
- Check AWS credentials are correct
- Check DynamoDB tables are created
- Check IAM permissions include DynamoDB access

### OTP Not Working

- Check `USE_DYNAMODB=true` is set
- Check OTP table exists in DynamoDB
- Check OTP expiration time (default 10 minutes)

### Data Collection Progress Not Showing

- This is expected on serverless (messages collected then displayed)
- Messages will appear after data collection completes
- For real-time progress, consider using WebSockets (future enhancement)

## Limitations

### Serverless Constraints

1. **No Real-Time Progress**: Progress messages are collected then displayed (not real-time)
2. **Execution Time Limits**: Vercel has 10s (Hobby) or 60s (Pro) execution limits
3. **Cold Starts**: First request may be slower due to cold start

### Future Enhancements

1. **WebSockets**: For real-time progress updates
2. **Session Refresh**: Auto-refresh sessions before expiration
3. **Rate Limiting**: Prevent abuse with rate limiting
4. **Caching**: Cache frequently accessed data

## Cost Estimate

### DynamoDB Costs

- **Free Tier**: 25 GB storage, 25 read/write units per month
- **Paid Tier**: ~$0.25/GB storage, $1.25 per million writes
- **Typical Small App**: $0-5/month (stays in free tier)

### Vercel Costs

- **Hobby**: Free (with limitations)
- **Pro**: $20/month (unlimited)

## Security

### Session Security

- Sessions expire after 24 hours
- Tokens are UUIDs (unguessable)
- Sessions are stored securely in DynamoDB
- No sensitive data in sessions (only user_id)

### OTP Security

- OTPs expire after 10 minutes
- OTPs are single-use (verified flag)
- OTPs are stored securely in DynamoDB

## Support

For issues or questions:
1. Check logs in Vercel dashboard
2. Check DynamoDB tables in AWS console
3. Check environment variables are set correctly
4. Review this guide for common issues

