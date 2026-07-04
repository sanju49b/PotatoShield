#!/bin/bash

echo "========================================"
echo "Starting Potato Shield Development"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found!"
    echo "Please create .env file with OPENAI_API_KEY"
    echo ""
fi

echo "Starting Backend Server..."
echo "Backend will run at: http://localhost:8000"
echo ""

# Start backend in new terminal (Linux/Mac)
cd api
python main.py &
BACKEND_PID=$!
cd ..

sleep 3

echo "Starting Frontend Server..."
echo "Frontend will run at: http://localhost:3000"
echo ""

# Start frontend in new terminal
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "Both servers are starting..."
echo "========================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

