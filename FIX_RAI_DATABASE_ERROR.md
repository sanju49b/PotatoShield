# 🔧 FIX: RAI Database Connection Error

## 🎯 The Error You're Seeing

```
Startup  :  error in DB connection
TypeError: 'NoneType' object is not subscriptable
    logdb=mydb["Logdb"]
```

**Problem**: RAI ModerationLayer is trying to connect to MongoDB, but you don't have it configured.

**Solution**: Configure the database connection in the RAI `.env` file.

---

## ✅ SOLUTION (2 Options)

### Option 1: Use SQLite (Simplest - RECOMMENDED)

The RAI toolkit can work without MongoDB if you configure it correctly.

**Step 1: Create/Edit .env file in RAI ModerationLayer**

```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer
notepad .env
```

**Add these lines:**

```env
# OpenAI API Key (use your existing key)
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Database Configuration - Use SQLite (no MongoDB needed)
USE_SQLITE=true
DATABASE_TYPE=sqlite
SQLITE_DB_PATH=./data/rai_database.db

# OR disable database entirely if not needed
DISABLE_DATABASE=true

# Flask Configuration
FLASK_HOST=127.0.0.1
FLASK_PORT=5001
FLASK_DEBUG=false

# Optional: Azure Translation (disable if not using)
ENABLE_TRANSLATION=false
```

**Step 2: Try starting RAI again**

```powershell
cd src
python main.py
```

---

### Option 2: Install and Use MongoDB (More Complex)

If RAI requires MongoDB, you need to install it:

**Install MongoDB:**

```powershell
# Option A: Download MongoDB Installer
# Visit: https://www.mongodb.com/try/download/community
# Install MongoDB Community Edition

# Option B: Use Docker (easier)
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Then configure .env:**

```env
OPENAI_API_KEY=sk-your-key-here
MONGO_URI=mongodb://localhost:27017/rai_database
DATABASE_TYPE=mongodb
```

---

## 🎯 QUICK FIX (Try This First)

The RAI Toolkit README mentions it works with **SQLite by default**. The issue might be missing environment variables.

**Create a minimal .env file:**

```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer
notepad .env
```

**Paste EXACTLY this:**

```env
OPENAI_API_KEY=sk-proj-your-actual-openai-key-from-potato-shield-env-file

FLASK_PORT=5001
FLASK_HOST=127.0.0.1
FLASK_DEBUG=false

DATABASE_TYPE=sqlite
DISABLE_DATABASE=true
```

**Replace** `sk-proj-your-actual-openai-key...` with your **actual OpenAI API key** from your main `.env` file.

**Save and try again:**

```powershell
cd src
python main.py
```

---

## 📋 Alternative: Check RAI Configuration File

The RAI toolkit might have a config file where you can disable database:

```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\src
dir config\config.py
```

**Edit `config\config.py` and look for:**
```python
USE_DATABASE = True  # Change to False
# OR
MONGO_URI = "..."  # Comment out or set to None
```

---

## 🆘 Current Error Breakdown

**Error Location:**
```
File: rai-toolkit/responsible-ai-moderationlayer/src/dao/AdminDb.py (line 220)
Code: logdb=mydb["Logdb"]
Error: mydb is None (database connection failed)
```

**Why it's failing:**
1. RAI is trying to connect to MongoDB
2. No MongoDB connection string in environment
3. `mydb` returns `None`
4. Code tries to use `None["Logdb"]` → TypeError

**Fix:**
- Provide MongoDB connection string
- OR disable database entirely
- OR configure SQLite instead

---

## ✅ Recommended Fix (Copy This)

### Create `.env` file with database disabled:

```powershell
# 1. Navigate to RAI folder
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer

# 2. Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "FLASK_PORT=5001" >> .env
echo "DISABLE_DATABASE=true" >> .env
echo "DATABASE_TYPE=none" >> .env

# 3. Edit .env and add your REAL OpenAI key
notepad .env

# 4. Start service
cd src
python main.py
```

**Replace `sk-your-key-here` with your actual OpenAI API key!**

---

## 🎯 If That Doesn't Work

### Check RAI ModerationLayer README for database config:

```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer
notepad README.md
```

Look for sections about:
- "Database Configuration"
- "Environment Variables"
- "Running Without MongoDB"
- "SQLite Mode"

Follow THEIR instructions for database setup!

---

## 💡 Understanding the Issue

The Infosys RAI Toolkit is designed for **enterprise use** with:
- MongoDB for persistent storage
- User management & authentication
- Multi-tenant support

For **your use case** (single-user, local development), you probably:
- ❌ Don't need MongoDB
- ❌ Don't need persistent storage
- ✅ Can use in-memory or SQLite mode

The toolkit should have a **simplified mode** for local dev - check the official README!

---

## 📞 Next Steps

1. **Create `.env` file** with database disabled (see above)
2. **Try starting RAI** again: `python main.py`
3. **If still fails**, read the official README for database configuration
4. **Alternative**: Contact Infosys RAI team at Infosysraitoolkit@infosys.com for setup help

---

**TL;DR**: The RAI service needs database configuration. Create a `.env` file with `DISABLE_DATABASE=true` and your OpenAI API key, then try again!
