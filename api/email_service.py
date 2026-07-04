"""
AWS SES Email Service for sending OTP emails
"""
import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional

class SESEmailService:
    """AWS SES email service for sending OTP emails"""
    
    def __init__(self):
        # Get AWS region from environment or use default
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Get sender email from environment (must be verified in SES)
        self.sender_email = os.getenv('SES_SENDER_EMAIL')
        
        if not self.sender_email:
            print("⚠️  WARNING: SES_SENDER_EMAIL not set!")
            print("   Set it with: export SES_SENDER_EMAIL=your-verified-email@example.com")
            print("   Email sending will be disabled until this is set.")
        
        # Initialize SES client
        # AWS credentials are automatically picked up from:
        # 1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        # 2. AWS credentials file (~/.aws/credentials)
        # 3. IAM role (if running on EC2)
        try:
            self.ses_client = boto3.client('ses', region_name=self.aws_region)
            print(f"AWS SES client initialized for region: {self.aws_region}")
        except Exception as e:
            print(f"Warning: Failed to initialize AWS SES client: {e}")
            print("Falling back to mock email service")
            self.ses_client = None
    
    def send_otp_email(self, recipient_email: str, otp_code: str) -> bool:
        """
        Send OTP email via AWS SES
        
        Args:
            recipient_email: Recipient's email address
            otp_code: 6-digit OTP code
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.sender_email:
            print(f"⚠️  Cannot send email: SES_SENDER_EMAIL not set")
            print(f"   OTP code for {recipient_email}: {otp_code}")
            print(f"   Set SES_SENDER_EMAIL and verify email in AWS SES to enable email sending")
            return False
        
        if not self.ses_client:
            # Fallback to console output if SES not configured
            print(f"⚠️  SES client not initialized - email sending disabled")
            print(f"   OTP code for {recipient_email}: {otp_code}")
            return False
        
        # Email subject
        subject = "Your Potato Shield OTP Code"
        
        # Email body (HTML)
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #000000;
                    color: #FF6B35;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #0A0A0A;
                    border: 2px solid #FF6B35;
                    border-radius: 10px;
                    padding: 30px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .otp-code {{
                    font-size: 36px;
                    font-weight: bold;
                    text-align: center;
                    color: #4CAF50;
                    letter-spacing: 10px;
                    margin: 30px 0;
                    padding: 20px;
                    background-color: #000000;
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    color: #888888;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="color: #FF6B35; text-transform: uppercase;">POTATO SHIELD</h1>
                    <p style="color: #4CAF50;">Your OTP Verification Code</p>
                </div>
                
                <p>Your One-Time Password (OTP) for Potato Shield is:</p>
                
                <div class="otp-code">{otp_code}</div>
                
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
                
                <div class="footer">
                    <p>This is an automated message from Potato Shield AI System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
POTATO SHIELD - OTP VERIFICATION

Your One-Time Password (OTP) is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

This is an automated message from Potato Shield AI System.
        """
        
        try:
            # Send email via SES
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={
                    'ToAddresses': [recipient_email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': html_body,
                            'Charset': 'UTF-8'
                        },
                        'Text': {
                            'Data': text_body,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            
            print(f"OTP email sent successfully to {recipient_email}. MessageId: {response['MessageId']}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            print(f"AWS SES Error ({error_code}): {error_message}")
            
            # Common error handling
            if error_code == 'MessageRejected':
                if 'not verified' in error_message.lower():
                    # Check if it's sender or recipient
                    if self.sender_email and self.sender_email.lower() in error_message.lower():
                        print(f"❌ Error: Sender email {self.sender_email} is not verified in AWS SES.")
                        print(f"   Please verify {self.sender_email} in the AWS SES console:")
                        print(f"   https://console.aws.amazon.com/ses/")
                    else:
                        print(f"❌ Error: Recipient email {recipient_email} is not verified.")
                        print(f"   AWS SES is in SANDBOX MODE - you can only send to verified emails.")
                        print(f"   Solutions:")
                        print(f"   1. Verify {recipient_email} in AWS SES Console (for testing)")
                        print(f"   2. Request production access in SES Console (to send to any email)")
                        print(f"   3. Or verify the sender email {self.sender_email} if not already done")
                else:
                    print(f"Error: Message rejected - {error_message}")
            elif error_code == 'MailFromDomainNotVerified':
                print("Error: The sender domain is not verified in AWS SES.")
            elif error_code == 'AccountSendingPausedException':
                print("Error: Account sending is paused. Check AWS SES console.")
            
            # Fallback to console for development
            print(f"[FALLBACK] OTP {otp_code} would be sent to {recipient_email}")
            return False
            
        except Exception as e:
            print(f"Unexpected error sending email: {e}")
            print(f"[FALLBACK] OTP {otp_code} would be sent to {recipient_email}")
            return False

# Initialize email service singleton
email_service = SESEmailService()

def send_otp_email(email: str, otp: str) -> bool:
    """
    Convenience function to send OTP email
    
    Args:
        email: Recipient email address
        otp: OTP code to send
        
    Returns:
        bool: True if sent successfully
    """
    return email_service.send_otp_email(email, otp)

