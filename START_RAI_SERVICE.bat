@echo off
echo ================================================================
echo Starting Infosys RAI ModerationLayer Service
echo ================================================================
echo.

cd /d c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\src

echo Setting environment variables...
set DBTYPE=False
set FLASK_PORT=5555
set FLASK_HOST=0.0.0.0
set OPENAI_API_KEY=your-openai-api-key-here

echo Bypassing authentication for local testing...
set TELEMETRY_ENVIRONMENT=AZURE
set TARGETENVIRONMENT=aicloud

echo.
echo Starting RAI service on port 5555...
echo Press Ctrl+C to stop the service
echo.

python main.py
