# src/graph/workflow.py (updated)
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.state.agent_state import AgentState
from src.agents.router_agent import RouterAgent
from src.agents.data_collection_agent import DataCollectionAgent
from src.agents.predictive_agent import PredictiveAgent
from src.agents.diagnostic_agent import DiagnosticAgent
from src.agents.general_chat_agent import GeneralChatAgent
from src.memory.long_term_memory import LongTermMemory
from src.memory.short_term_memory import ShortTermMemory

class PotatoCareWorkflow:
    """
    Main LangGraph orchestration with data collection loop
    """
    
    def __init__(self):
        self.long_memory = LongTermMemory()
        self.short_memory = ShortTermMemory()
        self.router = RouterAgent()
        self.data_collector = DataCollectionAgent()
        self.predictive = PredictiveAgent()
        self.diagnostic = DiagnosticAgent()
        self.general_chat = GeneralChatAgent(long_memory=self.long_memory)
        
        self.app = self._build_graph()
    
    def _build_graph(self):
        """Construct the LangGraph workflow with data collection"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("load_context", self._load_user_context)
        workflow.add_node("router", self._route_to_agent)
        workflow.add_node("collect_data", self._collect_missing_data)
        workflow.add_node("parse_data", self._parse_collected_data)
        workflow.add_node("predictive_agent", self._run_predictive)
        workflow.add_node("diagnostic_agent", self._run_diagnostic)
        workflow.add_node("general_chat_agent", self._run_general_chat)
        workflow.add_node("save_conversation", self._save_to_memory)
        
        # Define flow
        workflow.add_edge(START, "load_context")
        workflow.add_edge("load_context", "router")
        
        # Conditional routing from router
        workflow.add_conditional_edges(
            "router",
            self._routing_logic,
            {
                "predictive": "predictive_agent",
                "diagnostic": "diagnostic_agent",
                "collect_data": "collect_data",
                "direct_response": "save_conversation",  # Direct responses go straight to save
                "general_chat": "general_chat_agent"
            }
        )
        
        # Data collection loop
        workflow.add_edge("collect_data", "save_conversation")  # Ask user and wait
        # When user responds with data, it goes through parse_data
        workflow.add_edge("parse_data", "router")  # Re-route after data collection
        
        # All agents converge to save step
        workflow.add_edge("predictive_agent", "save_conversation")
        workflow.add_edge("diagnostic_agent", "save_conversation")
        workflow.add_edge("general_chat_agent", "save_conversation")
        workflow.add_edge("save_conversation", END)
        
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    def _routing_logic(self, state: AgentState) -> str:
        """Conditional edge: Return next node based on router decision"""
        selected = state.get("selected_agent")
        
        # Return the selected agent directly - the conditional edges mapping will handle routing
        # "direct_response" -> "save_conversation" (mapped in conditional_edges)
        # "general_chat" -> "general_chat_agent" (mapped in conditional_edges)
        # "predictive" -> "predictive_agent" (mapped in conditional_edges)
        # "diagnostic" -> "diagnostic_agent" (mapped in conditional_edges)
        # "collect_data" -> "collect_data" (mapped in conditional_edges)
        
        if selected in ["direct_response", "general_chat", "predictive", "diagnostic", "collect_data"]:
            return selected
        
        # Fallback to general_chat if unknown
        return "general_chat"
    
    def _collect_missing_data(self, state: AgentState) -> AgentState:
        """Node: Ask user for missing data"""
        return self.data_collector.collect_missing_data(state)
    
    def _parse_collected_data(self, state: AgentState) -> AgentState:
        """Node: Extract structured data from user response"""
        result = self.data_collector.parse_user_data_response(state)
        
        # If data is complete, save to long-term memory
        if result.get("data_collection_complete"):
            user_id = state["user_profile"]["user_id"]
            location = result.get("extracted_location")
            sowing_date = result.get("extracted_sowing_date")
            
            if location and sowing_date:
                field_id = self.long_memory.add_field(
                    user_id=user_id,
                    location=location,
                    sowing_date=sowing_date
                )
                # Update state with new field
                state["conversation"]["current_field_id"] = field_id
        
        return result
    
    def _load_user_context(self, state: AgentState) -> AgentState:
        """Node: Load user profile and conversation history"""
        user_id = state["user_profile"]["user_id"]
        session_id = state["conversation"]["session_id"]
        
        # Load user profile from long-term memory
        profile = self.long_memory.get_user_profile(user_id)
        if profile:
            state["user_profile"] = {
                "user_id": profile.get("user_id", user_id),
                "username": profile.get("username", ""),
                "fields": profile.get("fields", [])
            }
        
        # If messages already exist in state (loaded from conversation history), preserve them
        # Otherwise, load from short-term memory as fallback
        if not state["conversation"].get("messages"):
            recent_messages = self.short_memory.get_recent_context(session_id)
            state["conversation"]["messages"] = recent_messages
        # If messages exist, keep them (they're from conversation history loaded in API)
        
        # Ensure messages list exists and is properly formatted
        if not state["conversation"].get("messages"):
            state["conversation"]["messages"] = []
        
        # Debug: Print conversation context being loaded
        print(f"📝 Loaded {len(state['conversation']['messages'])} messages for context")
        if state["conversation"]["messages"]:
            print(f"   Last message: {state['conversation']['messages'][-1].get('role', 'unknown')}: {state['conversation']['messages'][-1].get('content', '')[:50]}...")
        
        return state
    
    def _route_to_agent(self, state: AgentState) -> AgentState:
        """Node: Route to appropriate agent based on analysis"""
        # Determine input type if not set
        if not state.get("input_type"):
            if state.get("image_data"):
                state["input_type"] = "image"
            else:
                state["input_type"] = "text"
        
        # Router analyzes and decides
        selected = self.router.analyze_and_route(state)
        
        # Store routing decision (already done in router, but ensure it's set)
        if not state.get("selected_agent"):
            state["selected_agent"] = selected
        
        return state
    
    def _run_predictive(self, state: AgentState) -> AgentState:
        """Node: Run predictive agent for weather-based forecasting"""
        # Check if predictive agent is available
        if not hasattr(self.predictive, 'predict') or not callable(getattr(self.predictive, 'predict', None)):
            state["final_report"] = "Predictive agent is not yet implemented. Please use diagnostic agent with an image."
            return state
        
        # Initialize progress tracking
        state["progress_updates"] = []
        state["current_progress"] = {"step": 0, "total_steps": 12, "progress": 0, "message": "Starting analysis..."}
        
        # Run blight prediction (BlightPredictionAgent already updates state)
        result = self.predictive.predict(state)
        
        # Extract results - BlightPredictionAgent sets blight_prediction in state
        # but we also need to ensure workflow fields are set
        blight_prediction = state.get("blight_prediction") or result.get("prediction", {})
        weather_dataset = state.get("weather_dataset") or result.get("weather_data", {})
        final_report = state.get("final_report") or result.get("report", "Prediction completed.")
        
        # Update state with all results
        state["blight_prediction"] = blight_prediction
        state["disease_prediction"] = blight_prediction  # Also set for compatibility
        state["weather_data"] = weather_dataset
        state["weather_dataset"] = weather_dataset  # Also set for compatibility
        state["final_report"] = final_report
        
        # Mark progress as complete
        state["current_progress"] = {"step": 12, "total_steps": 12, "progress": 100, "message": "Analysis complete!"}
        
        return state
    
    def _run_diagnostic(self, state: AgentState) -> AgentState:
        """Node: Run diagnostic agent for image-based disease identification"""
        result = self.diagnostic.identify_disease(state)
        return result
    
    def _run_general_chat(self, state: AgentState) -> AgentState:
        """Node: Run general chat agent for conversational responses"""
        return self.general_chat.chat(state)
    
    def _save_to_memory(self, state: AgentState) -> AgentState:
        """Node: Save conversation to memory (both short-term and long-term)"""
        session_id = state["conversation"]["session_id"]
        user_input = state.get("user_input", "")
        final_report = state.get("final_report", "")
        
        # Save user message if exists
        if user_input:
            # Save to short-term memory
            self.short_memory.add_message(
                session_id=session_id,
                role="user",
                content=user_input,
                metadata={
                    "input_type": state.get("input_type"),
                    "selected_agent": state.get("selected_agent")
                }
            )
            
            # Also save to long-term memory if session_id is a conversation_id
            # (conversation_ids are UUIDs, session_ids might be different format)
            if len(session_id) > 20 and '-' in session_id:  # Likely a UUID/conversation_id
                try:
                    self.long_memory.add_message_to_conversation(
                        conversation_id=session_id,
                        role="user",
                        content=user_input,
                        metadata={
                            "input_type": state.get("input_type"),
                            "selected_agent": state.get("selected_agent"),
                            "has_image": bool(state.get("image_data"))
                        }
                    )
                except Exception as e:
                    print(f"⚠️ Could not save to long-term memory: {e}")
        
        # Save assistant response
        if final_report:
            # Save to short-term memory
            self.short_memory.add_message(
                session_id=session_id,
                role="assistant",
                content=final_report,
                metadata={
                    "agent": state.get("selected_agent"),
                    "routing_confidence": state.get("routing_confidence"),
                    "disease_identification": state.get("disease_identification"),
                    "disease_prediction": state.get("disease_prediction")
                }
            )
            
            # Also save to long-term memory
            if len(session_id) > 20 and '-' in session_id:  # Likely a UUID/conversation_id
                try:
                    self.long_memory.add_message_to_conversation(
                        conversation_id=session_id,
                        role="assistant",
                        content=final_report,
                        metadata={
                            "agent": state.get("selected_agent"),
                            "routing_confidence": state.get("routing_confidence"),
                            "disease_identification": state.get("disease_identification"),
                            "disease_prediction": state.get("disease_prediction")
                        }
                    )
                except Exception as e:
                    print(f"⚠️ Could not save to long-term memory: {e}")
        
        return state
    
    def invoke(self, state: AgentState, config: dict = None):
        """Invoke the workflow with initial state"""
        if config is None:
            config = {"configurable": {"thread_id": state["conversation"]["session_id"]}}
        return self.app.invoke(state, config)
    
    def stream(self, state: AgentState, config: dict = None):
        """Stream workflow execution"""
        if config is None:
            config = {"configurable": {"thread_id": state["conversation"]["session_id"]}}
        return self.app.stream(state, config)
