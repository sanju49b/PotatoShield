# 🔑 How to Update Your API Keys

## Quick Steps

1. **Update your `.env` file** in the project root with your new API keys
2. **Create `frontend/.env.local`** with the same `OPENAI_API_KEY` 
3. **Restart both backend and frontend**

## Detailed Instructions

### Step 1: Update Root .env File

Edit `.env` in the project root directory:

```env
OPENAI_API_KEY=sk-your-new-openai-key-here
TAVILY_API_KEY=tvly-your-new-tavily-key-here
GOOGLE_MAPS_API_KEY=your-new-google-maps-key-here
```

### Step 2: Update Frontend .env.local

Create or edit `frontend/.env.local`:

```env
OPENAI_API_KEY=sk-your-new-openai-key-here
```

**Why both files?**
- Root `.env` → Used by Python backend (`api/main.py`)
- `frontend/.env.local` → Used by Next.js API routes (`frontend/app/api/ai-advisor/route.ts`)

### Step 3: Restart Services

**Backend:**
```powershell
# Stop current backend (Ctrl+C)
# Then restart:
cd api
python main.py
```

**Frontend:**
```powershell
# Stop current frontend (Ctrl+C)
# Then restart:
cd frontend
npm run dev
```

## ✅ Verification

After restarting, check the console output:

**Backend should show:**
```
[OK] Loaded environment variables from C:\Users\satya\Desktop\Potato-Shield\.env
```

**Frontend API routes** will automatically use keys from `frontend/.env.local`

## 📋 All Files Using Environment Variables

All these files automatically read from `.env` - **no code changes needed!**

### Backend (Python):
- ✅ `api/main.py` - Loads .env automatically
- ✅ `src/agents/blight_prediction_agent.py` - Uses `os.getenv("OPENAI_API_KEY")` and `os.getenv("TAVILY_API_KEY")`
- ✅ `src/agents/diagnostic_agent.py` - Uses `os.getenv("OPENAI_API_KEY")` and `os.getenv("TAVILY_API_KEY")`
- ✅ `src/agents/streaming_narrator_agent.py` - Uses `os.getenv("OPENAI_API_KEY")`
- ✅ `src/agents/router_agent.py` - Uses `os.getenv("OPENAI_API_KEY")` (via LangChain)
- ✅ `src/agents/general_chat_agent.py` - Uses `os.getenv("OPENAI_API_KEY")` (via LangChain)
- ✅ `src/agents/data_collection_agent.py` - Uses `os.getenv("OPENAI_API_KEY")` (via LangChain)

### Frontend (Next.js):
- ✅ `frontend/app/api/ai-advisor/route.ts` - Uses `process.env.OPENAI_API_KEY`

## 🔍 Troubleshooting

### Keys not updating?
1. Make sure you saved the `.env` file
2. Restart both backend AND frontend
3. Check for typos in variable names (must be exact: `OPENAI_API_KEY`, not `OPENAI_API_KEY_`)

### Frontend API routes not working?
1. Create `frontend/.env.local` (not `.env`)
2. Add `OPENAI_API_KEY=your-key-here`
3. Restart Next.js dev server

### Backend not loading keys?
1. Check console for: `[OK] Loaded environment variables from...`
2. Verify `.env` is in project root (not in `api/` folder)
3. Ensure `python-dotenv` is installed: `pip install python-dotenv`

