# src/agents/predictive_agent.py
from typing import Dict, Generator, Any
from src.state.agent_state import AgentState
from src.agents.blight_prediction_agent import BlightPredictionAgent

class PredictiveAgent:
    """
    Weather-based disease prediction agent.
    Uses BlightPredictionAgent to predict disease risk for potato crops.
    Integrates comprehensive weather analysis with climate-specific configurations.
    """
    
    def __init__(self):
        """Initialize the predictive agent with blight prediction capabilities."""
        self.blight_agent = BlightPredictionAgent()
    
    def predict(self, state: AgentState) -> Dict:
        """
        Predict disease risk based on weather conditions and field data.
        Uses the enhanced BlightPredictionAgent with all features:
        - Automatic user data extraction (location, sowing date)
        - Climate-specific configurations (India/UK)
        - Hutton Criteria checking (UK)
        - Comprehensive weather analysis
        
        Args:
            state: AgentState containing user_profile with fields
            
        Returns:
            Dict with prediction, weather_data, and report
        """
        # Use BlightPredictionAgent to get comprehensive prediction
        updated_state = self.blight_agent.predict_blight_risk(state)
        
        # Extract results from updated state
        blight_prediction = updated_state.get("blight_prediction", {})
        weather_dataset = updated_state.get("weather_dataset", {})
        final_report = updated_state.get("final_report", "")
        
        # Return in format expected by workflow
        return {
            "prediction": blight_prediction,
            "weather_data": weather_dataset,
            "report": final_report
        }
    
    def predict_streaming(self, state: AgentState) -> Generator[Dict[str, Any], None, None]:
        """
        Stream disease risk prediction with progress updates.
        Uses BlightPredictionAgent's streaming method.
        
        Args:
            state: AgentState containing user_profile with fields
            
        Yields:
            Dict with type, message, stage, and data
        """
        # Use BlightPredictionAgent's streaming method
        for update in self.blight_agent.predict_blight_risk_streaming(state):
            yield update
