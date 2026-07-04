# Streaming Debug Checklist

## Backend Issues to Check

### ✅ SSE Format
- [x] Events use `data: {json}\n\n` format
- [x] Double newline (`\n\n`) after each event
- [x] Proper JSON encoding

### ✅ Headers
- [x] `Content-Type: text/event-stream; charset=utf-8`
- [x] `Cache-Control: no-cache, no-store, must-revalidate`
- [x] `Connection: keep-alive`
- [x] `X-Accel-Buffering: no`

### ⚠️ Potential Issues

1. **FastAPI/Uvicorn Buffering**
   - FastAPI might buffer events before sending
   - Solution: Use `StreamingResponse` with proper headers
   - Check: Events appear in logs but not in frontend

2. **Data Collection Progress**
   - Currently collects all messages first, then yields
   - This means messages appear all at once, not in real-time
   - Solution: This is expected for serverless compatibility

3. **Event Timing**
   - Events might be sent too fast
   - Frontend might not process them fast enough
   - Solution: Added 1ms delay between events

## Frontend Issues to Check

### ✅ Stream Reading
- [x] Uses `response.body.getReader()`
- [x] Properly decodes chunks
- [x] Handles `data: ` prefix
- [x] Parses JSON correctly

### ⚠️ Potential Issues

1. **Browser Buffering**
   - Browser might buffer SSE events
   - Check: Network tab shows events arriving
   - Solution: Headers should prevent buffering

2. **Event Processing**
   - Events might be received but not displayed
   - Check: Console logs show events received
   - Solution: Verify event handlers are working

3. **React State Updates**
   - State updates might be batched
   - Check: UI updates when events arrive
   - Solution: Force immediate updates

## How to Debug

### Step 1: Check Backend Logs
```
[STREAMING] Yielding data_collection_progress: ...
[STREAMING] Event JSON: ...
```
If you see these, backend is generating events.

### Step 2: Check Frontend Console
```
[FRONTEND API] Starting SSE stream request...
[FRONTEND API] Stream response received, status: 200
[FRONTEND API] Event #1 - data_collection_progress: ...
```
If you see these, frontend is receiving events.

### Step 3: Check Network Tab
1. Open browser DevTools → Network tab
2. Find the `/api/chat/stream` request
3. Click on it → Response tab
4. Check if events are appearing in real-time
5. Check if `Content-Type` is `text/event-stream`

### Step 4: Check Event Handlers
1. Open browser DevTools → Console tab
2. Look for `[FRONTEND] data_collection_progress event received`
3. If you see this, events are being processed
4. If not, events are being received but not handled

## Common Problems

### Problem 1: Events Not Appearing in Frontend
**Symptoms**: Backend logs show events, but frontend doesn't show them
**Cause**: Events might be buffered or not being processed
**Solution**: 
- Check Network tab to see if events are arriving
- Check console for errors
- Verify event handlers are registered

### Problem 2: Events Appear All at Once
**Symptoms**: All progress messages appear simultaneously
**Cause**: Data collection collects all messages first (serverless compatibility)
**Solution**: This is expected behavior. For real-time streaming, would need WebSockets.

### Problem 3: Events Missing `data:` Prefix
**Symptoms**: Frontend can't parse events
**Cause**: Backend not formatting correctly
**Solution**: Verify backend uses `f"data: {json}\n\n"` format

### Problem 4: CORS Issues
**Symptoms**: Stream request fails
**Cause**: CORS headers not set correctly
**Solution**: Verify CORS headers in StreamingResponse

## Testing Commands

### Test Backend
```bash
# Start backend
cd api
python main.py

# In another terminal, test SSE endpoint
curl -N -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}' \
  http://localhost:8000/api/chat/stream
```

### Test Frontend
1. Open browser console (F12)
2. Send a prediction request
3. Watch for console logs:
   - `[FRONTEND API] Starting SSE stream request...`
   - `[FRONTEND API] Event #X - data_collection_progress: ...`
   - `[FRONTEND] data_collection_progress event received`

## Next Steps

If events still don't appear:
1. Check Network tab for the actual response
2. Check if events are being sent but not processed
3. Check if there are any JavaScript errors
4. Verify the event type is `data_collection_progress`
5. Check if the message content is being updated in React state

