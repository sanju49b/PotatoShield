# Potato Shield - AWS-Ready Backend Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              POTATO SHIELD CLOUD ARCHITECTURE                        │
│                                    (AWS Ready)                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    USER LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐  │
│  │   User (Farmer)  │────────▶│  Next.js Frontend │────────▶│  Chat Interface  │  │
│  │                  │         │  (Vercel/Static)  │         │  Dashboard UI     │  │
│  └──────────────────┘         └──────────────────┘         └──────────────────┘  │
│                                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTPS/REST API
                                        │ SSE (Server-Sent Events)
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 API GATEWAY LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐ │
│  │                        FastAPI Application (api/main.py)                      │ │
│  │                                                                                │ │
│  │  ┌────────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    API Endpoints                                        │  │ │
│  │  │  • POST /auth/register          • POST /auth/login                     │  │ │
│  │  │  • POST /auth/verify-otp         • POST /auth/send-otp                  │  │ │
│  │  │  • POST /chat/stream             • GET  /chat/history                    │  │ │
│  │  │  • POST /fields                  • GET  /fields                         │  │ │
│  │  │  • GET  /health                  • POST /predict                        │  │ │
│  │  └────────────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                                │ │
│  │  ┌────────────────────────────────────────────────────────────────────────┐  │ │
│  │  │              Responsible AI Middleware (RAI)                            │  │ │
│  │  │  • Input Validation (Local Heuristics + LLM Guard)                     │  │ │
│  │  │  • Output Validation (PII Masking + Toxicity Check)                     │  │ │
│  │  │  • Audit Logging (Redacted)                                             │  │ │
│  │  │  • Infosys RAI Toolkit Integration                                      │  │ │
│  │  └────────────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                                │ │
│  │  ┌────────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    CORS Middleware                                      │  │ │
│  │  │                    Security (HTTPBearer)                                │  │ │
│  │  └────────────────────────────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              AGENT ORCHESTRATION LAYER                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐ │
│  │                    LangGraph Workflow (src/graph/workflow.py)                  │ │
│  │                                                                                │ │
│  │  ┌────────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    Router Agent                                         │  │ │
│  │  │  • Routes queries to appropriate agent                                  │  │ │
│  │  │  • Intent classification                                                │  │ │
│  │  └────────────────────────────────────────────────────────────────────────┘  │ │
│  │                            │                                                    │
│  │                            ├─────────────────────────────────────┐             │ │
│  │                            │                                     │             │ │
│  │                            ▼                                     ▼             │ │
│  │  ┌──────────────────────────────┐         ┌──────────────────────────────┐  │ │
│  │  │   Blight Prediction Agent    │         │   General Chat Agent          │  │ │
│  │  │   (Primary Engine)           │         │   • Conversational AI          │  │ │
│  │  │   • Weather-based rules      │         │   • Multi-language support     │  │ │
│  │  │   • Disease risk calculation │         │   • Context-aware responses    │  │ │
│  │  │   • Streaming reports        │         │   • RAG (Tavily Search)        │  │ │
│  │  └──────────────────────────────┘         └──────────────────────────────┘  │ │
│  │            │                                                                    │ │
│  │            │ ML Validation                                                      │ │
│  │            ▼                                                                    │ │
│  │  ┌──────────────────────────────┐                                             │ │
│  │  │   Disease Classifier (ML)    │                                             │ │
│  │  │   • RandomForest Model        │                                             │ │
│  │  │   • Binary Classification    │                                             │ │
│  │  │   • Secondary Validation     │                                             │ │
│  │  │   • Consistency Guarantee     │                                             │ │
│  │  └──────────────────────────────┘                                             │ │
│  │                                                                                │ │
│  │  ┌──────────────────────────────┐         ┌──────────────────────────────┐  │ │
│  │  │   Diagnostic Agent           │         │   Predictive Agent            │  │ │
│  │  │   • Image analysis           │         │   • Future risk forecasting   │  │ │
│  │  │   • Symptom matching         │         │   • Trend analysis             │  │ │
│  │  └──────────────────────────────┘         └──────────────────────────────┘  │ │
│  │                                                                                │ │
│  │  ┌──────────────────────────────┐                                             │ │
│  │  │   Streaming Narrator Agent   │                                             │ │
│  │  │   • Real-time narration      │                                             │ │
│  │  │   • SSE streaming            │                                             │ │
│  │  └──────────────────────────────┘                                             │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 TOOLBOX LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐                │
│  │  Weather Tool    │  │  Tavily Search   │  │  Vision Tool     │                │
│  │  (Open-Meteo API)│  │  (Web Search)    │  │  (Image Analysis)│                │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘                │
│                                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐                │
│  │  Disease Tool    │  │  Report Tool     │  │  Translation     │                │
│  │  (Prediction)    │  │  (PDF Export)    │  │  Helper         │                │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘                │
│                                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              MEMORY & STORAGE LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐ │
│  │                    Memory Management System                                    │ │
│  │                                                                                │ │
│  │  ┌──────────────────────────────┐         ┌──────────────────────────────┐  │ │
│  │  │   Long-Term Memory            │         │   Short-Term Memory          │  │ │
│  │  │   • User profiles             │         │   • Recent conversations     │  │ │
│  │  │   • Conversation history      │         │   • Session context          │  │ │
│  │  │   • Field information         │         │   • In-memory cache          │  │ │
│  │  │   • PII sanitization         │         │   • DynamoDB-backed option   │  │ │
│  │  └──────────────────────────────┘         └──────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐ │
│  │                    Data Storage (AWS Ready)                                   │ │
│  │                                                                                │ │
│  │  ┌──────────────────────────────┐         ┌──────────────────────────────┐  │ │
│  │  │   SQLite (Local Dev)        │         │   DynamoDB (Production)        │  │ │
│  │  │   • users.db                │         │   • Users table                │  │ │
│  │  │   • conversations.db       │         │   • Conversations table       │  │ │
│  │  │   • fields.db              │         │   • Messages table             │  │ │
│  │  │   • PII masked content     │         │   • Fields table               │  │ │
│  │  └──────────────────────────────┘         │   • OTP table                 │  │ │
│  │                                            │   • Encrypted at rest        │  │ │
│  │                                            └──────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            EXTERNAL SERVICES LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐                │
│  │  OpenAI API      │  │  Open-Meteo API  │  │  Tavily API      │                │
│  │  • GPT-4o-mini   │  │  • Weather data  │  │  • Web search    │                │
│  │  • LLM Guard     │  │  • Forecasts     │  │  • RAG retrieval │                │
│  │  • Translation   │  │  • Historical    │  │  • Real-time     │                │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘                │
│                                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐                │
│  │  AWS SES          │  │  Infosys RAI      │  │  AWS Cognito     │                │
│  │  • OTP emails     │  │  Toolkit          │  │  (Future)        │                │
│  │  • Notifications  │  │  • Moderation     │  │  • Auth          │                │
│  │  • Sandbox mode   │  │  • Safety checks  │  │  • User mgmt     │                │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘                │
│                                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            OBSERVABILITY & MONITORING                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐ │
│  │                    Audit & Logging                                            │ │
│  │  • RAI audit events (redacted)                                                │ │
│  │  • API request/response logs                                                   │ │
│  │  • Error tracking                                                              │ │
│  │  • Performance metrics                                                         │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐ │
│  │                    Future: CloudWatch / ELK Stack                              │ │
│  │  • Centralized logging                                                        │ │
│  │  • Metrics dashboard                                                           │ │
│  │  • Alerting                                                                    │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘

```

## Component Details

### 1. **User Layer**
- **Next.js Frontend**: React-based UI deployed on Vercel
- **Chat Interface**: Real-time chat with SSE streaming
- **Dashboard**: Field management, predictions, reports

### 2. **API Gateway Layer**
- **FastAPI Application**: Main API server (`api/main.py`)
- **RAI Middleware**: Input/output validation, PII masking, audit logging
- **Authentication**: JWT-based with OTP verification via AWS SES

### 3. **Agent Orchestration Layer**
- **LangGraph Workflow**: State machine for agent coordination
- **Router Agent**: Routes queries to appropriate agents
- **Blight Prediction Agent**: Primary rule-based prediction engine
- **Disease Classifier (ML)**: Secondary validation using RandomForest
- **General Chat Agent**: Conversational AI with RAG
- **Diagnostic Agent**: Image-based disease diagnosis
- **Predictive Agent**: Future risk forecasting
- **Streaming Narrator**: Real-time narration for reports

### 4. **Toolbox Layer**
- **Weather Tool**: Open-Meteo API integration
- **Tavily Search**: Web search for RAG
- **Vision Tool**: Image analysis capabilities
- **Translation Helper**: Multi-language support

### 5. **Memory & Storage Layer**
- **Long-Term Memory**: User profiles, conversations, fields (SQLite/DynamoDB)
- **Short-Term Memory**: Session context, recent conversations
- **PII Sanitization**: Automatic masking before storage
- **DynamoDB**: Production-ready multi-user storage

### 6. **External Services Layer**
- **OpenAI API**: LLM for chat, translation, safety checks
- **Open-Meteo API**: Weather data and forecasts
- **Tavily API**: Web search and RAG
- **AWS SES**: Email service for OTP
- **Infosys RAI Toolkit**: Responsible AI compliance
- **AWS Cognito**: Future authentication service

### 7. **Observability Layer**
- **Audit Logging**: Redacted logs for compliance
- **Error Tracking**: Exception monitoring
- **Performance Metrics**: API response times, agent execution times

## Data Flow

1. **User Request** → Frontend sends HTTP/SSE request
2. **API Gateway** → FastAPI receives, validates via RAI middleware
3. **Agent Router** → Routes to appropriate agent based on intent
4. **Agent Execution** → Agent uses tools (weather, search, ML model)
5. **Memory Access** → Retrieves/stores user context and history
6. **Response Streaming** → SSE stream back to frontend
7. **Audit Logging** → Redacted events logged for compliance

## Security Features

- ✅ **Input Validation**: Local heuristics + LLM guard
- ✅ **Output Validation**: PII masking, toxicity checks
- ✅ **PII Sanitization**: Automatic masking in storage
- ✅ **Audit Logging**: Redacted logs (no raw PII)
- ✅ **Encryption at Rest**: DynamoDB encryption
- ✅ **OTP Verification**: AWS SES email service
- ✅ **JWT Authentication**: Secure token-based auth

## AWS Deployment Ready

- ✅ **DynamoDB**: Multi-user production storage
- ✅ **AWS SES**: Email service for OTP
- ✅ **Lambda Ready**: Can be containerized for Lambda
- ✅ **ECS/EKS Ready**: Can be deployed as containers
- ✅ **CloudWatch Ready**: Logging infrastructure ready
- ✅ **Cognito Ready**: Can integrate AWS Cognito for auth

## ML Model Integration

- **Disease Classifier**: Trained RandomForest model
- **Training Data**: `Disease with Weather.csv` (4000+ samples)
- **Features**: Temperature, Humidity, Wind Speed, Wind Bearing, Visibility, Pressure
- **Validation**: Secondary engine for prediction consistency
- **Storage**: Model saved as `disease_classifier.pkl`
