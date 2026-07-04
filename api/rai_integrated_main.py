"""
Potato Shield API with Infosys Responsible AI Toolkit Integration

This file shows how to integrate RAI Toolkit into the existing API.
To enable RAI, set RAI_ENABLED=true in .env and start RAI Backend service.

Official Toolkit: https://github.com/Infosys/Infosys-Responsible-AI-Toolkit
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import RAI middleware
from src.responsible_ai.rai_middleware import get_rai_middleware
from src.responsible_ai.rai_client import get_rai_client

# Import existing Potato Shield components
# (In production, this would replace api/main.py or be merged into it)

# Initialize RAI middleware
rai_middleware = get_rai_middleware()
rai_client = get_rai_client()

print(f"\n{'='*70}")
print("Potato Shield API - Responsible AI Integration")
print(f"{'='*70}")
print(f"RAI Toolkit Enabled: {rai_client.enabled}")
if rai_client.enabled:
    print(f"RAI Backend URL: {rai_client.base_url}")
    print(f"Modules: ModerationLayer, Hallucination, Privacy, Safety, Fairness, Explainability")
else:
    print("⚠️  RAI Toolkit is DISABLED")
    print("   To enable: Set RAI_ENABLED=true in .env and start RAI Backend")
print(f"{'='*70}\n")


"""
INTEGRATION EXAMPLE 1: Chat Endpoint with Full RAI Protection

This shows how to wrap the existing /api/chat endpoint with RAI validation.
"""

async def chat_with_rai_protection(
    message: str,
    conversation_id: str,
    user_id: str,
    workflow  # Your existing workflow instance
):
    """
    Enhanced chat endpoint with Infosys RAI Toolkit validation.
    
    RAI Checks Applied:
    1. Input Validation (Safety, Privacy, Prompt Injection)
    2. Output Validation (Hallucination, Safety, Fairness)
    3. Explainability (for high-risk predictions)
    4. Audit Logging (all decisions tracked)
    
    Args:
        message: User's message
        conversation_id: Conversation ID
        user_id: User ID
        workflow: LangGraph workflow instance
        
    Returns:
        Dict with validated response + RAI metadata
    """
    
    # STEP 1: RAI Input Validation
    print("[RAI] Validating user input...")
    input_validation = await rai_middleware.validate_user_input(
        user_input=message,
        user_id=user_id,
        session_id=conversation_id
    )
    
    # Block unsafe inputs
    if not input_validation["is_safe"]:
        print(f"[RAI] ❌ Input validation failed: {input_validation['violations']}")
        return {
            "error": "Input validation failed",
            "reason": "Your message contains content that violates safety or privacy guidelines",
            "violations": input_validation["violations"],
            "rai_metadata": input_validation["rai_metadata"]
        }
    
    # Use sanitized input (PII anonymized)
    sanitized_message = input_validation["sanitized_input"]
    if sanitized_message != message:
        print(f"[RAI] ℹ️  PII detected and anonymized")
    
    print(f"[RAI] ✅ Input validation passed")
    
    # STEP 2: Process with existing Potato Shield workflow
    print("[WORKFLOW] Processing query...")
    
    # ... your existing workflow code here ...
    # state = create_state(sanitized_message, user_id, conversation_id)
    # result = workflow.invoke(state)
    
    # For this example, we'll use placeholder result
    result = {
        "final_report": "Based on weather analysis, Late Blight risk is HIGH (85%). Immediate fungicide application recommended.",
        "blight_prediction": {
            "late_blight_risk": {
                "risk_level": "high",
                "risk_percentage": 85
            }
        },
        "weather_dataset": {
            "location": {"city": "Hyderabad", "country": "India"},
            "daily_weather": {"temperature_2m_mean": [22.5]}
        }
    }
    
    # STEP 3: RAI Output Validation
    print("[RAI] Validating AI output...")
    output_validation = await rai_middleware.validate_ai_output(
        ai_output=result["final_report"],
        source_data={"weather_dataset": result.get("weather_dataset")},
        prediction_data=result.get("blight_prediction"),
        user_context={"user_id": user_id}
    )
    
    if not output_validation["is_safe"]:
        print(f"[RAI] ❌ Output validation failed")
        # Return safe fallback response
        return {
            "response": output_validation["validated_output"],
            "rai_validation_failed": True,
            "rai_checks": output_validation["rai_checks"]
        }
    
    print(f"[RAI] ✅ Output validation passed")
    
    # STEP 4: Add Explainability (for high-risk predictions)
    explanation = None
    if result.get("blight_prediction", {}).get("late_blight_risk", {}).get("risk_level") == "high":
        print("[RAI] Generating explanation (Chain of Thought)...")
        explanation = rai_middleware.generate_explanation(
            prediction=result.get("blight_prediction"),
            method="chain_of_thought"
        )
    
    # STEP 5: Return validated response with RAI metadata
    return {
        "response": output_validation["validated_output"],
        "blight_prediction": result.get("blight_prediction"),
        "weather_data": result.get("weather_dataset"),
        
        # RAI Compliance Metadata
        "rai_compliance": {
            "input_validation": {
                "safety_score": input_validation["rai_metadata"]["safety_score"],
                "privacy_risk": input_validation["rai_metadata"]["privacy_risk"],
                "violations": input_validation["violations"]
            },
            "output_validation": {
                "hallucination_score": output_validation["rai_checks"].get("hallucination", {}).get("hallucination_score", 0.0),
                "safety_score": output_validation["rai_checks"].get("safety", {}).get("safety_score", 1.0),
                "fairness_metadata": output_validation["rai_checks"].get("fairness_metadata", {})
            },
            "explainability": explanation,
            "compliance_status": "validated"
        }
    }


"""
INTEGRATION EXAMPLE 2: Blight Prediction with Hallucination Detection

Shows how to add RAI validation to the blight prediction agent.
"""

def predict_blight_with_rai_validation(
    weather_dataset: dict,
    user_profile: dict,
    prediction_result: dict
) -> dict:
    """
    Add RAI Hallucination Detection to blight predictions.
    
    Validates that:
    - Risk percentages match weather data
    - Temperature claims are accurate
    - Fungicide recommendations are evidence-based
    - Historical outbreak claims are verifiable
    """
    
    # Get prediction result from existing agent
    final_report = prediction_result.get("final_report", "")
    
    # RAI Hallucination Check
    hallucination_result = rai_client.detect_hallucination(
        ai_response=final_report,
        ground_truth={
            "weather_dataset": weather_dataset,
            "user_profile": user_profile,
            "blight_prediction": prediction_result
        },
        domain="agriculture"
    )
    
    # Add RAI validation to result
    prediction_result["rai_validation"] = {
        "hallucination_detected": hallucination_result.get("hallucination_detected", False),
        "hallucination_score": hallucination_result.get("hallucination_score", 0.0),
        "factual_errors": hallucination_result.get("factual_errors", []),
        "verified_statements": hallucination_result.get("verified_statements", []),
        "confidence": hallucination_result.get("confidence", "medium")
    }
    
    # If high hallucination, flag for human review
    if hallucination_result.get("hallucination_score", 0.0) > 0.7:
        prediction_result["requires_human_review"] = True
        prediction_result["rai_alert"] = "High hallucination score detected. Please verify weather data accuracy."
        print(f"[RAI] ⚠️  HIGH HALLUCINATION DETECTED ({hallucination_result['hallucination_score']:.2f})")
        print(f"[RAI] Factual Errors: {hallucination_result.get('factual_errors', [])}")
    
    return prediction_result


"""
INTEGRATION EXAMPLE 3: Fairness Check Across Regions

Shows how to monitor fairness across different farmer demographics.
"""

def analyze_prediction_fairness(all_predictions: list):
    """
    Periodic fairness analysis across user demographics.
    
    Run this weekly to ensure equitable service delivery.
    """
    
    # Group predictions by demographics
    demographic_slices = {
        "india_smallholder": [p for p in all_predictions if p.get("country") == "India" and p.get("farm_size") == "small"],
        "india_commercial": [p for p in all_predictions if p.get("country") == "India" and p.get("farm_size") == "large"],
        "uk_smallholder": [p for p in all_predictions if p.get("country") == "UK" and p.get("farm_size") == "small"],
        "uk_commercial": [p for p in all_predictions if p.get("country") == "UK" and p.get("farm_size") == "large"],
    }
    
    # RAI Fairness Check
    fairness_result = rai_client.check_fairness(
        predictions=all_predictions,
        demographic_slices=demographic_slices,
        protected_attributes=["country", "region", "farm_size"]
    )
    
    # Check four-fifths rule
    if fairness_result.get("disparate_impact_ratio", 1.0) < 0.8:
        print(f"[RAI] ⚠️  FAIRNESS VIOLATION DETECTED")
        print(f"[RAI] Disparate Impact Ratio: {fairness_result['disparate_impact_ratio']:.2f}")
        print(f"[RAI] This violates the four-fifths rule (should be >= 0.8)")
        print(f"[RAI] Some demographic groups may be receiving biased predictions")
        
        # Trigger fairness review
        alert_governance_team(fairness_result)
    
    return fairness_result


"""
USAGE INSTRUCTIONS:

1. Install RAI Toolkit:
   ```
   ./setup_rai_toolkit.bat  # Windows
   ./setup_rai_toolkit.sh   # Linux/Mac
   ```

2. Start RAI Backend:
   ```
   cd rai-toolkit/responsible-ai-backend
   python app.py
   ```

3. Configure .env:
   ```
   RAI_ENABLED=true
   RAI_API_KEY=your_api_key
   RAI_BACKEND_URL=http://localhost:5001
   ```

4. Test integration:
   ```
   python test_rai_integration.py
   ```

5. Use in your API:
   ```python
   from src.responsible_ai import get_rai_middleware
   
   rai = get_rai_middleware()
   
   # Validate input
   input_check = await rai.validate_user_input(user_message)
   
   # Validate output
   output_check = await rai.validate_ai_output(ai_response, source_data)
   ```
"""
