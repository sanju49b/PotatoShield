@echo off
echo 🥔 Potato Shield Setup Script
echo ==============================
echo.

REM Backend setup
echo 📦 Setting up backend...
cd api
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

cd ..

REM Frontend setup
echo.
echo 📦 Setting up frontend...
cd frontend

if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install
)

echo.
echo ✅ Setup complete!
echo.
echo To start the backend:
echo   cd api && venv\Scripts\activate && python main.py
echo.
echo To start the frontend:
echo   cd frontend && npm run dev
echo.

pause

