# ✅ CORRECTED: How to Actually Set Up Infosys RAI Toolkit

## 🎯 Answer to Your Question: **Do We Need an API Key?**

### **NO API KEY NEEDED for Local Development!**

The Infosys RAI Toolkit is **open source** and runs on your own machine. You only need:
- ✅ OpenAI API key (you already have this for Potato Shield)
- ✅ No special RAI API key for localhost setup
- ✅ No subscription fees
- ✅ Free to use under MIT License

**API key only needed if:**
- You deploy RAI Backend to a remote server with authentication
- You use cloud-hosted RAI services (optional)

---

## 🔧 What Went Wrong?

Looking at your terminal output, I found **two issues**:

### Issue 1: Requirements Files in Wrong Location
The setup script looked for `requirements.txt` in the root of each module, but they're actually in a `requirements/` subfolder!

**Actual location:**
```
rai-toolkit/responsible-ai-moderationlayer/requirements/requirement.txt  ← HERE
NOT: rai-toolkit/responsible-ai-moderationlayer/requirements.txt  ← WRONG
```

### Issue 2: RAI Backend Not Running
The tests failed with "connection refused" because no service is running on `http://localhost:5001`.

---

## ✅ CORRECTED Setup Process

### Step 1: Install ModerationLayer Module (CORE MODULE)

This is the main module that provides comprehensive RAI checks:

```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer

# Install from the requirements folder (note the subfolder!)
pip install -r requirements\requirement.txt
```

**Expected output:**
```
Collecting flask
Collecting pandas
Collecting numpy
...
Successfully installed flask-2.0.1 pandas-1.5.0 ...
```

---

### Step 2: Start ModerationLayer Service

```powershell
# Still in responsible-ai-moderationlayer folder
cd src
python app.py
```

**OR** (if there's a different entry point):
```powershell
python main.py
```

**OR** check the README for the correct startup command:
```powershell
type ..\README.md
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Running on http://localhost:5001
```

✅ **Keep this terminal open!** This is your RAI service running.

---

### Step 3: Test if RAI is Running

Open a **NEW PowerShell terminal**:

```powershell
# Test if service is responding
curl http://localhost:5001
# OR
curl http://localhost:5001/api/health
# OR
Invoke-WebRequest -Uri http://localhost:5001/api/health
```

**If you get a response** (not "connection refused"), ✅ **it's working!**

---

### Step 4: NOW Run Potato Shield Tests

```powershell
cd c:\Users\satya\Desktop\Potato-Shield
python test_rai_integration.py
```

**Expected:** Tests should now actually connect to RAI service and run properly!

---

## 🎯 Simplified Setup (Just What You Need)

You **DON'T** need all 10 RAI modules for basic functionality. Start with the **ModerationLayer** - it's the comprehensive module that includes:

✅ Safety checks
✅ Privacy (PII) detection
✅ Hallucination detection
✅ Fairness validation
✅ Explainability support

**Just install and run ModerationLayer** - that's 80% of what you need!

---

## 📋 Minimum Viable Setup (15 minutes)

### Quick 3-Command Setup:

```powershell
# 1. Install ModerationLayer dependencies
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer
pip install -r requirements\requirement.txt

# 2. Start ModerationLayer service
cd src
python app.py

# (Keep terminal open - service is running)
```

### In a NEW terminal:

```powershell
# 3. Test connection
cd c:\Users\satya\Desktop\Potato-Shield
python test_rai_integration.py
```

✅ **Done!** RAI is now protecting Potato Shield.

---

## 🔄 How to Use Daily

### Every time you work on Potato Shield:

**Terminal 1: Start RAI Service**
```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\src
python app.py
```
✅ Leave running

**Terminal 2: Start Potato Shield API**
```powershell
cd c:\Users\satya\Desktop\Potato-Shield\api
python main.py
```
✅ Should show "RAI Toolkit Enabled: True"

**Terminal 3: Start Frontend**
```powershell
cd c:\Users\satya\Desktop\Potato-Shield\frontend
npm run dev
```

**All 3 running?** ✅ Open http://localhost:3000

---

## 🆘 Still Not Working?

### Check RAI Backend README for exact startup commands:

```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer
notepad README.md
```

Look for sections titled:
- "Getting Started"
- "Installation"
- "Running the Service"
- "Quick Start"

Follow THOSE instructions instead of our generic ones!

---

## 💡 Alternative: Use RAI as Python Library (No Service)

If starting the RAI service is too complex, you can import RAI modules directly:

```powershell
# Install as Python package
cd rai-toolkit\responsible-ai-moderationlayer
pip install -e .
```

Then in your Python code:
```python
# Import directly (no HTTP requests needed)
from responsible_ai.moderationlayer import ModerationAPI

moderator = ModerationAPI()
result = moderator.check_input(text="What is disease risk?")
```

This is **simpler** than running a service, but check if the module supports this!

---

## 📊 Current Status Summary

✅ **Completed:**
- RAI Toolkit cloned
- Integration code written
- Configuration files created
- Documentation complete
- Test suite ready

⏳ **Blocked on:**
- Starting RAI ModerationLayer service
- Need to find correct startup command from official README

🎯 **Next Action:**
1. Read `rai-toolkit/responsible-ai-moderationlayer/README.md`
2. Find the "How to Run" section
3. Follow THEIR instructions to start the service
4. Then run our tests

---

## 📖 Key Insight

The Infosys RAI Toolkit is a **collection of microservices**, not a single unified backend. Each module (moderationlayer, hallucination, privacy, etc.) can run independently.

**For your needs**, start with **JUST the ModerationLayer** - it's the most comprehensive module and provides most features you need.

**Read the official README** in each module folder for accurate setup instructions!

---

**TL;DR:**
- ❌ No special API key needed (it's open source, runs on your machine)
- ❌ Our setup script had wrong paths (requirements are in `requirements/requirement.txt`)
- ✅ Install ModerationLayer: `pip install -r requirements\requirement.txt`
- ✅ Start service: `python src/app.py` (or check README for correct command)
- ✅ Then tests will work!

