#!/bin/bash

echo "🥔 Potato Shield Setup Script"
echo "=============================="
echo ""

# Backend setup
echo "📦 Setting up backend..."
cd api
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

cd ..

# Frontend setup
echo ""
echo "📦 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the backend:"
echo "  cd api && source venv/bin/activate && python main.py"
echo ""
echo "To start the frontend:"
echo "  cd frontend && npm run dev"
echo ""

