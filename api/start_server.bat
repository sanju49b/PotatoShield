@echo off
echo Starting Potato Shield API Server...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server...
echo Server will be available at http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python main.py

