# Responsible AI Toolkit Integration Guide

## Overview

This document outlines the integration of the **Infosys Responsible AI Toolkit** into Potato Shield to meet UK-India AIxcelerate 2025-26 evaluation criteria.

**Toolkit Repository:** https://github.com/Infosys/Infosys-Responsible-AI-Toolkit

---

## Why Responsible AI for Potato Shield?

As an **agricultural AI system** providing disease predictions and treatment recommendations to farmers:

### Critical Safety Requirements:
- **Safety & Robustness**: Wrong disease predictions can cause crop loss and farmer hardship
- **Fairness**: Must serve smallholder farmers equally as commercial farms (no regional bias)
- **Transparency**: Farmers need to understand WHY a disease risk is predicted
- **Privacy**: Must protect farmer location and field data (DPDP Act 2023 compliance)
- **Hallucination Prevention**: Cannot provide unverified treatment recommendations
- **Accountability**: Clear audit trail for all AI decisions affecting crops

### Regulatory Alignment:
- **India**: NITI Aayog Responsible AI for All framework
- **UK**: UK AI White Paper principles (safety, transparency, fairness, accountability)
- **Agriculture-Specific**: FAO AI in Agriculture guidelines (Section 10.2 of evaluation criteria)

---

## Infosys RAI Toolkit Modules to Integrate

### 1. **ModerationLayer API** (Priority 1)
**Repository:** `responsible-ai-moderationlayer`

**Features:**
- Comprehensive suite covering Safety, Privacy, Explainability, Fairness, Hallucination
- Regulates content of prompts (user inputs) and responses (AI outputs)

**Use Cases in Potato Shield:**
- ✅ Check user queries for prompt injection attempts
- ✅ Validate AI predictions before sending to farmers
- ✅ Detect hallucinations in disease recommendations
- ✅ Ensure privacy protection in field data

**Integration Points:**
- `api/main.py` - Add as middleware for all `/api/chat` endpoints
- `src/graph/workflow.py` - Add validation layer in workflow nodes
- `src/agents/*` - Validate agent outputs before returning to user

---

### 2. **Hallucination Detection API** (Priority 1)
**Repository:** `responsible-ai-Hallucination`

**Features:**
- Detects and quantifies hallucination in LLM responses
- Critical for RAG scenarios (weather data + AI analysis)

**Use Cases in Potato Shield:**
- ✅ Verify disease predictions are grounded in actual weather data
- ✅ Ensure treatment recommendations are evidence-based
- ✅ Validate fungicide dosages against known safe ranges
- ✅ Cross-check historical outbreak claims with Tavily sources

**Integration Points:**
- `src/agents/blight_prediction_agent.py` - Validate predictions against weather dataset
- `src/agents/diagnostic_agent.py` - Verify disease identification claims
- `src/agents/general_chat_agent.py` - Check factual accuracy of chat responses

---

### 3. **Privacy API** (Priority 1)
**Repository:** `responsible-ai-privacy`

**Features:**
- Detects and anonymizes PII (Personally Identifiable Information)
- Complies with DPDP Act 2023 (India) and UK GDPR

**Use Cases in Potato Shield:**
- ✅ Detect phone numbers, emails, Aadhaar in user messages
- ✅ Anonymize farmer personal data in logs
- ✅ Protect location coordinates from unauthorized access
- ✅ Ensure field data privacy in multi-user scenarios

**Integration Points:**
- `api/main.py` - Scan all user inputs for PII before processing
- `src/memory/long_term_memory.py` - Encrypt sensitive field data
- Audit logs - Anonymize PII in all logs

---

### 4. **Safety API** (Priority 1)
**Repository:** `responsible-ai-safety`

**Features:**
- Detects toxic, profane, and harmful content
- Checks for prompt injection and jailbreak attempts

**Use Cases in Potato Shield:**
- ✅ Block malicious prompt injection attempts
- ✅ Filter toxic language from user inputs
- ✅ Prevent jailbreak attempts to manipulate AI behavior
- ✅ Ensure agricultural advice remains safe and professional

**Integration Points:**
- `api/main.py` - Input validation for all chat endpoints
- `src/agents/router_agent.py` - Safety check before routing
- `src/agents/*` - Output safety validation

---

### 5. **Fairness & Bias API** (Priority 2)
**Repository:** `responsible-ai-fairness`

**Features:**
- Detects bias in LLM prompts and responses
- Bias detection methods: Statistical Parity, Disparate Impact Ratio, Four-Fifths Rule

**Use Cases in Potato Shield:**
- ✅ Ensure predictions are fair across regions (India vs UK)
- ✅ Prevent bias against smallholder farmers
- ✅ Check for language bias (English vs regional languages)
- ✅ Validate resource accessibility (expensive vs affordable solutions)

**Integration Points:**
- `src/agents/blight_prediction_agent.py` - Fairness check for risk predictions
- `src/agents/diagnostic_agent.py` - Bias check for Tavily recommendations
- Demographic analysis - Compare predictions across farm sizes, regions

---

### 6. **Explainability APIs** (Priority 2)
**Repository:** `responsible-ai-llm-explain`

**Features:**
- Thread of Thoughts (ThoT)
- Chain of Thoughts (CoT)
- Graph of Thoughts (GoT)
- Chain of Verification (CoVe)
- Token importance analysis

**Use Cases in Potato Shield:**
- ✅ Explain WHY a disease risk is high/medium/low
- ✅ Show which weather factors contributed most to risk score
- ✅ Provide reasoning chains for treatment recommendations
- ✅ Token-level explanations for critical predictions

**Integration Points:**
- `src/agents/blight_prediction_agent.py` - Add explainability to risk calculations
- Frontend dashboard - Display explanation visualizations
- API responses - Include explanation metadata

---

### 7. **Security API** (Priority 2)
**Repository:** `responsible-ai-security`

**Features:**
- Adversarial attack detection
- Defense mechanisms for ML models
- Prompt injection checks

**Use Cases in Potato Shield:**
- ✅ Protect weather data collection from manipulation
- ✅ Secure prediction models from adversarial inputs
- ✅ Validate API requests for security threats

---

### 8. **Telemetry & Monitoring** (Priority 3)
**Repository:** `responsible-ai-telemetry`

**Features:**
- Elasticsearch integration for RAI metrics
- Kibana dashboards for visualization
- Audit trail logging

**Use Cases in Potato Shield:**
- ✅ Track all RAI checks (safety, privacy, fairness, hallucination)
- ✅ Monitor bias trends across user demographics
- ✅ Generate compliance reports for regulators
- ✅ Create audit dashboard for stakeholders

---

## Installation & Setup Plan

### Step 1: Clone Infosys RAI Toolkit

```bash
# Clone the toolkit repository as a submodule
cd c:\Users\satya\Desktop\Potato-Shield
git clone https://github.com/Infosys/Infosys-Responsible-AI-Toolkit.git rai-toolkit
```

### Step 2: Install Required RAI Modules

Each module has its own `requirements.txt`. We'll install:

```bash
# Install ModerationLayer (comprehensive suite)
cd rai-toolkit/responsible-ai-moderationlayer
pip install -r requirements.txt

# Install Hallucination Detection
cd ../responsible-ai-Hallucination
pip install -r requirements.txt

# Install Privacy API
cd ../responsible-ai-privacy
pip install -r requirements.txt

# Install Safety API
cd ../responsible-ai-safety
pip install -r requirements.txt

# Install Fairness API
cd ../responsible-ai-fairness
pip install -r requirements.txt

# Install Explainability
cd ../responsible-ai-llm-explain
pip install -r requirements.txt
```

### Step 3: Configure RAI Toolkit Endpoints

The toolkit uses microservice architecture. We need to:
1. Run RAI Backend service
2. Configure API endpoints
3. Set up authentication

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Potato Shield Frontend                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Potato Shield API (FastAPI)                     │
│                  + RAI Middleware                            │
└──────────┬─────────────────────────────────────┬────────────┘
           │                                     │
           ▼                                     ▼
┌──────────────────────┐           ┌────────────────────────┐
│  Infosys RAI Toolkit │           │   LangGraph Workflow   │
│  Moderation Layer    │           │   (Agent Orchestration)│
└──────────┬───────────┘           └───────────┬────────────┘
           │                                   │
           ├─→ Safety API                      │
           ├─→ Privacy API                     │
           ├─→ Hallucination API               │
           ├─→ Fairness API                    │
           ├─→ Explainability API              │
           └─→ Telemetry API                   │
                                               ▼
                                    ┌─────────────────────┐
                                    │  RAI Validated      │
                                    │  Disease Prediction │
                                    └─────────────────────┘
```

---

## Key Integration Points

### 1. **Chat Endpoint with RAI Middleware**

```python
# api/main.py

from rai_toolkit.moderationlayer import ModerationAPI

# Initialize RAI Moderation
rai_moderator = ModerationAPI(config={
    "safety_threshold": 0.7,
    "hallucination_threshold": 0.6,
    "privacy_auto_mask": True
})

@app.post("/api/chat")
async def chat_with_rai_protection(request: ChatRequest, user_id: str = Depends(require_verified_user)):
    # 1. RAI Input Validation
    input_check = rai_moderator.check_input(
        text=request.message,
        checks=["safety", "privacy", "prompt_injection"]
    )
    
    if not input_check["is_safe"]:
        return {"error": "Input validation failed", "details": input_check}
    
    # 2. Process with workflow (existing code)
    result = workflow.invoke(state)
    
    # 3. RAI Output Validation
    output_check = rai_moderator.check_output(
        text=result["final_report"],
        source_data=result.get("weather_dataset"),
        checks=["hallucination", "safety", "fairness"]
    )
    
    if not output_check["is_safe"]:
        return {"error": "Output validation failed", "details": output_check}
    
    # 4. Return validated response with RAI metadata
    return {
        "response": output_check["validated_text"],
        "rai_compliance": {
            "safety_score": output_check["safety_score"],
            "hallucination_score": output_check["hallucination_score"],
            "fairness_score": output_check["fairness_score"]
        }
    }
```

### 2. **Blight Prediction with Hallucination Detection**

```python
# src/agents/blight_prediction_agent.py

from rai_toolkit.hallucination import HallucinationAPI

def predict_blight_risk(self, state: AgentState) -> AgentState:
    # ... existing prediction code ...
    
    # Validate prediction against weather dataset
    hallucination_check = HallucinationAPI.verify_response(
        ai_response=result["final_report"],
        ground_truth_data={
            "weather_dataset": weather_dataset,
            "user_profile": state["user_profile"]
        },
        domain="agriculture"
    )
    
    # Add hallucination score to result
    result["rai_validation"] = {
        "hallucination_score": hallucination_check["score"],
        "verified_claims": hallucination_check["verified_claims"],
        "unsupported_claims": hallucination_check["unsupported_claims"]
    }
    
    return state
```

### 3. **Fairness Check for Regional Predictions**

```python
# src/agents/blight_prediction_agent.py

from rai_toolkit.fairness import FairnessAPI

def check_regional_fairness(predictions_by_region: Dict):
    """Compare predictions across India vs UK, Urban vs Rural"""
    
    fairness_check = FairnessAPI.check_disparate_impact(
        predictions=predictions_by_region,
        protected_attributes=["country", "region", "farm_size"],
        metrics=["statistical_parity", "four_fifths_rule"]
    )
    
    return fairness_check
```

---

## Step-by-Step Implementation Plan

### Phase 1: Setup RAI Toolkit (Week 1)

1. ✅ Clone Infosys RAI Toolkit repository
2. ✅ Install core modules (moderationlayer, hallucination, privacy, safety, fairness)
3. ✅ Start RAI Backend service
4. ✅ Configure API endpoints and authentication
5. ✅ Test each module independently

### Phase 2: Input Validation (Week 2)

1. ✅ Integrate Safety API for user input validation
2. ✅ Add Privacy API for PII detection
3. ✅ Implement prompt injection checks
4. ✅ Add middleware to `/api/chat` and `/api/chat/stream` endpoints
5. ✅ Test with malicious inputs

### Phase 3: Output Validation (Week 3)

1. ✅ Integrate Hallucination API for prediction validation
2. ✅ Add Fairness API for bias detection
3. ✅ Validate predictions against weather data
4. ✅ Test across different regions and user types

### Phase 4: Explainability (Week 4)

1. ✅ Integrate Explainability APIs (CoT, ThoT, GoT)
2. ✅ Add explanation layers to disease predictions
3. ✅ Create visual explanations for frontend
4. ✅ Document reasoning chains

### Phase 5: Governance & Monitoring (Week 5)

1. ✅ Set up RAI Telemetry module
2. ✅ Configure Elasticsearch + Kibana
3. ✅ Create compliance dashboard
4. ✅ Implement audit logging
5. ✅ Generate metrics reports

---

## RAI Toolkit Endpoints to Use

### Moderation Layer API

```bash
POST /api/moderation/check-input
POST /api/moderation/check-output
POST /api/moderation/validate-complete
```

### Hallucination API

```bash
POST /api/hallucination/detect
POST /api/hallucination/verify-grounding
```

### Privacy API

```bash
POST /api/privacy/detect-pii
POST /api/privacy/anonymize
```

### Safety API

```bash
POST /api/safety/check-toxicity
POST /api/safety/detect-injection
```

### Fairness API

```bash
POST /api/fairness/check-bias
POST /api/fairness/disparate-impact
```

### Explainability API

```bash
POST /api/explain/chain-of-thought
POST /api/explain/token-importance
```

---

## Configuration File

```yaml
# config/rai_config.yaml

responsible_ai:
  enabled: true
  
  moderation_layer:
    endpoint: "http://localhost:5001"
    api_key: "${RAI_API_KEY}"
    
  safety:
    toxicity_threshold: 0.7
    prompt_injection_threshold: 0.8
    jailbreak_threshold: 0.75
    
  privacy:
    auto_anonymize: true
    pii_types: ["email", "phone", "aadhaar", "address"]
    
  hallucination:
    verification_threshold: 0.6
    require_ground_truth: true
    
  fairness:
    protected_attributes:
      - country
      - region  
      - farm_size
      - language
    disparity_threshold: 0.8  # Four-fifths rule
    
  explainability:
    methods: ["chain_of_thought", "token_importance"]
    min_confidence_for_explanation: 0.5
    
  governance:
    audit_logging: true
    telemetry_enabled: true
    elasticsearch_endpoint: "http://localhost:9200"
```

---

## Compliance Checklist (UK-India AIxcelerate Criteria)

### ✅ Transparency & Explainability
- [ ] RAI Explainability API integrated
- [ ] Chain-of-Thought reasoning for predictions
- [ ] Token importance for weather factors
- [ ] Documentation of data sources

### ✅ Accountability & Governance  
- [ ] RAI Telemetry tracking all decisions
- [ ] Audit logs with immutable records
- [ ] Clear roles and responsibilities documented
- [ ] Grievance redressal mechanism

### ✅ Safety & Robustness
- [ ] RAI Safety API for toxic content
- [ ] Prompt injection detection
- [ ] Adversarial testing completed
- [ ] Continuous monitoring enabled

### ✅ Fairness & Non-Discrimination
- [ ] RAI Fairness API checking bias
- [ ] Disparate impact analysis (India vs UK)
- [ ] Smallholder vs commercial farmer parity
- [ ] Regional language support

### ✅ Privacy & Data Governance
- [ ] RAI Privacy API for PII detection
- [ ] DPDP Act 2023 compliance (India)
- [ ] UK GDPR compliance
- [ ] Data anonymization in logs

### ✅ Human-Centricity
- [ ] Human-in-the-loop for high-risk predictions
- [ ] User feedback mechanism
- [ ] Contestability of AI decisions
- [ ] Farmer well-being prioritized

### ✅ Inclusiveness & Accessibility
- [ ] Multi-region support (India & UK)
- [ ] Smallholder farmer accessibility
- [ ] Regional language considerations
- [ ] Low-resource recommendations

### ✅ Sustainability & Social Impact
- [ ] Low-carbon AI infrastructure
- [ ] Positive social impact on farmers
- [ ] Environmental harm minimization
- [ ] SDG alignment

---

## RAI Metrics Dashboard

The following metrics will be tracked using RAI Telemetry:

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Safety Score | >0.9 | TBD | ⏳ |
| Hallucination Rate | <10% | TBD | ⏳ |
| Privacy Violations | 0 | TBD | ⏳ |
| Fairness (Disparate Impact) | >0.8 | TBD | ⏳ |
| Explainability Coverage | 100% | TBD | ⏳ |
| Prompt Injection Blocks | Track | TBD | ⏳ |

---

## Next Steps

1. **Clone RAI Toolkit**: `git clone https://github.com/Infosys/Infosys-Responsible-AI-Toolkit.git`
2. **Read Documentation**: Review each module's README
3. **Install Dependencies**: Set up Python environments for each module
4. **Start RAI Services**: Run backend services for APIs
5. **Integrate Middleware**: Add RAI checks to Potato Shield API
6. **Test & Validate**: Run comprehensive testing
7. **Deploy Monitoring**: Set up Elasticsearch + Kibana dashboards

---

## References

- **Infosys RAI Toolkit**: https://github.com/Infosys/Infosys-Responsible-AI-Toolkit
- **UK AI White Paper**: DSIT 2023-24
- **NITI Aayog Responsible AI**: https://www.niti.gov.in
- **FAO AI in Agriculture**: Section 10.2 guidelines
- **DPDP Act 2023**: India data protection
- **UK GDPR**: Data protection compliance

---

**Status**: Ready for implementation pending RAI Toolkit setup
**Owner**: Development Team
**Timeline**: 5 weeks (Phase 1-5)
**Priority**: High (Evaluation Criteria Requirement)
