@echo off
echo ========================================
echo Starting Potato Shield Development
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Please create .env file with OPENAI_API_KEY
    echo.
)

echo Starting Backend Server (Terminal 1)...
echo Backend will run at: http://localhost:8000
echo.
start cmd /k "cd api && python main.py"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server (Terminal 2)...
echo Frontend will run at: http://localhost:3000
echo.
start cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window (servers will keep running)
pause >nul

