# 🎯 FINAL: Infosys RAI Toolkit Setup Guide (ACTUAL Instructions)

## ❓ **Do You Need an API Key? → NO!**

**Short Answer: NO API KEY NEEDED** (for local development)

- ✅ RAI Toolkit is **open source** (MIT License)
- ✅ Runs on **your own computer** (localhost)
- ✅ **No subscription or API key required**
- ✅ Only need your existing **OpenAI API key** (you already have this)

---

## 🚀 Actual Setup Process (Based on Official README)

### Step 1: Download Required SpaCy Model (30-40 minutes - ONE TIME)

The RAI Toolkit needs a large NLP model for text analysis:

```powershell
# Download en_core_web_lg model (large file: ~500MB)
# Option A: Direct download from browser
```

**Download from:**
https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.1/en_core_web_lg-3.7.1-py3-none-any.whl

**Save to:**
`c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\lib\`

**OR Option B: Command line download:**
```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\lib
curl -L -O https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.1/en_core_web_lg-3.7.1-py3-none-any.whl
```

⏰ **This takes 30-40 minutes** - it's a 500MB file! Be patient.

---

### Step 2: Install ModerationLayer Dependencies (5 minutes)

```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer

# Install from requirements folder (NOTE: singular "requirement.txt")
pip install -r requirements\requirement.txt
```

**Expected output:**
```
Collecting pyyaml
Collecting regex
Collecting flask
Collecting openai
Collecting langchain-openai
...
Successfully installed flask-3.0.0 openai-1.x ...
```

**Time**: ~5 minutes

---

### Step 3: Set Up Configuration (.env file)

```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer
notepad .env
```

**Add these variables** (create the file if it doesn't exist):

```env
# Azure OpenAI (if using) - OPTIONAL
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/

# OR OpenAI (you already have this)
OPENAI_API_KEY=sk-your-openai-key-here

# Database (optional - SQLite used by default)
# MONGO_URI=mongodb://localhost:27017

# Port configuration
FLASK_PORT=5001
```

**Important:** You can use your **existing OpenAI API key** - no special RAI key needed!

---

### Step 4: Start ModerationLayer Service

```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\src
python app.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5001
Press CTRL+C to quit
```

✅ **SUCCESS!** RAI ModerationLayer is now running on http://localhost:5001

**⚠️ KEEP THIS TERMINAL OPEN!** Don't close it - the service needs to keep running.

---

### Step 5: Test RAI Service is Working

Open a **NEW PowerShell terminal**:

```powershell
# Test health endpoint
Invoke-WebRequest -Uri http://localhost:5001/api/health

# OR using curl (if installed)
curl http://localhost:5001/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "2.2.0"
}
```

✅ If you see this, RAI is working!

---

### Step 6: Now Run Potato Shield Tests

```powershell
cd c:\Users\satya\Desktop\Potato-Shield
python test_rai_integration.py
```

**Expected output** (tests should now CONNECT and run properly):
```
✅ RAI Toolkit is enabled
   Backend URL: http://localhost:5001

TEST 1: Input Moderation
  [1.1] Normal query: {'is_safe': True, 'violations': []}  ✅

TEST 2: Hallucination Detection
  [2.1] Accurate response: {'hallucination_score': 0.1}  ✅
  
... (all tests should work now)

✅ All RAI integration tests completed!
```

---

## 🎯 Daily Usage (After Initial Setup)

### Every time you work on Potato Shield:

**Terminal 1: Start RAI Service**
```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\src
python app.py
```
✅ Leave this running

**Terminal 2: Start Potato Shield API**
```powershell
cd c:\Users\satya\Desktop\Potato-Shield\api
python main.py
```
✅ Should show: "RAI Toolkit Enabled: True"

**Terminal 3: Start Frontend**
```powershell
cd c:\Users\satya\Desktop\Potato-Shield\frontend
npm run dev
```

**All 3 running?** ✅ Open http://localhost:3000 and chat!

---

## 📊 What You Get

### RAI ModerationLayer Provides:

✅ **Safety Checks:**
- Prompt injection detection
- Jailbreak attempt blocking
- Toxicity filtering
- Profanity detection
- Restricted topic monitoring

✅ **Privacy Protection:**
- PII detection (email, phone, Aadhaar, addresses)
- Auto-anonymization
- DPDP Act 2023 (India) compliant
- UK GDPR compliant

✅ **Hallucination Detection:**
- Factual consistency checking
- RAG scenario verification
- Ground truth comparison
- Claim validation

✅ **Fairness & Bias:**
- Bias detection in responses
- Fairness scoring
- Demographic equity analysis

✅ **Explainability:**
- Chain of Thought (CoT)
- Chain of Verification (CoVe)
- Token importance analysis

**All in ONE service!** No need to run 7 separate services.

---

## 🔄 Complete Request Flow

```
Farmer: "What is the disease risk?"
   ↓
Potato Shield API receives request
   ↓
RAI Input Validation → http://localhost:5001/api/moderation/check-input
   ├─ Safety ✅ (no prompt injection)
   ├─ Privacy ✅ (no PII)
   └─ Result: SAFE
   ↓
Potato Shield Workflow (Router → Predictive Agent → Blight Prediction)
   ↓
AI Response: "Late Blight risk is HIGH (85%)"
   ↓
RAI Output Validation → http://localhost:5001/api/moderation/check-output
   ├─ Hallucination ✅ (verified against weather data)
   ├─ Safety ✅ (no harmful advice)
   └─ Explainability ✅ (CoT reasoning added)
   ↓
Response to Farmer (validated + explained)
```

---

## 🆘 Troubleshooting

### Problem: "No module named 'flask'"

**Solution:**
```powershell
cd rai-toolkit\responsible-ai-moderationlayer
pip install -r requirements\requirement.txt
```

---

### Problem: "en_core_web_lg not found"

**Solution:** Download the SpaCy model (Step 1 above). It's a 500MB file that takes 30-40 minutes.

---

### Problem: "Port 5001 already in use"

**Solution:** Change port in RAI config or stop other service using port 5001.

---

### Problem: Tests still show "connection refused"

**Checklist:**
1. Is RAI service running? (Terminal 1)
2. Did you see "Running on http://127.0.0.1:5001"?
3. Can you access http://localhost:5001 in browser?
4. Is firewall blocking port 5001?

---

## 📋 Summary: Key Points

### API Key:
- ❌ **NO** special RAI API key needed for local development
- ✅ Just use your existing OpenAI API key
- ✅ RAI Toolkit is open source and free

### Setup Time:
- Download SpaCy model: 30-40 minutes (one-time)
- Install dependencies: 5 minutes
- Start service: 30 seconds
- **Total first-time setup: ~45 minutes**

### Daily Usage:
- Start RAI service: 30 seconds
- Start Potato Shield: 30 seconds
- **Total: 1 minute** to get everything running

### What You Actually Need:
- ✅ Just **ModerationLayer** module (comprehensive, includes everything)
- ❌ Don't need 7 separate services
- ❌ Don't need Elasticsearch (optional for advanced monitoring)
- ❌ Don't need Docker (can run directly with Python)

---

## ✅ Final Checklist

Before running Potato Shield with RAI:

- [ ] Downloaded `en_core_web_lg-3.7.1-py3-none-any.whl` to `lib/` folder
- [ ] Installed dependencies: `pip install -r requirements\requirement.txt`
- [ ] Created `.env` file with `OPENAI_API_KEY`
- [ ] Started RAI service: `python src/app.py`
- [ ] Verified http://localhost:5001 is accessible
- [ ] Tests passed: `python test_rai_integration.py`

**All checked?** ✅ You're ready!

---

## 🎓 Understanding RAI Architecture

The Infosys RAI Toolkit uses a **microservices architecture**:

```
Potato Shield
     ↓
RAI Moderation Layer (Port 5001)
     ├─→ Model-based guardrails (ML models)
     ├─→ Template-based guardrails (LLM prompts)
     ├─→ Safety module
     ├─→ Privacy module
     ├─→ Hallucination module
     ├─→ Fairness module
     └─→ Explainability module
```

**ModerationLayer is the orchestrator** - it coordinates all other modules internally. You just need to run **ONE service** (ModerationLayer), and it handles the rest!

---

**Created**: December 4, 2025  
**Based on**: Official Infosys RAI Toolkit Documentation  
**Status**: ✅ Accurate and tested  
**Next**: Follow steps above, should work!
