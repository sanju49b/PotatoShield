# Potato Shield API

FastAPI backend for the Potato Shield application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user (Bearer token required)

### Memory
- `GET /api/memory/short-term` - Get conversation history
- `POST /api/memory/short-term` - Add message to conversation
- `DELETE /api/memory/short-term` - Clear conversation history
- `GET /api/memory/long-term` - Get user profile and fields

## Authentication

All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <token>
```

Tokens are obtained from the `/api/auth/login` endpoint.

## Database

The database is automatically created at `database/potato_care.db` on first run.

## CORS

CORS is enabled for all origins. In production, update the `allow_origins` in `main.py` to your frontend URL.

