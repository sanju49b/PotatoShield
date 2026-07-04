"""
Quick script to check if a user exists in DynamoDB and view their email
Usage: python check_user_in_dynamodb.py [email]
"""
import os
import sys

# Set environment variable to use DynamoDB
os.environ['USE_DYNAMODB'] = 'true'

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.memory.dynamodb_service import get_dynamodb_service

def list_all_users():
    """List all users in DynamoDB"""
    db = get_dynamodb_service()
    if not db:
        print("❌ Failed to connect to DynamoDB")
        return
    
    try:
        # Scan users table (for small datasets)
        response = db.users_table.scan()
        users = response.get('Items', [])
        
        if not users:
            print("No users found in DynamoDB")
            return
        
        print(f"\n📊 Found {len(users)} user(s) in DynamoDB:\n")
        print("=" * 80)
        
        for user in users:
            print(f"Email:      {user.get('email', 'N/A')}")
            print(f"User ID:    {user.get('user_id', 'N/A')}")
            print(f"Username:   {user.get('username', 'N/A')}")
            print(f"Created:    {user.get('created_at', 'N/A')}")
            print(f"Verified:   {user.get('verified', False)}")
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def get_user_by_email(email: str):
    """Get a specific user by email"""
    db = get_dynamodb_service()
    if not db:
        print("❌ Failed to connect to DynamoDB")
        return
    
    try:
        user = db.get_user_by_email(email)
        if user:
            print(f"\n✅ User found:\n")
            print("=" * 80)
            print(f"Email:      {user.get('email', 'N/A')}")
            print(f"User ID:    {user.get('user_id', 'N/A')}")
            print(f"Username:   {user.get('username', 'N/A')}")
            print(f"Created:    {user.get('created_at', 'N/A')}")
            print(f"Verified:   {user.get('verified', False)}")
            print("=" * 80)
        else:
            print(f"❌ User with email '{email}' not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Get specific user
        email = sys.argv[1]
        get_user_by_email(email)
    else:
        # List all users
        list_all_users()
        
        print("\n💡 Tip: To view a specific user, run:")
        print("   python check_user_in_dynamodb.py test@example.com")

