@echo off
REM Start FastAPI server with DynamoDB enabled
echo Starting Potato Shield API with DynamoDB...
echo.

REM Set environment variables
set USE_DYNAMODB=true
set AWS_REGION=us-east-1

REM Check if AWS credentials are set
if "%AWS_ACCESS_KEY_ID%"=="" (
    echo Warning: AWS_ACCESS_KEY_ID not set
    echo Please set AWS credentials or use 'aws configure'
    echo.
)

if "%AWS_SECRET_ACCESS_KEY%"=="" (
    echo Warning: AWS_SECRET_ACCESS_KEY not set
    echo Please set AWS credentials or use 'aws configure'
    echo.
)

REM Set SES sender email if not set
if "%SES_SENDER_EMAIL%"=="" (
    echo Warning: SES_SENDER_EMAIL not set
    echo OTP emails will not be sent
    echo.
)

echo Environment:
echo   USE_DYNAMODB=%USE_DYNAMODB%
echo   AWS_REGION=%AWS_REGION%
echo   SES_SENDER_EMAIL=%SES_SENDER_EMAIL%
echo.

REM Start the server
python main.py

