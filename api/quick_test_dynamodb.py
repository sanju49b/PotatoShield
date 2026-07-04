"""
Quick test to verify DynamoDB connection
Run this before running the full test suite
"""
import os
import sys

# Set environment variable to use DynamoDB
os.environ['USE_DYNAMODB'] = 'true'

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 50)
print("Quick DynamoDB Connection Test")
print("=" * 50)

try:
    from src.memory.dynamodb_service import get_dynamodb_service
    
    print("\n1. Testing DynamoDB service initialization...")
    db = get_dynamodb_service()
    
    if db:
        print("   ✅ DynamoDB service initialized successfully!")
        print(f"   Region: {db.aws_region}")
        print(f"   Users table: {db.users_table_name}")
        print(f"   Conversations table: {db.conversations_table_name}")
        print(f"   Messages table: {db.messages_table_name}")
        print(f"   Fields table: {db.fields_table_name}")
        print(f"   OTP table: {db.otp_table_name}")
        
        print("\n2. Testing table access...")
        try:
            # Try to access a table (this will create it if it doesn't exist)
            table = db.users_table
            print(f"   ✅ Users table accessible: {table.table_name}")
            print(f"   ✅ Table status: {table.table_status}")
            
            print("\n✅ All checks passed! DynamoDB is ready to use.")
            print("\nNext steps:")
            print("  1. Run full test: python test_dynamodb.py")
            print("  2. Start server: USE_DYNAMODB=true python main.py")
            
        except Exception as e:
            print(f"   ⚠️  Table access error: {e}")
            print("   This might be normal if tables don't exist yet.")
            print("   They will be created automatically on first use.")
            
    else:
        print("   ❌ Failed to initialize DynamoDB service")
        print("\nTroubleshooting:")
        print("  1. Check AWS credentials:")
        print("     - Run: aws configure")
        print("     - Or set: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("  2. Check AWS region:")
        print("     - Set: AWS_REGION=us-east-1")
        print("  3. Verify IAM permissions for DynamoDB")
        sys.exit(1)
        
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    print("\nTroubleshooting:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Make sure you're in the 'api' directory")
    sys.exit(1)
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\nTroubleshooting:")
    print("  1. Verify AWS credentials are set correctly")
    print("  2. Check AWS region matches your credentials")
    print("  3. Ensure boto3 is installed: pip install boto3")
    sys.exit(1)

