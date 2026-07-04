# Start Frontend

## ✅ Correct Command

The frontend uses Next.js, so you need to run:

```bash
cd frontend
npm run dev
```

**NOT** `npm dev` - it must be `npm run dev`

## 🚀 Quick Start

### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 2: Start Development Server
```bash
npm run dev
```

### Step 3: Open Browser
The frontend will be available at:
```
http://localhost:3000
```

## 📝 Note

- Frontend runs on port **3000**
- Backend should run on port **8000**
- Make sure backend is running with `USE_DYNAMODB=true` before testing registration

## 🔍 Check if Frontend is Running

You should see output like:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - ready started server on 0.0.0.0:3000
```

## 🐛 If You Get Errors

### "npm: command not found"
- Install Node.js from https://nodejs.org/
- Make sure npm is in your PATH

### "Cannot find module"
- Run: `npm install` in the frontend directory
- This installs all dependencies

### Port 3000 already in use
- Stop other processes on port 3000
- Or change port: `PORT=3001 npm run dev`

