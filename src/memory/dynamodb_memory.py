"""
DynamoDB-based long-term memory implementation
Replaces SQLite for Vercel deployment
"""
from typing import Optional, Dict, List
from .dynamodb_service import get_dynamodb_service

class DynamoDBLongTermMemory:
    """DynamoDB-based long-term memory"""
    
    def __init__(self, db_path: str = None):
        # db_path parameter for compatibility, but not used for DynamoDB
        self.db = get_dynamodb_service()
        if not self.db:
            raise RuntimeError("DynamoDB service not available")
    
    def _init_database(self):
        """No-op for DynamoDB (tables are created separately)"""
        pass
    
    def create_user(self, email: str, password: str = None, username: str = None, verified: bool = False) -> str:
        """Create new user with email and optional password"""
        from passlib.hash import bcrypt
        
        password_hash = None
        if password:
            password_hash = bcrypt.hash(password)
        
        return self.db.create_user(email, password_hash, username, verified)
    
    def update_user_verified(self, email: str, verified: bool = True):
        """Update user's verified status"""
        return self.db.update_user_verified(email, verified)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        return self.db.get_user_by_email(email)
    
    def authenticate_with_password(self, email: str, password: str) -> Optional[str]:
        """Authenticate user with email and password"""
        from passlib.hash import bcrypt
        
        user = self.db.get_user_by_email(email)
        if not user:
            return None
        
        password_hash = user.get('password_hash')
        if not password_hash:
            return None
        
        if bcrypt.verify(password, password_hash):
            return user['user_id']
        
        return None
    
    def store_otp(self, email: str, otp_code: str, expires_in_minutes: int = 10):
        """Store OTP code"""
        self.db.store_otp(email, otp_code, expires_in_minutes)
    
    def verify_otp(self, email: str, otp_code: str) -> bool:
        """Verify OTP code"""
        return self.db.verify_otp(email, otp_code)
    
    def create_conversation(self, user_id: str, title: str = None) -> str:
        """Create a new conversation"""
        return self.db.create_conversation(user_id, title)
    
    def get_user_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversations for a user"""
        return self.db.get_user_conversations(user_id)
    
    def add_message_to_conversation(self, conversation_id: str, role: str, content: str, metadata: Dict = None):
        """Add message to a conversation"""
        return self.db.add_message(conversation_id, role, content, metadata)
    
    def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """Get all messages for a conversation"""
        return self.db.get_conversation_messages(conversation_id)
    
    def add_field(self, user_id: str, location: str, sowing_date: str, area_hectares: float = None,
                  latitude: float = None, longitude: float = None, email: str = None) -> str:
        """Add a new field for user with email stored in fields table"""
        # If email not provided, try to get it from user
        if not email:
            user = self.get_user_by_id(user_id)
            if user:
                email = user.get('email')
        return self.db.create_field(
            user_id=user_id,
            location=location,
            sowing_date=sowing_date,
            area_hectares=area_hectares,
            email=email,
            latitude=latitude,
            longitude=longitude
        )
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Retrieve complete user profile with all fields"""
        # Get user by user_id
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Get fields
        fields = self.db.get_user_fields(user_id)
        
        return {
            'user_id': user_id,
            'email': user.get('email'),
            'username': user.get('username'),
            'created_at': user.get('created_at'),
            'fields': fields
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by user_id using GSI"""
        return self.db.get_user_by_id(user_id)
    
    def update_field(self, field_id: str, user_id: str, location: str = None, sowing_date: str = None,
                     area_hectares: float = None, latitude: float = None, longitude: float = None) -> bool:
        """Update field information"""
        if hasattr(self.db, 'update_field'):
            return self.db.update_field(
                field_id=field_id,
                location=location,
                sowing_date=sowing_date,
                area_hectares=area_hectares,
                latitude=latitude,
                longitude=longitude
            )
        return False

