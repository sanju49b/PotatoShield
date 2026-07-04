from typing import TypedDict,Optional,List,Literal
from datetime import datetime

class UserProfile(TypedDict):
    '''Long-term user data'''
    user_id: str
    username: str
    fields : List[dict] ## [{field_id, location, crop_type, sowing_date}]

class ConversationContext(TypedDict):
    '''short-term session data'''
    session_id: str
    messages: List[dict]
    current_field_id: Optional[str]

class AgentState(TypedDict, total=False):
    '''Master State Passed through LangGraph Nodes'''
    #user context
    user_profile: UserProfile
    conversation: ConversationContext

    #current interaction
    user_input: str
    input_type: Literal["text","image"] #Text query or image upload
    image_data: Optional[bytes]

    #Routing Decision
    selected_agent: Optional[Literal["predictive","diagnostic","general_chat","direct_response","collect_data"]]
    routing_reasoning: Optional[str] #why this route is chosen, explained by the agent
    routing_confidence: Optional[int] #confidence score for routing decision

    #agent outputs
    weather_data: Optional[dict]
    weather_dataset: Optional[dict]  # Full weather dataset from BlightPredictionAgent
    disease_prediction: Optional[dict]
    blight_prediction: Optional[dict]  # Enhanced blight prediction from BlightPredictionAgent
    disease_identification: Optional[dict]
    final_report: Optional[str]
    
    #streaming progress
    progress_updates: Optional[List[dict]]  # List of progress updates for UI
    current_progress: Optional[dict]  # Current progress state

    #language preferences
    preferred_language: Optional[str]
    requested_languages: Optional[List[str]]

    #data collection
    missing_data: Optional[List[str]]  # List of missing data fields
    awaiting_data: Optional[List[str]]  # List of data fields awaiting user response
    extracted_location: Optional[str]  # Location extracted from user response
    extracted_sowing_date: Optional[str]  # Sowing date extracted from user response
    data_collection_complete: Optional[bool]  # Whether data collection is complete

    #validation
    llm_judge_validation: Optional[dict]
    