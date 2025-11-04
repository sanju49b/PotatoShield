# src/agents/router_agent.py
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from typing import Literal, List, Dict, Optional
from src.state.agent_state import AgentState

class RouterAgent:
    """
    Complex reasoning agent that analyzes user input and determines
    which specialized agent should handle the request.
    """
    
    def __init__(self):
        # Use GPT-4 for complex reasoning
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    
    def check_required_data(self, state: AgentState) -> Dict:
        """
        Check if required data exists before routing.
        Returns dict with missing_data list and whether to proceed.
        """
        user_profile = state["user_profile"]
        input_type = state["input_type"]
        
        missing = []
        
        # Check for fields data
        fields = user_profile.get('fields', [])
        if not fields:
            missing.extend(['location', 'sowing_date'])
        else:
            # Check if current field has complete data
            current_field = fields[0] if fields else {}
            if not current_field.get('location'):
                missing.append('location')
            if not current_field.get('sowing_date'):
                missing.append('sowing_date')
        
        # For image inputs, we can proceed with diagnostic even without field data
        can_proceed = (input_type == "image") or (len(missing) == 0)
        
        return {
            "missing_data": missing,
            "can_proceed": can_proceed,
            "needs_data_collection": len(missing) > 0 and input_type != "image"
        }
    
    def analyze_and_route(self, state: AgentState) -> Literal["predictive", "diagnostic", "collect_data"]:
        """
        Intelligent routing based on:
        1. Input type (text vs image)
        2. User intent analysis
        3. Context from conversation history
        4. Field information availability
        """
        
        # First, check if we have required data
        data_check = self.check_required_data(state)
        
        # If critical data is missing for text queries, route to data collection first
        if data_check["needs_data_collection"]:
            state["missing_data"] = data_check["missing_data"]
            return "collect_data"
        
        user_input = state["user_input"]
        input_type = state["input_type"]
        conversation_context = state["conversation"]["messages"]
        user_profile = state["user_profile"]
        
        # Build routing prompt with agent capabilities
        routing_prompt = f"""
You are an intelligent routing agent for a potato disease management system.

USER INPUT: {user_input}
INPUT TYPE: {input_type}
USER HAS FIELD DATA: {bool(user_profile.get('fields'))}
FIELD LOCATION: {user_profile.get('fields', [{}])[0].get('location', 'Not set')}
SOWING DATE: {user_profile.get('fields', [{}])[0].get('sowing_date', 'Not set')}

RECENT CONVERSATION:
{self._format_conversation(conversation_context)}

AVAILABLE AGENTS:

1. PREDICTIVE AGENT (weather-based forecasting)
   - Use when: User asks about future disease risk, prevention, or "will my crop get disease"
   - Capabilities: 
     * Fetches weather data for user's location
     * Predicts disease probability based on environmental conditions
     * Provides preventive recommendations
     * Uses LLM validation to cross-check predictions with agricultural knowledge
   - Best for: Proactive disease management and planning
   
2. DIAGNOSTIC AGENT (image-based identification)
   - Use when: User uploads image OR describes visible symptoms on existing plants
   - Capabilities:
     * Identifies disease from plant images using GPT-4V
     * Determines crop stage and disease progression
     * Generates detailed treatment report using Tavily research
     * Provides immediate action items
   - Best for: Reactive disease management and treatment

ROUTING RULES:
- If INPUT TYPE is "image" → ALWAYS route to "diagnostic"
- Keywords for PREDICTIVE: "predict", "will", "forecast", "prevent", "risk", "likely", "weather", "conditions"
- Keywords for DIAGNOSTIC: "identify", "what is this", "spots", "leaves turning", "disease", "symptoms", "picture"
- If user describes current symptoms (e.g., "my plant has brown spots") → "diagnostic" even without image
- If ambiguous but field data exists → "predictive" (safer default for prevention)
- Consider conversation flow: if previous message was about a specific issue, stay contextually relevant

ANALYSIS STEPS:
1. Identify primary user intent (prediction vs diagnosis)
2. Check if symptoms are mentioned (past/present tense = diagnostic, future = predictive)
3. Consider conversation context
4. Assign confidence based on clarity of intent

Respond ONLY with valid JSON (no markdown, no extra text):
{{
    "agent": "predictive",
    "confidence": 85,
    "reasoning": "User is asking about future disease risk using 'will' and 'forecast' keywords. Field data is available for weather-based prediction."
}}

OR

{{
    "agent": "diagnostic",
    "confidence": 92,
    "reasoning": "User uploaded an image of potato plant. This requires visual disease identification."
}}
"""
        
        response = self.llm.invoke(routing_prompt)
        decision = self._parse_routing_decision(response.content)
        
        # Store reasoning in state for transparency
        state["routing_reasoning"] = decision["reasoning"]
        state["routing_confidence"] = decision["confidence"]
        state["selected_agent"] = decision["agent"]
        
        return decision["agent"]
    
    def _format_conversation(self, messages: List[Dict]) -> str:
        """Format recent conversation for context"""
        if not messages:
            return "No previous conversation"
        
        formatted = []
        for msg in messages[-4:]:  # Last 2 exchanges
            role = msg.get('role', 'unknown').upper()
            content = msg.get('content', '')[:200]  # Increased from 150 for better context
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
    
    def _parse_routing_decision(self, response: str) -> Dict:
        """Parse LLM's routing decision with robust error handling"""
        import json
        import re
        
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith('```'):
                # Extract JSON from code block
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned, re.DOTALL)
                if json_match:
                    cleaned = json_match.group(1)
            
            parsed = json.loads(cleaned)
            
            # Validate structure
            if "agent" not in parsed:
                raise ValueError("Missing 'agent' key")
            
            # Ensure agent is valid
            if parsed["agent"] not in ["predictive", "diagnostic"]:
                parsed["agent"] = "predictive"  # Safe default
            
            # Provide defaults for optional fields
            parsed.setdefault("confidence", 70)
            parsed.setdefault("reasoning", "Routing decision made")
            
            return parsed
            
        except Exception as e:
            print(f"⚠️ Router parsing error: {e}. Response was: {response[:200]}")
            
            # Intelligent fallback based on keywords
            response_lower = response.lower()
            
            if any(word in response_lower for word in ["diagnostic", "image", "identify", "symptom"]):
                return {
                    "agent": "diagnostic",
                    "confidence": 50,
                    "reasoning": "Fallback: Detected diagnostic keywords in malformed response"
                }
            else:
                return {
                    "agent": "predictive",
                    "confidence": 50,
                    "reasoning": "Fallback: Default to predictive for safety"
                }