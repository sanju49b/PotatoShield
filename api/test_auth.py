"""
Test script to verify authentication is working
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.memory.long_term_memory import LongTermMemory

def test_auth():
    """Test authentication"""
    memory = LongTermMemory()
    
    # Test email and password
    test_email = input("Enter email to test: ").strip().lower()
    test_password = input("Enter password to test: ").strip()
    
    print(f"\nTesting authentication for: {test_email}")
    
    # Check if user exists
    user = memory.get_user_by_email(test_email)
    if not user:
        print("❌ User not found in database")
        return
    
    print(f"✓ User found: {user.get('user_id')}")
    print(f"  Email: {user.get('email')}")
    print(f"  Has password: {'Yes' if user.get('password_hash') else 'No'}")
    
    # Try authentication
    user_id = memory.authenticate_with_password(test_email, test_password)
    
    if user_id:
        print(f"✓ Authentication successful! User ID: {user_id}")
    else:
        print("❌ Authentication failed")
        print("\nPossible issues:")
        print("1. Password is incorrect")
        print("2. Password hash mismatch")
        print("3. User was created with OTP (no password)")

if __name__ == "__main__":
    test_auth()

