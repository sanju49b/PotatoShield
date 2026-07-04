"""
Check if backend is using DynamoDB or SQLite
"""
import os
import sys

# Check environment variable
use_dynamodb = os.getenv('USE_DYNAMODB', 'false').lower() == 'true'

print("=" * 60)
print("Backend Configuration Check")
print("=" * 60)
print(f"\nUSE_DYNAMODB environment variable: {os.getenv('USE_DYNAMODB', 'NOT SET')}")
print(f"DynamoDB enabled: {use_dynamodb}")
print(f"AWS Region: {os.getenv('AWS_REGION', 'NOT SET')}")
print(f"AWS Access Key ID: {'SET' if os.getenv('AWS_ACCESS_KEY_ID') else 'NOT SET'}")

if not use_dynamodb:
    print("\n❌ WARNING: DynamoDB is NOT enabled!")
    print("   Backend is using SQLite instead of DynamoDB")
    print("\n   To enable DynamoDB:")
    print("   PowerShell: $env:USE_DYNAMODB='true'")
    print("   CMD: set USE_DYNAMODB=true")
    print("   Then restart the backend server")
else:
    print("\n✅ DynamoDB is enabled!")
    
    # Try to connect
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from src.memory.dynamodb_service import get_dynamodb_service
        db = get_dynamodb_service()
        if db:
            print("✅ DynamoDB connection successful!")
            print(f"   Region: {db.aws_region}")
        else:
            print("❌ DynamoDB connection failed")
    except Exception as e:
        print(f"❌ Error connecting to DynamoDB: {e}")

print("\n" + "=" * 60)

