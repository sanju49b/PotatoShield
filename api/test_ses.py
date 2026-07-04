"""
Quick test script to verify AWS SES email service is working
"""
import os
import sys
from email_service import send_otp_email

def test_ses():
    """Test AWS SES email sending"""
    print("🧪 Testing AWS SES Email Service")
    print("=" * 40)
    
    # Get sender email from environment
    sender_email = os.getenv('SES_SENDER_EMAIL')
    if not sender_email:
        print("❌ SES_SENDER_EMAIL not set in environment")
        print("   Set it with: export SES_SENDER_EMAIL=your-email@example.com")
        return False
    
    print(f"📧 Sender email: {sender_email}")
    
    # Get test recipient
    if len(sys.argv) > 1:
        recipient = sys.argv[1]
    else:
        recipient = input("Enter recipient email (must be verified if in Sandbox): ").strip()
    
    if not recipient:
        print("❌ Recipient email required")
        return False
    
    print(f"📬 Recipient: {recipient}")
    print("")
    
    # Generate test OTP
    import random
    import string
    test_otp = ''.join(random.choices(string.digits, k=6))
    
    print(f"🔑 Test OTP: {test_otp}")
    print("")
    print("📤 Sending email...")
    
    # Send email
    success = send_otp_email(recipient, test_otp)
    
    if success:
        print("✅ Email sent successfully!")
        print(f"   Check {recipient} inbox for the OTP code")
        return True
    else:
        print("⚠️  Email sending failed (check logs above)")
        print("   Common issues:")
        print("   1. Email not verified in SES")
        print("   2. Account in Sandbox mode (can only send to verified emails)")
        print("   3. AWS credentials not configured")
        return False

if __name__ == "__main__":
    test_ses()

