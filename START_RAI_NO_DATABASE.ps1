# Start RAI Moderation Layer without database
# This sets environment variables and starts the service

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Starting RAI Toolkit (No Database)" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables to disable database
$env:DBTYPE = "False"
$env:FLASK_PORT = "5555"
$env:FLASK_HOST = "0.0.0.0"
$env:ENABLE_TELEMETRY = "false"
$env:VERIFY_SSL = "False"

# IMPORTANT: Set your OpenAI API key here!
# Replace YOUR_KEY_HERE with your actual key
$env:OPENAI_API_KEY = "your-openai-api-key-here"

Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  DBTYPE=$env:DBTYPE"
Write-Host "  FLASK_PORT=$env:FLASK_PORT"
Write-Host "  FLASK_HOST=$env:FLASK_HOST"
Write-Host "  OPENAI_API_KEY=$($env:OPENAI_API_KEY.Substring(0, [Math]::Min(10, $env:OPENAI_API_KEY.Length)))..."
Write-Host ""

# Navigate to RAI source directory
Set-Location "c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\src"

Write-Host "Starting RAI service..." -ForegroundColor Yellow
Write-Host ""

# Start Python with environment variables set
python main.py
