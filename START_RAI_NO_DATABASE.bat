@echo off
REM Start RAI Moderation Layer without database
REM This sets environment variables and starts the service

echo ====================================
echo Starting RAI Toolkit (No Database)
echo ====================================

REM Set environment variables to disable database
set DBTYPE=False
set FLASK_PORT=5555
set FLASK_HOST=0.0.0.0
set ENABLE_TELEMETRY=false

REM IMPORTANT: Set your OpenAI API key here!
REM Replace YOUR_KEY_HERE with your actual key
set OPENAI_API_KEY=YOUR_KEY_HERE

echo.
echo Configuration:
echo   DBTYPE=%DBTYPE%
echo   FLASK_PORT=%FLASK_PORT%
echo   FLASK_HOST=%FLASK_HOST%
echo   OPENAI_API_KEY=%OPENAI_API_KEY:~0,10%...
echo.

REM Navigate to RAI source directory
cd /d "c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\src"

echo Starting RAI service...
echo.

REM Start Python with environment variables set
python main.py

pause
