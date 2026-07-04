"""
Test script for DynamoDB integration
Run this to verify DynamoDB setup is working correctly
"""
import os
import sys

# Set environment variable to use DynamoDB
os.environ['USE_DYNAMODB'] = 'true'

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.memory.long_term_memory import LongTermMemory
from src.memory.short_term_memory import ShortTermMemory
from src.memory.dynamodb_service import get_dynamodb_service

def test_dynamodb_connection():
    """Test DynamoDB connection and table creation"""
    print("=" * 50)
    print("Testing DynamoDB Connection")
    print("=" * 50)
    
    try:
        db_service = get_dynamodb_service()
        if not db_service:
            print("❌ Failed to initialize DynamoDB service")
            print("Check your AWS credentials and region")
            return False
        
        print("✓ DynamoDB service initialized")
        print(f"✓ Region: {db_service.aws_region}")
        print(f"✓ Users table: {db_service.users_table_name}")
        print(f"✓ Conversations table: {db_service.conversations_table_name}")
        print(f"✓ Messages table: {db_service.messages_table_name}")
        print(f"✓ Fields table: {db_service.fields_table_name}")
        print(f"✓ OTP table: {db_service.otp_table_name}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_operations():
    """Test user creation and retrieval"""
    print("\n" + "=" * 50)
    print("Testing User Operations")
    print("=" * 50)
    
    try:
        memory = LongTermMemory()
        
        # Test user creation
        test_email = f"test_{os.getpid()}@example.com"
        print(f"\nCreating user: {test_email}")
        user_id = memory.create_user(
            email=test_email,
            password="testpassword123",
            username="testuser"
        )
        print(f"✓ User created with ID: {user_id}")
        
        # Test retrieving user by email
        user = memory.get_user_by_email(test_email)
        if user:
            print(f"✓ User retrieved: {user.get('email')}")
        else:
            print("❌ Failed to retrieve user")
            return False
        
        # Test authentication
        authenticated_user_id = memory.authenticate_with_password(
            test_email, 
            "testpassword123"
        )
        if authenticated_user_id == user_id:
            print("✓ Authentication successful")
        else:
            print("❌ Authentication failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_otp_operations():
    """Test OTP storage and verification"""
    print("\n" + "=" * 50)
    print("Testing OTP Operations")
    print("=" * 50)
    
    try:
        memory = LongTermMemory()
        
        test_email = f"otp_test_{os.getpid()}@example.com"
        test_otp = "123456"
        
        # Store OTP
        print(f"\nStoring OTP for: {test_email}")
        memory.store_otp(test_email, test_otp)
        print("✓ OTP stored")
        
        # Verify OTP
        is_valid = memory.verify_otp(test_email, test_otp)
        if is_valid:
            print("✓ OTP verification successful")
        else:
            print("❌ OTP verification failed")
            return False
        
        # Test invalid OTP
        is_invalid = memory.verify_otp(test_email, "999999")
        if not is_invalid:
            print("✓ Invalid OTP correctly rejected")
        else:
            print("❌ Invalid OTP was accepted")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_operations():
    """Test conversation and message operations"""
    print("\n" + "=" * 50)
    print("Testing Conversation Operations")
    print("=" * 50)
    
    try:
        memory = LongTermMemory()
        
        # Create test user
        test_email = f"conv_test_{os.getpid()}@example.com"
        user_id = memory.create_user(email=test_email, password="test123")
        
        # Create conversation
        print(f"\nCreating conversation for user: {user_id}")
        conv_id = memory.create_conversation(user_id, "Test Chat")
        print(f"✓ Conversation created: {conv_id}")
        
        # Add messages
        print("\nAdding messages...")
        memory.add_message_to_conversation(conv_id, "user", "Hello, how are you?")
        print("✓ User message added")
        
        memory.add_message_to_conversation(conv_id, "assistant", "I'm doing well, thank you!")
        print("✓ Assistant message added")
        
        # Retrieve messages
        messages = memory.get_conversation_messages(conv_id)
        print(f"✓ Retrieved {len(messages)} messages")
        
        if len(messages) == 2:
            print("✓ Conversation operations working correctly")
            return True
        else:
            print(f"❌ Expected 2 messages, got {len(messages)}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_field_operations():
    """Test field operations"""
    print("\n" + "=" * 50)
    print("Testing Field Operations")
    print("=" * 50)
    
    try:
        memory = LongTermMemory()
        
        # Create test user
        test_email = f"field_test_{os.getpid()}@example.com"
        user_id = memory.create_user(email=test_email, password="test123")
        
        # Add field
        print(f"\nAdding field for user: {user_id}")
        field_id = memory.add_field(
            user_id=user_id,
            location="Coventry, UK",
            sowing_date="2024-03-15",
            area_hectares=5.0
        )
        print(f"✓ Field created: {field_id}")
        
        # Get user profile (includes fields)
        profile = memory.get_user_profile(user_id)
        if profile and 'fields' in profile:
            fields = profile['fields']
            print(f"✓ Retrieved {len(fields)} fields")
            if len(fields) > 0:
                print(f"  Location: {fields[0].get('location')}")
                print(f"  Sowing Date: {fields[0].get('sowing_date')}")
                return True
        
        print("❌ Failed to retrieve fields")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n🚀 DynamoDB Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("DynamoDB Connection", test_dynamodb_connection),
        ("User Operations", test_user_operations),
        ("OTP Operations", test_otp_operations),
        ("Conversation Operations", test_conversation_operations),
        ("Field Operations", test_field_operations),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! DynamoDB integration is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())

