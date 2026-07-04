from collections import deque
from typing import List, Dict
import json
import datetime
import os

# Check if we should use DynamoDB
USE_DYNAMODB = os.getenv('USE_DYNAMODB', 'false').lower() == 'true'

if USE_DYNAMODB:
    from .dynamodb_short_term import DynamoDBShortTermMemory
    ShortTermMemory = DynamoDBShortTermMemory
else:
    # SQLite/in-memory implementation (for local development)
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
            
            content = self._sanitize_content(content)
            message = {
                "role": role,  # "user" or "assistant"
                "content": content,
                "timestamp": datetime.datetime.now().isoformat(),
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
        
        def _sanitize_content(self, text: str) -> str:
            """Mask obvious PII and trim oversized payloads before persistence (in-memory)."""
            if not text:
                return text
            import re
            cleaned = text
            patterns = [
                re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
                re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),
                re.compile(r"\b\d{12,19}\b"),
            ]
            for pat in patterns:
                cleaned = pat.sub("[REDACTED]", cleaned)
            cleaned = re.sub(r"https?://\S+", "[LINK]", cleaned)
            return cleaned[:2000]
        
        def format_for_llm(self, session_id: str) -> str:
            """Format conversation history for LLM context"""
            messages = self.get_recent_context(session_id)
            formatted = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in messages
            ])
            return formatted