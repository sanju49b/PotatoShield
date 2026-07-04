# Running Development Servers Locally

## Quick Start

### Option 1: Run Both Servers (Recommended)

**Terminal 1 - Backend (FastAPI):**
```bash
cd api
python main.py
```
Server will run at: http://localhost:8000

**Terminal 2 - Frontend (Next.js):**
```bash
cd frontend
npm run dev
```
Frontend will run at: http://localhost:3000

---

## Detailed Instructions

### Prerequisites

1. **Python 3.8+** installed
2. **Node.js 18+** installed
3. **.env file** with `OPENAI_API_KEY` in project root

### Step 1: Setup Backend

```bash
# Navigate to api directory
cd api

# Install Python dependencies (if not already installed)
pip install -r requirements.txt

# Make sure .env file exists in project root with OPENAI_API_KEY
# If not, create it:
# OPENAI_API_KEY=your_key_here
```

### Step 2: Start Backend Server

```bash
# From api directory
python main.py
```

Or use the batch file (Windows):
```bash
start_server.bat
```

**Backend will be available at:** http://localhost:8000

**Test it:**
- Health check: http://localhost:8000/api/health
- API docs: http://localhost:8000/docs

### Step 3: Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies (if not already installed)
npm install
```

### Step 4: Start Frontend Server

```bash
# From frontend directory
npm run dev
```

**Frontend will be available at:** http://localhost:3000

---

## Testing the Predictive Agent

Once both servers are running:

1. **Open browser:** http://localhost:3000
2. **Login/Register** a user
3. **Setup a field** with:
   - Location (e.g., "Hyderabad, India" or "London, UK")
   - Sowing date
4. **Ask a prediction question:**
   - "What is the disease risk for my crop?"
   - "Will my potatoes get blight?"
   - "Predict disease risk"

The system will:
- Extract location and sowing date from your profile
- Collect weather data automatically
- Run blight prediction with all enhanced features
- Return comprehensive risk assessment

---

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Change port in api/main.py line 949:
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use different port
```

**Missing OPENAI_API_KEY:**
- Create `.env` file in project root
- Add: `OPENAI_API_KEY=your_key_here`

**Module not found errors:**
```bash
cd api
pip install -r requirements.txt
```

### Frontend Issues

**Port 3000 already in use:**
- Next.js will automatically use 3001, 3002, etc.

**npm install errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**API connection errors:**
- Make sure backend is running on port 8000
- Check `frontend/lib/api.ts` for correct API URL

---

## Quick Test Script

You can also test the prediction directly without the frontend:

```bash
# From project root
python test_blight.py
```

This will:
- Collect weather data for Hyderabad
- Run blight prediction
- Print the full report

---

## Environment Variables Needed

Create `.env` file in project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Optional (for AWS/DynamoDB):
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=potato_care_users
```

---

## API Endpoints for Testing

Once backend is running, you can test:

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**Chat Endpoint (requires auth):**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the disease risk?", "conversation_id": "test-123"}'
```

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

