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

class AgentState(TypedDict):
    '''Master State Passed through LangGraph Nodes'''
    #user context
    user_profile: UserProfile
    conversation: ConversationContext

    #current interaction
    user_input: str
    input_type: Literal["text","image"] #Text query or image upload
    image_data: Optional[bytes]

    #Routing Decision
    selected_agent: Optional[Literal["predictive","diagnostic"]]
    routing_resoning: Optional[str] #why this route is chosen, explained by the agent

    #agent outputs
    weather_data: Optional[dict]
    disease_prediction: Optional[dict]
    disease_identification: Optional[dict]
    final_report: Optional[str]

    #validation
    llm_judge_validation: Optional[dict]
    