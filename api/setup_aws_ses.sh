#!/bin/bash

echo "🔧 AWS SES Setup Helper"
echo "======================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed."
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

echo "✅ AWS CLI found"
echo ""

# Check AWS credentials
echo "Checking AWS credentials..."
aws sts get-caller-identity > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ AWS credentials are configured"
    AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region || echo "us-east-1")
    echo "   Account: $AWS_ACCOUNT"
    echo "   Region: $AWS_REGION"
else
    echo "❌ AWS credentials not configured"
    echo "Run: aws configure"
    exit 1
fi

echo ""

# Get sender email
read -p "Enter your sender email (must be verified in SES): " SENDER_EMAIL

if [ -z "$SENDER_EMAIL" ]; then
    echo "❌ Sender email is required"
    exit 1
fi

# Check if email is verified
echo "Checking if $SENDER_EMAIL is verified in SES..."
VERIFIED=$(aws sesv2 get-email-identity --email-identity "$SENDER_EMAIL" 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Email is verified in SES"
else
    echo "⚠️  Email may not be verified in SES"
    echo "   Go to AWS Console → SES → Verified identities"
    echo "   Verify: $SENDER_EMAIL"
fi

echo ""

# Create .env file
ENV_FILE=".env"
echo "Creating $ENV_FILE file..."

cat > "$ENV_FILE" << EOF
# AWS Configuration
AWS_REGION=$AWS_REGION
SES_SENDER_EMAIL=$SENDER_EMAIL

# Environment (set to 'development' to show OTP in response)
ENVIRONMENT=production
EOF

echo "✅ Created $ENV_FILE"
echo ""
echo "📝 Configuration:"
echo "   AWS_REGION=$AWS_REGION"
echo "   SES_SENDER_EMAIL=$SENDER_EMAIL"
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure $SENDER_EMAIL is verified in AWS SES"
echo "2. Install Python dependencies: pip install -r requirements.txt"
echo "3. Start the server: python main.py"
echo "4. Test by sending an OTP from the frontend"

