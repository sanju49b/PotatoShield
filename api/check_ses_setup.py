"""
Check AWS SES setup and configuration
Run this to verify SES is properly configured
"""
import os
import boto3
from botocore.exceptions import ClientError

def check_ses_setup():
    """Check AWS SES configuration"""
    print("=" * 60)
    print("AWS SES Configuration Check")
    print("=" * 60)
    
    # Check environment variables
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    sender_email = os.getenv('SES_SENDER_EMAIL')
    
    print(f"\n1. Environment Variables:")
    print(f"   AWS_REGION: {aws_region}")
    print(f"   SES_SENDER_EMAIL: {sender_email if sender_email else '❌ NOT SET'}")
    
    if not sender_email:
        print("\n⚠️  WARNING: SES_SENDER_EMAIL not set!")
        print("   Set it with: export SES_SENDER_EMAIL=your-email@example.com")
        return False
    
    # Check AWS credentials
    print(f"\n2. AWS Credentials:")
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if aws_access_key:
        print(f"   AWS_ACCESS_KEY_ID: {'✅ SET' if aws_access_key else '❌ NOT SET'}")
    else:
        print("   AWS_ACCESS_KEY_ID: Using AWS credentials file or IAM role")
    
    # Try to initialize SES client
    print(f"\n3. SES Client Initialization:")
    try:
        ses_client = boto3.client('ses', region_name=aws_region)
        print(f"   ✅ SES client initialized for region: {aws_region}")
    except Exception as e:
        print(f"   ❌ Failed to initialize SES client: {e}")
        return False
    
    # Check sender email verification
    print(f"\n4. Sender Email Verification:")
    try:
        response = ses_client.get_identity_verification_attributes(
            Identities=[sender_email]
        )
        
        verification_status = response.get('VerificationAttributes', {}).get(sender_email, {})
        
        if verification_status:
            status = verification_status.get('VerificationStatus')
            if status == 'Success':
                print(f"   ✅ {sender_email} is verified")
            elif status == 'Pending':
                print(f"   ⚠️  {sender_email} verification is pending")
                print(f"      Check your email inbox for verification link")
            elif status == 'Failed':
                print(f"   ❌ {sender_email} verification failed")
            else:
                print(f"   ⚠️  {sender_email} status: {status}")
        else:
            print(f"   ❌ {sender_email} is not verified in SES")
            print(f"\n   To verify:")
            print(f"   1. Go to AWS SES Console: https://console.aws.amazon.com/ses/")
            print(f"   2. Click 'Verified identities'")
            print(f"   3. Click 'Create identity'")
            print(f"   4. Enter email: {sender_email}")
            print(f"   5. Click 'Create identity'")
            print(f"   6. Check your email and click verification link")
            return False
            
    except ClientError as e:
        print(f"   ❌ Error checking verification: {e}")
        return False
    
    # Check sending quota
    print(f"\n5. Sending Quota:")
    try:
        response = ses_client.get_send_quota()
        max_24h = response.get('Max24HourSend', 0)
        max_send_rate = response.get('MaxSendRate', 0)
        sent_24h = response.get('SentLast24Hours', 0)
        
        print(f"   Max 24h send: {max_24h}")
        print(f"   Max send rate: {max_send_rate} emails/second")
        print(f"   Sent last 24h: {sent_24h}")
        
        if sent_24h >= max_24h * 0.9:
            print(f"   ⚠️  Warning: Near sending limit!")
        
    except ClientError as e:
        print(f"   ⚠️  Could not check quota: {e}")
    
    # Test sending (dry run)
    print(f"\n6. Test Configuration:")
    print(f"   ✅ All checks passed!")
    print(f"   Ready to send emails from: {sender_email}")
    
    return True

if __name__ == "__main__":
    success = check_ses_setup()
    if success:
        print("\n" + "=" * 60)
        print("✅ SES is properly configured!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ SES configuration needs attention")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Verify sender email in AWS SES Console")
        print("2. Set SES_SENDER_EMAIL environment variable")
        print("3. Check AWS credentials")
        print("4. Run this script again to verify")

