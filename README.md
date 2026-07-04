# Potato Shield - AI-Powered Potato Disease Diagnosis System

An advanced AI system for potato disease diagnosis and crop management with a stunning modern frontend.

## Features

### Backend (FastAPI)
- ✅ User Authentication (Register/Login)
- ✅ Short-term Memory (Conversation History)
- ✅ Long-term Memory (User Profiles, Fields, Disease History)
- ✅ RESTful API with CORS support
- ✅ SQLite database for persistent storage

### Frontend (Next.js)
- 🥔 **3D Potato Animation** - Interactive 3D potato field using React Three Fiber
- 🤖 **Robotic Text Styling** - Pixelated, futuristic typography with orange glow effects
- 🔐 **Authentication Pages** - Beautiful login and registration
- 💾 **Memory Visualization** - View and manage both short-term and long-term memory
- 🎨 **Modern UI** - Black background with orange accents, smooth animations
- 📱 **Responsive Design** - Works on all devices

## Project Structure

```
Potato-Shield/
├── api/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   └── requirements.txt   # Python dependencies
├── frontend/              # Next.js frontend
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   └── lib/              # Utilities and API client
├── src/                  # Core application code
│   ├── agents/          # AI agents (diagnostic, etc.)
│   ├── memory/          # Memory systems
│   ├── models/          # Data models
│   └── tools/           # Utility tools
└── database/            # Database schema
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the API directory:
```bash
cd api
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Make sure the database directory exists:
```bash
mkdir -p ../database
```

5. Run the API server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (requires auth)

### Memory
- `GET /api/memory/short-term` - Get short-term memory (requires auth)
- `POST /api/memory/short-term` - Add message to short-term memory (requires auth)
- `DELETE /api/memory/short-term` - Clear short-term memory (requires auth)
- `GET /api/memory/long-term` - Get long-term memory (requires auth)

### Health
- `GET /api/health` - Health check

## Deployment

### Frontend (Vercel)

1. Push your code to GitHub
2. Import your repository in [Vercel](https://vercel.com)
3. Set environment variable:
   - `NEXT_PUBLIC_API_URL` - Your backend API URL
4. Deploy!

### Backend

The backend can be deployed to:
- **Railway** - Easy Python deployment
- **Render** - Free tier available
- **Heroku** - Traditional platform
- **AWS/GCP/Azure** - Cloud platforms

Make sure to:
- Set proper CORS origins
- Use environment variables for sensitive data
- Set up a production database (PostgreSQL recommended)

## Testing the Application

1. **Register a new user:**
   - Go to `/register`
   - Create an account with username and password

2. **Login:**
   - Go to `/login`
   - Enter your credentials

3. **View Dashboard:**
   - See your account stats and fields
   - View the 3D potato animation

4. **Manage Memory:**
   - Go to `/memory`
   - View short-term memory (conversation history)
   - View long-term memory (user profile, fields, disease history)
   - Add messages to test short-term memory

## Design Features

- **3D Potato Animation**: Multiple animated potatoes floating in a field
- **Robotic Text**: Orbitron font with glitch effects and orange glow
- **Dark Theme**: Pure black background (#000000) with orange accents (#FF6B35)
- **Smooth Animations**: Framer Motion for page transitions
- **Modern UI**: Clean, futuristic design inspired by the reference image

## Development

### Backend Development
- The API uses FastAPI with automatic OpenAPI documentation
- Access API docs at `http://localhost:8000/docs`
- Memory systems are modular and can be extended

### Frontend Development
- Uses Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- React Three Fiber for 3D graphics

## Notes

- The diagnostic agent code exists but is not fully implemented (as mentioned by user)
- The frontend is ready for testing memory systems and authentication
- Database is automatically initialized on first run
- Short-term memory is in-memory (resets on server restart)
- Long-term memory persists in SQLite database

## License

This project is part of the Potato Shield AI system.

