from collections import deque
from typing import List, Dict
import json
import datetime

class ShortTermMemory:
    """Manages recent conversation history (last 3 chats)"""
    
    def __init__(self, max_conversations: int = 3):
        self.max_conversations = max_conversations
        self.conversations = {}  # {session_id: deque([messages])}
    
    def add_message(self, session_id: str, role: str, content: str, 
                    metadata: Dict = None):
        """Add a message to conversation history"""
        if session_id not in self.conversations:
            self.conversations[session_id] = deque(maxlen=self.max_conversations)
        
        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversations[session_id].append(message)
    
    def get_recent_context(self, session_id: str, 
                          num_messages: int = 6) -> List[Dict]:
        """Retrieve recent messages for context"""
        if session_id not in self.conversations:
            return []
        
        # Get last N messages (3 exchanges = 6 messages)
        recent = list(self.conversations[session_id])[-num_messages:]
        return recent
    
    def clear_session(self, session_id: str):
        """Clear conversation history for session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def format_for_llm(self, session_id: str) -> str:
        """Format conversation history for LLM context"""
        messages = self.get_recent_context(session_id)
        formatted = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in messages
        ])
        return formatted