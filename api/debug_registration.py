"""
Debug script to test user registration and see what's happening
"""
import os
import sys
import requests

# Set environment variable to use DynamoDB
os.environ['USE_DYNAMODB'] = 'true'

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.memory.long_term_memory import LongTermMemory

def test_registration(email: str, password: str, username: str = None):
    """Test user registration directly"""
    print(f"\n{'='*60}")
    print("Testing User Registration")
    print(f"{'='*60}\n")
    
    try:
        memory = LongTermMemory()
        
        print(f"1. Attempting to create user: {email}")
        user_id = memory.create_user(email, password, username)
        print(f"   ✅ User created with ID: {user_id}\n")
        
        print(f"2. Verifying user exists in DynamoDB...")
        user = memory.get_user_by_email(email)
        if user:
            print(f"   ✅ User found in DynamoDB!")
            print(f"   Email: {user.get('email')}")
            print(f"   User ID: {user.get('user_id')}")
            print(f"   Username: {user.get('username')}")
        else:
            print(f"   ❌ User NOT found in DynamoDB!")
        
        return user_id
        
    except ValueError as e:
        print(f"   ❌ Error: {e}")
        if "already exists" in str(e).lower():
            print(f"   ℹ️  User already exists - this is expected if you registered before")
            user = memory.get_user_by_email(email)
            if user:
                print(f"   ✅ Found existing user: {user.get('email')}")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_api_registration(email: str, password: str, username: str = None):
    """Test registration via API endpoint"""
    print(f"\n{'='*60}")
    print("Testing API Registration Endpoint")
    print(f"{'='*60}\n")
    
    try:
        url = "http://localhost:8000/api/auth/register"
        data = {
            "email": email,
            "password": password
        }
        if username:
            data["username"] = username
        
        print(f"1. Sending POST request to: {url}")
        print(f"   Data: {data}\n")
        
        response = requests.post(url, json=data)
        
        print(f"2. Response Status: {response.status_code}")
        print(f"   Response Body: {response.json()}\n")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Registration successful!")
                print(f"   User ID: {result.get('user_id')}")
                print(f"   Email: {result.get('email')}")
                
                # Verify in DynamoDB
                print(f"\n3. Verifying in DynamoDB...")
                memory = LongTermMemory()
                user = memory.get_user_by_email(email)
                if user:
                    print(f"   ✅ User found in DynamoDB!")
                else:
                    print(f"   ❌ User NOT found in DynamoDB!")
            else:
                print(f"   ❌ Registration failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ Registration failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to backend!")
        print(f"   Make sure backend is running on http://localhost:8000")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python debug_registration.py <email> <password> [username]")
        print("\nExample:")
        print("  python debug_registration.py test@example.com password123 myuser")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    username = sys.argv[3] if len(sys.argv) > 3 else None
    
    print("\n" + "="*60)
    print("DEBUG: User Registration")
    print("="*60)
    
    # Test direct registration
    print("\n[TEST 1] Direct Registration (via memory)")
    test_registration(email, password, username)
    
    # Test API registration
    print("\n[TEST 2] API Registration (via HTTP)")
    test_api_registration(email, password, username)
    
    print("\n" + "="*60)
    print("Debug Complete")
    print("="*60)

