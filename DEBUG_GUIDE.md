# How to Check Console Logs for Debugging

## Browser Console (Frontend Logs)

### Chrome/Edge/Brave:
1. **Press `F12`** or **`Ctrl+Shift+I`** (Windows/Linux) / **`Cmd+Option+I`** (Mac)
2. Click on the **"Console"** tab
3. You should see logs like:
   ```
   [FRONTEND] data_collection_progress event received: {...}
   [FRONTEND] Updated assistant content, length: 123
   ```

### Firefox:
1. **Press `F12`** or **`Ctrl+Shift+K`** (Windows/Linux) / **`Cmd+Option+K`** (Mac)
2. The Console tab should open automatically
3. Look for the same `[FRONTEND]` logs

### Safari:
1. Enable Developer menu first:
   - Go to Safari → Preferences → Advanced
   - Check "Show Develop menu in menu bar"
2. Then press **`Cmd+Option+C`** to open the console

---

## Backend/Terminal Console (Server Logs)

### If running with Python directly:
```bash
# In your terminal where you ran:
python api/main.py
# or
uvicorn api.main:app --reload
```

You should see logs like:
```
[STREAMING] Calling predictive agent streaming method...
[STREAMING DEBUG] Event #1: type=data_collection_progress, keys=['type', 'message', 'stage']
[STREAMING] Yielding data_collection_progress: Getting coordinates for...
[STREAMING] Event JSON: {"type":"data_collection_progress","message":"Getting coordinates...
```

### If running as a service:
- Check your service logs (systemd, PM2, Docker, etc.)

---

## What to Look For

### ✅ Good Signs:
- Frontend: `[FRONTEND] data_collection_progress event received` appears
- Backend: `[STREAMING] Yielding data_collection_progress` appears
- Messages appear in the chat UI in real-time

### ❌ Problem Signs:
- Frontend: No `[FRONTEND]` logs = events not reaching frontend
- Backend: No `[STREAMING]` logs = events not being generated
- Errors in red = something is broken

---

## Quick Test Steps

1. **Open Browser Console** (F12 → Console tab)
2. **Clear the console** (click the 🚫 icon or press `Ctrl+L`)
3. **Send a prediction request** in the chat
4. **Watch for logs**:
   - You should see `[FRONTEND] data_collection_progress event received` logs
   - Each log shows the message being received
5. **Check Backend Terminal**:
   - You should see `[STREAMING] Yielding data_collection_progress` logs
   - Each log shows what's being sent

---

## Filtering Logs

### In Browser Console:
- Type `[FRONTEND]` in the filter box to see only frontend logs
- Type `data_collection_progress` to see only those events

### In Terminal:
- Use `grep` to filter: `python api/main.py | grep "STREAMING"`
- Or redirect to a file: `python api/main.py > logs.txt 2>&1`

---

## Common Issues

### "No logs in browser console"
- Check if console is open before sending request
- Check if there are any errors blocking execution
- Verify the frontend code is deployed/refreshed

### "No logs in backend terminal"
- Check if the server is actually running
- Check if the request is reaching the `/api/chat/stream` endpoint
- Look for any Python errors/exceptions

### "Logs appear but UI doesn't update"
- Check React DevTools to see if state is updating
- Check Network tab to see if SSE events are arriving
- Look for JavaScript errors in console

