# src/agents/data_collection_agent.py
from langchain_openai import ChatOpenAI
from typing import Dict
from src.state.agent_state import AgentState

class DataCollectionAgent:
    """
    Handles missing data collection through conversational prompts.
    Asks user for location and sowing date if not in profile.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def collect_missing_data(self, state: AgentState) -> AgentState:
        """
        Generate a friendly prompt to collect missing data.
        """
        missing_data = state.get("missing_data", [])
        user_input = state["user_input"]
        
        # Generate contextual data request
        prompt = f"""
You are a friendly agricultural assistant. The user asked: "{user_input}"

To help them, you need the following information which is missing from their profile:
{', '.join(missing_data)}

Generate a friendly, conversational response that:
1. Acknowledges their question
2. Explains why you need this information (briefly)
3. Asks for the missing data in a natural way
4. Provides examples or suggestions

Be concise (2-3 sentences max). Sound helpful, not robotic.

Example good response:
"I'd love to help predict disease risk for your potato crop! To give you accurate forecasts based on weather conditions, I need to know: Where is your field located? (city/coordinates), and When did you plant? (sowing date). You can also allow location access if that's easier!"

Generate response:
"""
        
        response = self.llm.invoke(prompt)
        
        # Store the request message
        state["final_report"] = response.content
        state["awaiting_data"] = missing_data
        
        return state
    
    def parse_user_data_response(self, state: AgentState) -> AgentState:
        """
        Extract location and sowing date from user's response using LLM.
        """
        user_response = state["user_input"]
        awaiting_data = state.get("awaiting_data", [])
        
        extraction_prompt = f"""
Extract structured data from the user's response.

User said: "{user_response}"

We're looking for: {', '.join(awaiting_data)}

Extract and return ONLY valid JSON:
{{
    "location": "city name or coordinates or null",
    "sowing_date": "YYYY-MM-DD format or null"
}}

Examples:
- "I'm in Bihar, planted on Jan 15 2025" → {{"location": "Bihar", "sowing_date": "2025-01-15"}}
- "My field is in Patna" → {{"location": "Patna", "sowing_date": null}}
- "Planted last month" → {{"location": null, "sowing_date": null}} (need specific date)

Be strict: only extract if information is clear and complete.
"""
        
        response = self.llm.invoke(extraction_prompt)
        
        import json
        import re
        
        try:
            # Clean response
            cleaned = response.content.strip()
            if cleaned.startswith('```'):
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned, re.DOTALL)
                if json_match:
                    cleaned = json_match.group(1)
            
            extracted = json.loads(cleaned)
            
            # Update state with extracted data
            if extracted.get("location"):
                state["extracted_location"] = extracted["location"]
            if extracted.get("sowing_date"):
                state["extracted_sowing_date"] = extracted["sowing_date"]
            
            # Check if all required data is now available
            still_missing = []
            if "location" in awaiting_data and not extracted.get("location"):
                still_missing.append("location")
            if "sowing_date" in awaiting_data and not extracted.get("sowing_date"):
                still_missing.append("sowing_date")
            
            state["missing_data"] = still_missing
            state["data_collection_complete"] = len(still_missing) == 0
            
        except Exception as e:
            print(f"⚠️ Data extraction error: {e}")
            state["data_collection_complete"] = False
            state["final_report"] = "I couldn't quite understand that. Could you provide your location (city/region) and sowing date (e.g., 2025-01-15) clearly?"
        
        return state