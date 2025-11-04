# src/graph/workflow.py (updated)
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.state.agent_state import AgentState
from src.agents.router_agent import RouterAgent
from src.agents.data_collection_agent import DataCollectionAgent
from src.agents.predictive_agent import PredictiveAgent
from src.agents.diagnostic_agent import DiagnosticAgent
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
                "collect_data": "collect_data"
            }
        )
        
        # Data collection loop
        workflow.add_edge("collect_data", "save_conversation")  # Ask user and wait
        # When user responds with data, it goes through parse_data
        workflow.add_edge("parse_data", "router")  # Re-route after data collection
        
        # Both agents converge to save step
        workflow.add_edge("predictive_agent", "save_conversation")
        workflow.add_edge("diagnostic_agent", "save_conversation")
        workflow.add_edge("save_conversation", END)
        
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    def _routing_logic(self, state: AgentState) -> str:
        """Conditional edge: Return next node based on router decision"""
        return state["selected_agent"]
    
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
    
