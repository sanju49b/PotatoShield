# 🚀 START RAI SERVICE - Do This FIRST!

## ⚠️ Your Current Problem

The tests are failing with:
```
[WinError 10061] No connection could be made because the target machine actively refused it
```

**Reason**: No service is running on `http://localhost:5001`

**Solution**: You must **START the RAI ModerationLayer service FIRST** before running tests!

---

## ✅ DO THIS NOW (3 Steps)

### Step 1: Open a NEW Terminal (Keep it separate!)

**Open a NEW PowerShell terminal** (don't use your existing one)

---

### Step 2: Navigate to RAI Service Directory

```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\src
```

---

### Step 3: Start the RAI Service

```powershell
python app.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5001
Press CTRL+C to quit
```

✅ **If you see this, SUCCESS!**

**⚠️ KEEP THIS TERMINAL OPEN! Don't close it!**

The RAI service needs to keep running while you use Potato Shield.

---

## 🧪 Now Try Your Tests Again

Go back to your **original terminal** (where you ran tests) and run:

```powershell
python test_rai_integration.py
```

**Now it should work!** The tests will connect to http://localhost:5001 and actually run.

---

## 🎯 Quick Visual Guide

### Terminal Layout:

```
┌─────────────────────────────────────┐
│ Terminal 1: RAI Service             │
│ cd rai-toolkit\...\src              │
│ python app.py                       │
│ (KEEP RUNNING - Don't close!)       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Terminal 2: Tests/Development       │
│ cd Potato-Shield                    │
│ python test_rai_integration.py      │
│ (Can close after tests finish)      │
└─────────────────────────────────────┘
```

---

## 📋 Checklist Before Running Tests

- [ ] Opened a NEW terminal for RAI service
- [ ] Navigated to: `rai-toolkit\responsible-ai-moderationlayer\src`
- [ ] Started service: `python app.py`
- [ ] See message: "Running on http://127.0.0.1:5001"
- [ ] Terminal is still open (not closed)

**All checked?** ✅ NOW run tests in a different terminal!

---

## ❓ Common Questions

### Q: Do I need to keep the RAI terminal open?
**A:** YES! The RAI service must keep running. Don't close that terminal.

### Q: Can I run it in the background?
**A:** Yes, you can:
```powershell
# Windows: Start in background
Start-Process powershell -ArgumentList "cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\src; python app.py"
```

### Q: How do I stop the RAI service?
**A:** Press `CTRL+C` in the RAI service terminal.

### Q: Do I need to restart it every time?
**A:** Yes, every time you restart your computer or close the terminal, you need to start it again.

---

## 🎬 Complete Startup Sequence

### For Daily Use (3 terminals):

**Terminal 1: RAI Service** ⭐ START THIS FIRST
```powershell
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\src
python app.py
```
✅ Wait for "Running on http://127.0.0.1:5001"

**Terminal 2: Potato Shield API** ⭐ START SECOND
```powershell
cd c:\Users\satya\Desktop\Potato-Shield\api
python main.py
```
✅ Should show "RAI Toolkit Enabled: True"

**Terminal 3: Frontend** ⭐ START THIRD
```powershell
cd c:\Users\satya\Desktop\Potato-Shield\frontend
npm run dev
```
✅ Open http://localhost:3000

---

## 🚨 TL;DR - Just Do This:

```powershell
# NEW Terminal - keep it open
cd c:\Users\satya\Desktop\Potato-Shield\rai-toolkit\responsible-ai-moderationlayer\src
python app.py

# (DON'T CLOSE THIS TERMINAL!)
```

**Then in your original terminal:**
```powershell
python test_rai_integration.py
```

✅ **Tests will now work!**

---

**Problem Solved?** ✅ Once RAI service is running, everything else will work!
