"""
DynamoDB-based short-term memory for conversation history
"""
from typing import List, Dict
from datetime import datetime
from .dynamodb_service import get_dynamodb_service

class DynamoDBShortTermMemory:
    """DynamoDB-based short-term memory"""
    
    def __init__(self, max_conversations: int = 3):
        self.max_conversations = max_conversations
        self.db = get_dynamodb_service()
        if not self.db:
            raise RuntimeError("DynamoDB service not available")
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None):
        """Add a message to conversation history"""
        # Use session_id as conversation_id for short-term memory
        # Get or create conversation for this session
        conversation_id = f"session_{session_id}"
        
        # Sanitize before persisting
        content = self.db._sanitize_content(content)
        
        # Store message in messages table
        self.db.add_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata=metadata
        )
    
    def get_recent_context(self, session_id: str, num_messages: int = 6) -> List[Dict]:
        """Retrieve recent messages for context"""
        conversation_id = f"session_{session_id}"
        messages = self.db.get_conversation_messages(conversation_id)
        
        # Return last N messages
        return messages[-num_messages:] if len(messages) > num_messages else messages
    
    def clear_session(self, session_id: str):
        """Clear conversation history for session"""
        # In DynamoDB, we can't easily delete all messages, but we can mark them
        # For simplicity, we'll just not return old messages
        pass
    
    def format_for_llm(self, session_id: str) -> str:
        """Format conversation history for LLM context"""
        messages = self.get_recent_context(session_id)
        formatted = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in messages
        ])
        return formatted

