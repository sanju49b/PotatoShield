# Vercel Multi-User Support - Required Fixes

## Issues Identified

### 1. ❌ In-Memory Session Storage
- **Problem**: `active_sessions: Dict[str, str] = {}` is in-memory and doesn't work across multiple serverless functions
- **Impact**: Sessions are lost when function ends, users get logged out
- **Fix**: Use DynamoDB sessions table (already implemented in dynamodb_service.py)

### 2. ❌ In-Memory OTP Storage
- **Problem**: `otp_storage: Dict[str, str] = {}` is in-memory fallback
- **Impact**: OTPs don't work across function invocations
- **Fix**: Remove in-memory fallback, use DynamoDB only

### 3. ❌ Threading in Serverless
- **Problem**: `threading.Thread` and `Queue` don't work reliably in Vercel serverless
- **Impact**: Data collection progress streaming fails
- **Fix**: Replace with async/await pattern

### 4. ⚠️ Session Management
- **Status**: DynamoDB sessions table added, but API not fully using it
- **Fix**: Update all session operations to use DynamoDB

## Implementation Status

### ✅ Completed
- [x] Added sessions table to DynamoDB service
- [x] Added session CRUD methods to DynamoDB service
- [x] Updated API to conditionally use DynamoDB sessions

### ⚠️ Partially Completed
- [ ] Replace all `active_sessions[token]` with DynamoDB calls
- [ ] Remove `otp_storage` in-memory fallback
- [ ] Replace threading with async for data collection

### ❌ Not Started
- [ ] Replace threading in `blight_prediction_agent.py` with async
- [ ] Test multi-user concurrent requests
- [ ] Add session cleanup/expiration

## Next Steps

1. **Update `require_verified_user` function** to use DynamoDB
2. **Replace all session storage** with DynamoDB calls
3. **Remove OTP in-memory fallback** (use DynamoDB only)
4. **Replace threading with async** for data collection progress
5. **Test with multiple concurrent users**

## Environment Variables Required

```bash
USE_DYNAMODB=true
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

## Testing

1. Deploy to Vercel with `USE_DYNAMODB=true`
2. Test with multiple users simultaneously
3. Verify sessions persist across function invocations
4. Verify OTP works across function invocations
5. Verify data collection progress streams correctly

