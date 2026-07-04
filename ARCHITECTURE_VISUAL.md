# Potato Shield - AWS Architecture Diagram

## System Architecture (Visual Layout)

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                        POTATO SHIELD CLOUD ARCHITECTURE                          ║
║                              (AWS Production Ready)                               ║
╚═══════════════════════════════════════════════════════════════════════════════════╝


┌───────────────────────────────────────────────────────────────────────────────────┐
│                                    USER LAYER                                     │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│                    ┌──────────────┐                                             │
│                    │ User (Farmer)│                                             │
│                    └──────┬───────┘                                             │
│                           │                                                       │
│                           │ HTTPS / WebSocket                                    │
│                           ▼                                                       │
│              ┌────────────────────────────┐                                      │
│              │   Next.js Frontend App     │                                      │
│              │   • Chat Interface          │                                      │
│              │   • Dashboard               │                                      │
│              │   • Field Management        │                                      │
│              │   • Reports & Analytics     │                                      │
│              └────────────┬───────────────┘                                     │
│                           │                                                       │
└───────────────────────────┼───────────────────────────────────────────────────────┘
                             │
                             │ REST API / SSE
                             │
                             ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY LAYER                                    │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│              ┌─────────────────────────────────────────────────┐                │
│              │         FastAPI Application Server                │                │
│              │         (api/main.py)                            │                │
│              ├─────────────────────────────────────────────────┤                │
│              │                                                 │                │
│              │  ┌───────────────────────────────────────────┐  │                │
│              │  │  API Endpoints                            │  │                │
│              │  │  • /auth/register                        │  │                │
│              │  │  • /auth/login                           │  │                │
│              │  │  • /auth/verify-otp                      │  │                │
│              │  │  • /chat/stream                          │  │                │
│              │  │  • /fields                                │  │                │
│              │  │  • /predict                              │  │                │
│              │  └───────────────────────────────────────────┘  │                │
│              │                                                 │                │
│              │  ┌───────────────────────────────────────────┐  │                │
│              │  │  RAI Middleware                           │  │                │
│              │  │  • Input Validation                       │  │                │
│              │  │  • Output Sanitization                    │  │                │
│              │  │  • PII Masking                           │  │                │
│              │  │  • Audit Logging                        │  │                │
│              │  └───────────────────────────────────────────┘  │                │
│              │                                                 │                │
│              │  ┌───────────────────────────────────────────┐  │                │
│              │  │  Security Layer                           │  │                │
│              │  │  • CORS Middleware                        │  │                │
│              │  │  • JWT Authentication                    │  │                │
│              │  │  • HTTPBearer Security                  │  │                │
│              │  └───────────────────────────────────────────┘  │                │
│              └─────────────────────────────────────────────────┘                │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
                             │
                             │
                             ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                         AGENT ORCHESTRATION LAYER                                 │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│              ┌─────────────────────────────────────────────────┐                │
│              │      LangGraph Workflow Engine                   │                │
│              │      (src/graph/workflow.py)                     │                │
│              ├─────────────────────────────────────────────────┤                │
│              │                                                 │                │
│              │         ┌──────────────────────┐                │                │
│              │         │   Router Agent       │                │
│              │         │   Intent Routing     │                │
│              │         └───────────┬───────────┘                │                │
│              │                   │                              │                │
│              │    ┌──────────────┼──────────────┐             │                │
│              │    │              │              │             │                │
│              │    ▼              ▼              ▼             │                │
│              │  ┌──────────┐ ┌──────────┐ ┌──────────┐     │                │
│              │  │  Blight  │ │  General │ │Diagnostic│     │                │
│              │  │Prediction│ │   Chat   │ │  Agent   │     │                │
│              │  │  Agent   │ │  Agent   │ │          │     │                │
│              │  └────┬─────┘ └──────────┘ └──────────┘     │                │
│              │       │                                        │                │
│              │       │ ML Validation                          │                │
│              │       ▼                                        │                │
│              │  ┌──────────────────────┐                     │                │
│              │  │ Disease Classifier   │                     │                │
│              │  │ (RandomForest ML)    │                     │                │
│              │  │ • Binary Classifier  │                     │                │
│              │  │ • Consistency Check │                     │                │
│              │  └──────────────────────┘                     │                │
│              │                                                 │                │
│              │  ┌──────────┐  ┌──────────┐                    │                │
│              │  │Predictive│  │Streaming │                    │                │
│              │  │  Agent   │  │ Narrator │                    │                │
│              │  └──────────┘  └──────────┘                    │                │
│              └─────────────────────────────────────────────────┘                │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
                             │
                             │ Tool Calls
                             │
                             ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                                 TOOLBOX LAYER                                     │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Weather    │  │    Tavily    │  │    Vision     │  │   Disease     │       │
│  │    Tool      │  │   Search     │  │    Tool      │  │    Tool       │       │
│  │              │  │              │  │              │  │               │       │
│  │ Open-Meteo   │  │ Web Search   │  │ Image       │  │ Prediction    │       │
│  │ API          │  │ RAG          │  │ Analysis    │  │ Engine        │       │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                                                   │
│  ┌──────────────┐  ┌──────────────┐                                             │
│  │   Report     │  │ Translation  │                                             │
│  │   Tool       │  │   Helper     │                                             │
│  │              │  │              │                                             │
│  │ PDF Export   │  │ Multi-lang   │                                             │
│  └──────────────┘  └──────────────┘                                             │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
                             │
                             │ Data Access
                             │
                             ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                            MEMORY & STORAGE LAYER                                 │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                        Memory Management                                   │ │
│  │                                                                             │ │
│  │  ┌──────────────────────┐         ┌──────────────────────┐               │ │
│  │  │  Long-Term Memory    │         │  Short-Term Memory   │               │ │
│  │  │                      │         │                      │               │ │
│  │  │ • User Profiles      │         │ • Session Context    │               │ │
│  │  │ • Conversations      │         │ • Recent Messages    │               │ │
│  │  │ • Field Data         │         │ • In-Memory Cache    │               │ │
│  │  │ • PII Sanitized      │         │ • DynamoDB Option   │               │ │
│  │  └──────────────────────┘         └──────────────────────┘               │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                        Data Storage Backends                               │ │
│  │                                                                             │ │
│  │  ┌──────────────────────┐         ┌──────────────────────┐               │ │
│  │  │   SQLite (Local)     │         │   DynamoDB (AWS)     │               │ │
│  │  │                      │         │                      │               │ │
│  │  │ • users.db          │         │ • Users Table        │               │ │
│  │  │ • conversations.db   │         │ • Conversations      │               │ │
│  │  │ • fields.db         │         │ • Messages           │               │ │
│  │  │ • PII Masked        │         │ • Fields             │               │ │
│  │  │                     │         │ • OTP Storage        │               │ │
│  │  │                     │         │ • Encrypted at Rest  │               │ │
│  │  └──────────────────────┘         └──────────────────────┘               │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
                             │
                             │ External API Calls
                             │
                             ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES LAYER                                │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   OpenAI     │  │  Open-Meteo  │  │    Tavily    │  │   AWS SES    │       │
│  │              │  │              │  │              │  │              │       │
│  │ GPT-4o-mini  │  │ Weather Data │  │ Web Search   │  │ OTP Emails   │       │
│  │ LLM Guard    │  │ Forecasts    │  │ RAG          │  │ Notifications │       │
│  │ Translation  │  │ Historical   │  │ Real-time    │  │ Sandbox Mode │       │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                          │
│  │ Infosys RAI  │  │ AWS Cognito  │  │  CloudWatch  │                          │
│  │   Toolkit    │  │   (Future)   │  │   (Future)    │                          │
│  │              │  │              │  │              │                          │
│  │ Moderation   │  │ Auth Service  │  │ Logging      │                          │
│  │ Safety       │  │ User Mgmt    │  │ Metrics      │                          │
│  │ Compliance   │  │              │  │ Monitoring   │                          │
│  └──────────────┘  └──────────────┘  └──────────────┘                          │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
                             │
                             │
                             ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                        OBSERVABILITY & MONITORING                                │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                    Audit & Logging System                                  │ │
│  │                                                                             │ │
│  │  • RAI Audit Events (Redacted)                                             │ │
│  │  • API Request/Response Logs                                               │ │
│  │  • Error Tracking & Alerts                                                  │ │
│  │  • Performance Metrics                                                     │ │
│  │  • User Activity Logs                                                       │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘

```

## Key Components Summary

### **Frontend (Next.js)**
- Chat interface with real-time streaming
- Dashboard for field management
- Multi-language support
- Report visualization

### **Backend (FastAPI)**
- RESTful API endpoints
- Server-Sent Events (SSE) for streaming
- JWT authentication
- OTP verification via AWS SES

### **AI Agents**
- **Router Agent**: Routes user queries
- **Blight Prediction Agent**: Primary prediction engine
- **Disease Classifier**: ML-based secondary validation
- **General Chat Agent**: Conversational AI with RAG
- **Diagnostic Agent**: Image-based diagnosis
- **Predictive Agent**: Future risk forecasting

### **Tools & Services**
- Weather Tool (Open-Meteo)
- Tavily Search (Web RAG)
- Vision Tool (Image analysis)
- Translation Helper (Multi-language)

### **Storage**
- **SQLite**: Local development
- **DynamoDB**: Production (AWS)
- PII sanitization before storage
- Encrypted at rest (DynamoDB)

### **External APIs**
- OpenAI (LLM, translation, safety)
- Open-Meteo (Weather data)
- Tavily (Web search)
- AWS SES (Email service)
- Infosys RAI Toolkit (Compliance)

### **Security & Compliance**
- Input/Output validation
- PII masking
- Audit logging (redacted)
- Responsible AI compliance
- JWT authentication

## AWS Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AWS Cloud Region                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐              │
│  │   Vercel     │      │  ECS/Lambda  │      │   DynamoDB    │              │
│  │  (Frontend)  │─────▶│  (Backend)   │─────▶│  (Storage)   │              │
│  └──────────────┘      └──────────────┘      └──────────────┘              │
│                              │                                                │
│                              ├──────────────┐                                 │
│                              │              │                                 │
│                              ▼              ▼                                 │
│                       ┌──────────────┐  ┌──────────────┐                      │
│                       │   AWS SES    │  │  CloudWatch  │                      │
│                       │  (Email)     │  │  (Logging)   │                      │
│                       └──────────────┘  └──────────────┘                      │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Example: Blight Prediction

1. **User** → Sends query via Frontend
2. **API Gateway** → Validates input via RAI middleware
3. **Router Agent** → Routes to Blight Prediction Agent
4. **Blight Agent** → Calls Weather Tool (Open-Meteo)
5. **Weather Tool** → Returns weather data
6. **Blight Agent** → Calculates risk using rules
7. **ML Classifier** → Validates prediction consistency
8. **Memory** → Stores conversation (PII sanitized)
9. **Streaming** → SSE stream to Frontend
10. **Audit** → Logs redacted event

## Technology Stack

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python, LangGraph, LangChain
- **AI/ML**: OpenAI GPT-4o-mini, scikit-learn, RandomForest
- **Storage**: SQLite (dev), DynamoDB (prod)
- **External**: Open-Meteo, Tavily, AWS SES
- **Security**: RAI Toolkit, JWT, PII masking
- **Deployment**: Vercel (frontend), AWS ECS/Lambda (backend)
