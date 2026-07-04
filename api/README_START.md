# How to Start the Backend API Server

The backend is a **Python FastAPI** application, not Node.js.

## Quick Start (Windows)

### Option 1: Use the batch file
```bash
cd api
start_server.bat
```

### Option 2: Manual start

1. **Navigate to api directory:**
```bash
cd api
```

2. **Create virtual environment (if not exists):**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Start the server:**
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Server Information

- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

## Troubleshooting

### "python: command not found"
- Make sure Python is installed
- Add Python to PATH, or use full path: `C:\Python\python.exe`

### "Module not found"
- Make sure you activated the virtual environment
- Run: `pip install -r requirements.txt`

### Port 8000 already in use
- Change the port in `main.py` or use: `uvicorn main:app --port 8001`

