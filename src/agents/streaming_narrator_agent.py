"""
Streaming Narrator Agent - Provides real-time AI-powered commentary during analysis

This agent acts as a narrator that:
1. Watches data collection progress
2. Explains what's happening in conversational language
3. Provides context and key findings
4. Summarizes the final report decisions
"""

import os
from typing import AsyncGenerator, Dict, Any, List
from openai import AsyncOpenAI

class StreamingNarratorAgent:
    """AI narrator that explains analysis progress in real-time"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # Fast and cost-effective
        self.progress_context: List[str] = []
        
    async def narrate_progress(
        self,
        progress_message: str,
        stage: str,
        context: Dict[str, Any] = None
    ) -> AsyncGenerator[str, None]:
        """
        Narrate a single progress update with AI commentary
        
        Args:
            progress_message: Raw progress message from data collection
            stage: Current stage of analysis
            context: Additional context (location, crop info, etc.)
        
        Yields:
            AI-generated narrative chunks
        """
        # Add to context history
        self.progress_context.append(f"[{stage}] {progress_message}")
        
        # Only narrate significant milestones, not every single update
        should_narrate = self._should_narrate(progress_message, stage)
        
        if not should_narrate:
            return
        
        # Build prompt for AI narrator
        prompt = self._build_narration_prompt(progress_message, stage, context)
        
        try:
            # Stream AI response
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a friendly agricultural AI assistant narrating the analysis process.
                        
Your role:
- Explain what's happening in simple, conversational language
- Highlight why each step matters for farmers
- Keep responses brief (1-2 sentences max)
- Use a warm, supportive tone
- Add relevant emojis for visual appeal
- For disease prediction: Focus on weather patterns and disease risk
- For image diagnosis: Focus on visual analysis and disease identification

Example styles:
Predictive: "🌍 Found your location in Bengaluru! Now gathering weather data from the past week to check conditions..."
Diagnostic: "📸 Analyzing your crop image closely to identify any disease symptoms..."
"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=150,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"[NARRATOR] Error generating narration: {e}")
            # Fallback to original message if AI fails
            yield progress_message
    
    async def explain_final_report(
        self,
        report: str,
        chart_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        Provide AI explanation of the final report and key decisions
        
        Args:
            report: The final generated report
            chart_data: Chart data with risk percentages
            context: Analysis context
            
        Yields:
            AI-generated explanation chunks
        """
        prompt = f"""Based on this disease risk analysis, provide a clear, friendly explanation of the key findings:

Location: {context.get('location', 'Unknown')}
Crop Stage: {context.get('growth_stage', 'Unknown')}

Risk Results:
- Late Blight Risk: {chart_data.get('final_risk_percentage', {}).get('late_blight', 0):.1f}%
- Early Blight Risk: {chart_data.get('final_risk_percentage', {}).get('early_blight', 0):.1f}%
- Overall Risk: {chart_data.get('final_risk_percentage', {}).get('overall', 0):.1f}%

Your task:
1. Explain WHY these risk levels were determined (2-3 key factors)
2. Highlight the most important finding farmers should know
3. Summarize the main recommendation
4. Keep it concise (3-4 sentences max)
5. Use a supportive, actionable tone

Format as a brief summary starting with "🔍 **KEY FINDINGS:**"
"""
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an agricultural AI assistant explaining disease risk analysis to farmers. Be clear, supportive, and actionable."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"[NARRATOR] Error explaining report: {e}")
            yield "\n\n🔍 **Analysis Complete!** The detailed report and visualizations are now available above."
    
    def _should_narrate(self, message: str, stage: str) -> bool:
        """Determine if a progress message should be narrated"""
        # Narrate these key milestones for PREDICTIVE agent
        narrate_keywords = [
            "Getting coordinates",
            "Found:",
            "COMPREHENSIVE DATA COLLECTION",
            "Fetching historical weather",
            "[OK] Historical data fetched",
            "Fetching forecast weather",
            "[OK] Forecast data fetched",
            "Analyzing temperature",
            "Checking Hutton Criteria",
            "Calculating Late Blight",
            "Calculating Early Blight",
            "Generating visualizations"
        ]
        
        # Narrate these key milestones for DIAGNOSTIC agent
        diagnostic_keywords = [
            "Analyzing image",
            "Loading vision",
            "Preprocessing image",
            "Extracting features",
            "Identifying disease",
            "Confidence",
            "Severity"
        ]
        
        # Skip these verbose updates
        skip_keywords = [
            "Elevation:",
            "Timezone:",
            "Target Date:",
            "Window:",
            "Today's Date:",
            "Aggregating hourly",
            "Created 8 daily",
            "==="
        ]
        
        # Skip if message contains skip keywords
        if any(skip in message for skip in skip_keywords):
            return False
        
        # Narrate if message contains narrate keywords (predictive or diagnostic)
        return any(keyword in message for keyword in narrate_keywords + diagnostic_keywords)
    
    def _build_narration_prompt(
        self,
        progress_message: str,
        stage: str,
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for AI narrator"""
        location = context.get('location', 'your location') if context else 'your location'
        
        return f"""Progress update from disease analysis system:
Stage: {stage}
Message: {progress_message}
Location: {location}

Explain this step to a farmer in 1-2 friendly sentences. Why does this matter for disease prediction?
"""
    
    def reset_context(self):
        """Reset the progress context for a new analysis"""
        self.progress_context = []

