# Running API with DynamoDB

## Quick Start

### Windows (PowerShell)
```powershell
cd api
$env:USE_DYNAMODB="true"
$env:AWS_REGION="us-east-1"
python main.py
```

### Windows (CMD)
```cmd
cd api
set USE_DYNAMODB=true
set AWS_REGION=us-east-1
python main.py
```

### Linux/Mac
```bash
cd api
export USE_DYNAMODB=true
export AWS_REGION=us-east-1
python main.py
```

### Using Helper Scripts

**Windows:**
```cmd
cd api
start_with_dynamodb.bat
```

**Linux/Mac:**
```bash
cd api
chmod +x start_with_dynamodb.sh
./start_with_dynamodb.sh
```

## Verify It's Working

1. **Check console output** - Should see "DynamoDB client initialized"
2. **Test endpoint**: `http://localhost:8000/api/health`
3. **Register a user** - Check AWS DynamoDB console for `potato-shield-users` table
4. **Create a field** - Check `potato-shield-fields` table
5. **Send a message** - Check `potato-shield-messages` table

## AWS Credentials

Make sure AWS credentials are configured:

```bash
# Using AWS CLI (recommended)
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

## Testing

```bash
# Quick connection test
python quick_test_dynamodb.py

# Full test suite
python test_dynamodb.py
```

## Frontend Integration

The frontend automatically uses DynamoDB when backend has `USE_DYNAMODB=true` set.

No frontend changes needed! Just start the backend with DynamoDB enabled and the frontend will save all data to DynamoDB.

