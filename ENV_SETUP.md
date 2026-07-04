# 🔑 Environment Variables Setup Guide

This guide shows you where to update your API keys and how the system uses them.

## 📋 Required API Keys

### 1. **OPENAI_API_KEY** (Required)
- **Used by:**
  - `src/agents/blight_prediction_agent.py` - Disease prediction analysis
  - `src/agents/diagnostic_agent.py` - Image-based disease diagnosis
  - `src/agents/router_agent.py` - Request routing
  - `src/agents/general_chat_agent.py` - General chat responses
  - `src/agents/data_collection_agent.py` - Data collection prompts
  - `src/agents/streaming_narrator_agent.py` - Real-time narration
  - `frontend/app/api/ai-advisor/route.ts` - AI Crop Advisor component
- **How it's loaded:** Automatically via `os.getenv("OPENAI_API_KEY")` in Python, `process.env.OPENAI_API_KEY` in Next.js
- **Get your key:** https://platform.openai.com/api-keys

### 2. **TAVILY_API_KEY** (Required)
- **Used by:**
  - `src/agents/blight_prediction_agent.py` - Location-specific research
  - `src/agents/diagnostic_agent.py` - Disease management recommendations
- **How it's loaded:** `os.getenv("TAVILY_API_KEY")`
- **Get your key:** https://tavily.com/

### 3. **GOOGLE_MAPS_API_KEY** (Optional)
- **Used by:**
  - `api/main.py` - Enhanced geocoding (line 2738)
- **How it's loaded:** `os.getenv("GOOGLE_MAPS_API_KEY")`
- **Get your key:** https://console.cloud.google.com/apis/credentials
- **Note:** If not provided, system uses free geocoding services (Nominatim, Open-Meteo)

## 📁 Where to Place Your .env File

### Option 1: Root Directory (Recommended)
Create `.env` in the project root (same level as `api/` and `frontend/`):
```
Potato-Shield/
├── .env          ← Place here
├── api/
├── frontend/
└── src/
```

The backend (`api/main.py`) automatically loads this file.

### Option 2: Frontend Directory (For Next.js)
For Next.js API routes, also create `frontend/.env.local`:
```
frontend/
├── .env.local    ← Also create this for Next.js
├── app/
└── components/
```

## 🔧 How to Update Your API Keys

### Step 1: Create/Update .env File
Create a `.env` file in the project root with your keys:

```env
# Required
OPENAI_API_KEY=sk-your-actual-openai-key-here
TAVILY_API_KEY=tvly-your-actual-tavily-key-here

# Optional
GOOGLE_MAPS_API_KEY=your-google-maps-key-here

# AWS (if using DynamoDB)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=potato_care_users
USE_DYNAMODB=false

# Email (if using SES)
SES_SENDER_EMAIL=your-verified-email@example.com
SES_REGION=us-east-1

# Environment
ENVIRONMENT=development
```

### Step 2: Create frontend/.env.local (For Next.js)
Create `frontend/.env.local` with the same keys:

```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

### Step 3: Restart Services
After updating keys, restart both backend and frontend:

**Backend:**
```powershell
cd api
python main.py
```

**Frontend:**
```powershell
cd frontend
npm run dev
```

## ✅ Verification

All files are already configured to use environment variables. No code changes needed! Just update your `.env` file.

### Files That Use Environment Variables:
- ✅ `api/main.py` - Loads .env automatically (lines 12-23)
- ✅ `src/agents/blight_prediction_agent.py` - Uses `os.getenv("OPENAI_API_KEY")` and `os.getenv("TAVILY_API_KEY")`
- ✅ `src/agents/diagnostic_agent.py` - Uses `os.getenv("OPENAI_API_KEY")` and `os.getenv("TAVILY_API_KEY")`
- ✅ `src/agents/streaming_narrator_agent.py` - Uses `os.getenv("OPENAI_API_KEY")`
- ✅ `frontend/app/api/ai-advisor/route.ts` - Uses `process.env.OPENAI_API_KEY`

## 🔒 Security Notes

1. **Never commit .env files** - They contain sensitive keys
2. **Add to .gitignore** - Ensure `.env` and `.env.local` are ignored
3. **Rotate keys regularly** - Update keys if compromised
4. **Use different keys** - Use separate keys for development and production

## 🐛 Troubleshooting

### "API key not found" errors:
1. Check `.env` file exists in root directory
2. Verify keys are spelled correctly (no typos)
3. Restart backend/frontend after updating keys
4. Check for extra spaces or quotes around keys

### Frontend API routes not working:
1. Create `frontend/.env.local` with `OPENAI_API_KEY`
2. Restart Next.js dev server
3. Check browser console for errors

### Backend not loading keys:
1. Verify `.env` is in project root (not in `api/` folder)
2. Check `api/main.py` console output for: `[OK] Loaded environment variables from...`
3. Ensure `python-dotenv` is installed: `pip install python-dotenv`

