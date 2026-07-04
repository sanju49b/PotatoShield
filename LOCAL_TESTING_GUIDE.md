# Local Testing Guide for DynamoDB Integration

## Prerequisites

1. **AWS Account** - You need an AWS account with DynamoDB access
2. **AWS CLI Configured** - Or set environment variables manually
3. **Python Dependencies** - All packages from `api/requirements.txt`

## Step 1: Configure AWS Credentials

### Option A: Using AWS CLI (Recommended)
```bash
aws configure
```
Enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Default output format (e.g., `json`)

### Option B: Set Environment Variables
```bash
# Windows PowerShell
$env:AWS_REGION="us-east-1"
$env:AWS_ACCESS_KEY_ID="your_access_key"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key"

# Windows CMD
set AWS_REGION=us-east-1
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key

# Linux/Mac
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

## Step 2: Verify AWS Credentials

```bash
aws sts get-caller-identity
```

This should return your AWS account ID and user info.

## Step 3: Test DynamoDB Connection

```bash
cd api
python test_dynamodb.py
```

This will:
- ✅ Test DynamoDB connection
- ✅ Create tables automatically (if they don't exist)
- ✅ Test user operations
- ✅ Test OTP operations
- ✅ Test conversation operations
- ✅ Test field operations

## Step 4: Start Server with DynamoDB

```bash
# Windows PowerShell
$env:USE_DYNAMODB="true"
$env:SES_SENDER_EMAIL="noreply@yourdomain.com"  # Optional, for OTP emails
python main.py

# Windows CMD
set USE_DYNAMODB=true
set SES_SENDER_EMAIL=noreply@yourdomain.com
python main.py

# Linux/Mac
export USE_DYNAMODB=true
export SES_SENDER_EMAIL=noreply@yourdomain.com
python main.py
```

## Step 5: Test API Endpoints

### Test Registration
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","username":"testuser"}'
```

### Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Test OTP (if SES configured)
```bash
curl -X POST http://localhost:8000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

## Verify Tables in AWS Console

1. Go to [AWS DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
2. Click "Tables" in left sidebar
3. You should see these tables:
   - `potato-shield-users`
   - `potato-shield-conversations`
   - `potato-shield-messages`
   - `potato-shield-fields`
   - `potato-shield-otp`

## Troubleshooting

### Error: "Unable to locate credentials"
- Make sure AWS credentials are set (see Step 1)
- Verify with `aws sts get-caller-identity`

### Error: "Access Denied"
- Check IAM permissions for DynamoDB
- User needs: `dynamodb:*` or specific permissions (see DYNAMODB_SETUP.md)

### Tables Not Created
- Check AWS region matches your credentials
- Verify DynamoDB service is available in your region
- Check CloudWatch logs for errors

### Test Script Fails
- Make sure you're in the `api` directory
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

## Quick Test Script

Create a file `quick_test.py`:

```python
import os
os.environ['USE_DYNAMODB'] = 'true'

from src.memory.dynamodb_service import get_dynamodb_service

db = get_dynamodb_service()
if db:
    print("✅ DynamoDB connected!")
    print(f"Region: {db.aws_region}")
else:
    print("❌ DynamoDB connection failed")
```

Run: `python quick_test.py`

## Expected Output

When running `test_dynamodb.py`, you should see:

```
🚀 DynamoDB Integration Test Suite
==================================================
Testing DynamoDB Connection
==================================================
✓ DynamoDB service initialized
✓ Region: us-east-1
✓ Users table: potato-shield-users
...

✓ PASS: DynamoDB Connection
✓ PASS: User Operations
✓ PASS: OTP Operations
✓ PASS: Conversation Operations
✓ PASS: Field Operations

Total: 5/5 tests passed
🎉 All tests passed! DynamoDB integration is working correctly.
```

