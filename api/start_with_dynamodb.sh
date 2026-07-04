#!/bin/bash
# Start FastAPI server with DynamoDB enabled

echo "Starting Potato Shield API with DynamoDB..."
echo

# Set environment variables
export USE_DYNAMODB=true
export AWS_REGION=${AWS_REGION:-us-east-1}

# Check if AWS credentials are set
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "Warning: AWS_ACCESS_KEY_ID not set"
    echo "Please set AWS credentials or use 'aws configure'"
    echo
fi

if [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "Warning: AWS_SECRET_ACCESS_KEY not set"
    echo "Please set AWS credentials or use 'aws configure'"
    echo
fi

# Set SES sender email if not set
if [ -z "$SES_SENDER_EMAIL" ]; then
    echo "Warning: SES_SENDER_EMAIL not set"
    echo "OTP emails will not be sent"
    echo
fi

echo "Environment:"
echo "  USE_DYNAMODB=$USE_DYNAMODB"
echo "  AWS_REGION=$AWS_REGION"
echo "  SES_SENDER_EMAIL=$SES_SENDER_EMAIL"
echo

# Start the server
python main.py

