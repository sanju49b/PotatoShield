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
    
    def analyze_and_route(self, state: AgentState) -> Literal["predictive", "diagnostic", "collect_data", "direct_response", "general_chat"]:
        """
        Intelligent routing based on:
        1. Input type (text vs image)
        2. User intent analysis
        3. Context from conversation history
        4. Field information availability
        """
        
        user_input_lower = state["user_input"].lower()
        user_input = state["user_input"]  # Keep original for context
        input_type = state["input_type"]
        user_profile = state["user_profile"]
        fields = user_profile.get('fields', [])
        current_field = fields[0] if fields else {}
        location = current_field.get('location', '')
        sowing_date = current_field.get('sowing_date', '')
        
        # Check if user is asking about location or sowing date (comprehensive keyword matching)
        # Use word boundaries and phrases for better matching
        location_phrases = [
            'location', 'where', 'place', 'field location', 'my location', 'where is my field',
            'where is', 'where are', 'where do', 'where did', 'what is my location',
            'tell me my location', 'show me location', 'my field location', 'what location',
            'which location', 'location of', 'location is', 'where is my', 'where are my'
        ]
        dos_phrases = [
            'sowing date', 'dos', 'date of sowing', 'when did i sow', 'when did we sow',
            'when planted', 'planting date', 'when did you plant', 'when was planting',
            'crop date', 'sow date', 'when did i plant', 'when did we plant', 'planting date',
            'date of planting', 'when was', 'when did', 'sowing', 'planted'
        ]
        
        # Check for location queries (more precise - only field location questions)
        is_location_query = (
            'my location' in user_input_lower or
            'field location' in user_input_lower or
            'what is my location' in user_input_lower or
            'tell me my location' in user_input_lower or
            'show me location' in user_input_lower or
            'show me my location' in user_input_lower or
            ('where is' in user_input_lower and ('my' in user_input_lower or 'field' in user_input_lower)) or
            ('where are' in user_input_lower and ('my' in user_input_lower or 'field' in user_input_lower)) or
            (user_input_lower.strip() == 'location') or  # Single word "location"
            (user_input_lower.strip() == 'my location') or
            (user_input_lower in ['where is my field', 'where is my field located', 'what is my location', 'where am i'])
        )
        
        # Check for DOS queries
        is_dos_query = (
            'dos' in user_input_lower or
            'sowing date' in user_input_lower or
            'date of sowing' in user_input_lower or
            'planting date' in user_input_lower or
            'when did i sow' in user_input_lower or
            'when did we sow' in user_input_lower or
            'when planted' in user_input_lower or
            'when did i plant' in user_input_lower or
            'when did we plant' in user_input_lower or
            'when was planting' in user_input_lower or
            ('sowing' in user_input_lower and 'date' in user_input_lower) or
            ('planted' in user_input_lower and 'when' in user_input_lower)
        )
        
        # If asking about location or DOS, answer directly (even if data is missing)
        if is_location_query or is_dos_query:
            state["selected_agent"] = "direct_response"
            state["routing_reasoning"] = "User is asking about their field information"
            state["routing_confidence"] = 95
            
            # Generate direct response about location/DOS
            response_parts = []
            
            if is_location_query:
                if location:
                    response_parts.append(f"📍 **Your field location:** {location}")
                else:
                    response_parts.append("📍 Your field location is not set yet. Please visit the field setup page to add your location.")
            
            if is_dos_query:
                if sowing_date:
                    # Format the date nicely
                    try:
                        from datetime import datetime
                        date_obj = datetime.strptime(sowing_date, "%Y-%m-%d")
                        formatted_date = date_obj.strftime("%B %d, %Y")
                        response_parts.append(f"📅 **Your date of sowing (DOS):** {formatted_date} ({sowing_date})")
                    except:
                        response_parts.append(f"📅 **Your date of sowing (DOS):** {sowing_date}")
                else:
                    response_parts.append("📅 Your date of sowing is not set yet. Please visit the field setup page to add your sowing date.")
            
            # If asking for both
            if is_location_query and is_dos_query:
                if location and sowing_date:
                    response_parts.append(f"\nThis information helps me provide accurate disease predictions and recommendations for your field in {location}.")
            
            if response_parts:
                state["final_report"] = "\n\n".join(response_parts)
                return "direct_response"
        
        # First, check if we have required data
        data_check = self.check_required_data(state)
        
        # If critical data is missing for text queries, route to data collection first
        if data_check["needs_data_collection"]:
            state["missing_data"] = data_check["missing_data"]
            return "collect_data"
        
        conversation_context = state["conversation"].get("messages", [])
        
        # Build routing prompt with agent capabilities and full conversation context
        routing_prompt = f"""
You are an intelligent routing agent for a potato disease management system. You can also act as a general conversational assistant when queries are not about disease prediction or diagnosis.

USER INPUT: {user_input}
INPUT TYPE: {input_type}
USER HAS FIELD DATA: {bool(user_profile.get('fields'))}
FIELD LOCATION: {user_profile.get('fields', [{}])[0].get('location', 'Not set')}
SOWING DATE: {user_profile.get('fields', [{}])[0].get('sowing_date', 'Not set')}

FULL CONVERSATION HISTORY:
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

3. GENERAL CHAT (conversational assistant)
   - Use when: User asks general questions, greetings, thanks, or queries not related to disease prediction/diagnosis
   - Capabilities:
     * Provides friendly, contextual responses
     * Answers questions about potato farming, general agriculture
     * Maintains conversation flow and context
     * Can reference previous messages in the conversation
   - Best for: General conversation, questions, follow-ups, clarifications

ROUTING RULES:
- If INPUT TYPE is "image" → ALWAYS route to "diagnostic"
- Keywords for PREDICTIVE: "predict", "will", "forecast", "prevent", "risk", "likely", "weather", "conditions", "future", "chance"
- Keywords for DIAGNOSTIC: "identify", "what is this", "spots", "leaves turning", "disease", "symptoms", "picture", "image", "help", "problem", "issue"
- Keywords for GENERAL CHAT: greetings ("hi", "hello", "hey"), thanks, general questions, clarifications, follow-ups
- If user describes current symptoms (e.g., "my plant has brown spots") → "diagnostic" even without image
- If query is conversational or general (not about disease) → "general_chat"
- Consider FULL conversation context: previous messages may provide important context for current query
- Maintain conversation continuity: if previous message was about a specific disease, continue that context

ANALYSIS STEPS:
1. Check if this is a general conversation (greetings, thanks, general questions) → "general_chat"
2. Identify primary user intent (prediction vs diagnosis vs general chat)
3. Check if symptoms are mentioned (past/present tense = diagnostic, future = predictive)
4. Consider FULL conversation history for context
5. Assign confidence based on clarity of intent

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

OR

{{
    "agent": "general_chat",
    "confidence": 90,
    "reasoning": "User is asking a general question or having a conversation not directly related to disease prediction/diagnosis."
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
        """Format conversation history for context (uses more messages for better context)"""
        if not messages:
            return "No previous conversation"
        
        formatted = []
        # Use last 10 messages (last 5 exchanges) for better context
        for msg in messages[-10:]:
            role = msg.get('role', 'unknown').upper()
            content = msg.get('content', '')
            # Don't truncate too aggressively - keep more context
            if len(content) > 300:
                content = content[:300] + "..."
            formatted.append(f"{role}: {content}")
        
        if len(messages) > 10:
            return f"... ({len(messages) - 10} earlier messages)\n" + "\n".join(formatted)
        
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
            if parsed["agent"] not in ["predictive", "diagnostic", "general_chat", "direct_response"]:
                parsed["agent"] = "general_chat"  # Safe default for conversational queries
            
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