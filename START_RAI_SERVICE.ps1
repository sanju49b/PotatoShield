Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Starting Infosys RAI ModerationLayer Service" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\src"

Write-Host "Setting environment variables..." -ForegroundColor Yellow
$env:DBTYPE = "False"
$env:FLASK_PORT = "5555"
$env:FLASK_HOST = "0.0.0.0"
$env:OPENAI_API_KEY = "your-openai-api-key-here"

Write-Host "Bypassing authentication for local testing..." -ForegroundColor Yellow
$env:TELEMETRY_ENVIRONMENT = "AZURE"
$env:TARGETENVIRONMENT = "aicloud"

Write-Host ""
Write-Host "Starting RAI service on port 5555..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host ""

python main.py
