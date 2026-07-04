"""
AWS DynamoDB service for storing users, conversations, and messages
Cost-effective with PAY_PER_REQUEST billing mode
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, List
from datetime import datetime
import json
import os
from decimal import Decimal

class DynamoDBService:
    """Service for interacting with DynamoDB tables"""
    
    def __init__(self):
        # Get AWS region from environment
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Initialize DynamoDB resource
        try:
            self.dynamodb = boto3.resource('dynamodb', region_name=self.aws_region)
            print(f"DynamoDB client initialized for region: {self.aws_region}")
        except Exception as e:
            print(f"Warning: Failed to initialize DynamoDB: {e}")
            self.dynamodb = None
        
        # Table names
        self.users_table_name = "potato-shield-users"
        self.conversations_table_name = "potato-shield-conversations"
        self.messages_table_name = "potato-shield-messages"
        self.fields_table_name = "potato-shield-fields"
        self.otp_table_name = "potato-shield-otp"
        self.sessions_table_name = "potato-shield-sessions"
        
        # Initialize tables
        self._init_tables()
    
    def _init_tables(self):
        """Initialize or get DynamoDB tables"""
        if not self.dynamodb:
            return
        
        try:
            # Users table (with GSI on user_id for lookups)
            self.users_table = self._get_or_create_table(
                self.users_table_name,
                [
                    {"AttributeName": "email", "KeyType": "HASH"}  # Partition key
                ],
                [
                    {"AttributeName": "email", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"}
                ],
                global_secondary_indexes=[
                    {
                        'IndexName': 'user_id-index',
                        'KeySchema': [
                            {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            )
            
            # Conversations table
            self.conversations_table = self._get_or_create_table(
                self.conversations_table_name,
                [
                    {"AttributeName": "conversation_id", "KeyType": "HASH"}
                ],
                [
                    {"AttributeName": "conversation_id", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "updated_at", "AttributeType": "S"}
                ],
                global_secondary_indexes=[
                    {
                        'IndexName': 'user_id-index',
                        'KeySchema': [
                            {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'updated_at', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            )
            
            # Messages table
            self.messages_table = self._get_or_create_table(
                self.messages_table_name,
                [
                    {"AttributeName": "message_id", "KeyType": "HASH"}
                ],
                [
                    {"AttributeName": "message_id", "AttributeType": "S"},
                    {"AttributeName": "conversation_id", "AttributeType": "S"},
                    {"AttributeName": "created_at", "AttributeType": "S"}
                ],
                global_secondary_indexes=[
                    {
                        'IndexName': 'conversation_id-index',
                        'KeySchema': [
                            {'AttributeName': 'conversation_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            )
            
            # Fields table (stores user email, user_id, location, sowing_date)
            self.fields_table = self._get_or_create_table(
                self.fields_table_name,
                [
                    {"AttributeName": "field_id", "KeyType": "HASH"}
                ],
                [
                    {"AttributeName": "field_id", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "email", "AttributeType": "S"},
                    {"AttributeName": "created_at", "AttributeType": "S"}
                ],
                global_secondary_indexes=[
                    {
                        'IndexName': 'user_id-index',
                        'KeySchema': [
                            {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    },
                    {
                        'IndexName': 'email-index',
                        'KeySchema': [
                            {'AttributeName': 'email', 'KeyType': 'HASH'},
                            {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            )
            
            # OTP table
            self.otp_table = self._get_or_create_table(
                self.otp_table_name,
                [
                    {"AttributeName": "email", "KeyType": "HASH"}
                ],
                [
                    {"AttributeName": "email", "AttributeType": "S"}
                ]
            )
            
            # Sessions table (for multi-user support on Vercel)
            self.sessions_table = self._get_or_create_table(
                self.sessions_table_name,
                [
                    {"AttributeName": "token", "KeyType": "HASH"}
                ],
                [
                    {"AttributeName": "token", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "expires_at", "AttributeType": "S"}
                ],
                global_secondary_indexes=[
                    {
                        'IndexName': 'user_id-index',
                        'KeySchema': [
                            {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            )
            
            print("✓ All DynamoDB tables initialized")
            
        except Exception as e:
            print(f"Error initializing DynamoDB tables: {e}")
            raise
    
    def _get_or_create_table(self, table_name, key_schema, attribute_definitions, global_secondary_indexes=None):
        """Get existing table or create new one"""
        try:
            table = self.dynamodb.Table(table_name)
            table.load()  # Check if table exists
            print(f"✓ Table {table_name} exists")
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Table doesn't exist, create it
                print(f"Creating table {table_name}...")
                try:
                    params = {
                        'TableName': table_name,
                        'KeySchema': key_schema,
                        'AttributeDefinitions': attribute_definitions,
                        'BillingMode': 'PAY_PER_REQUEST'  # Cost-effective
                    }
                    
                    if global_secondary_indexes:
                        params['GlobalSecondaryIndexes'] = global_secondary_indexes
                    
                    table = self.dynamodb.create_table(**params)
                    table.wait_until_exists()
                    print(f"✓ Table {table_name} created")
                    return table
                except Exception as create_err:
                    print(f"Error creating table {table_name}: {create_err}")
                    raise
            else:
                raise
    
    # User operations
    def create_user(self, email: str, password_hash: str = None, username: str = None, verified: bool = False) -> str:
        """Create a new user"""
        import uuid
        user_id = str(uuid.uuid4())
        email_lower = email.lower().strip()
        
        try:
            self.users_table.put_item(
                Item={
                    'email': email_lower,
                    'user_id': user_id,
                    'username': username or email_lower.split('@')[0],
                    'password_hash': password_hash,
                    'created_at': datetime.now().isoformat(),
                    'verified': verified
                },
                ConditionExpression='attribute_not_exists(email)'  # Prevent duplicates
            )
            print(f"User created: {email_lower} (verified: {verified})")
            return user_id
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Email already exists")
            raise
    
    def update_user_verified(self, email: str, verified: bool = True):
        """Update user's verified status"""
        try:
            self.users_table.update_item(
                Key={'email': email.lower().strip()},
                UpdateExpression='SET verified = :verified',
                ExpressionAttributeValues={':verified': verified}
            )
            print(f"User {email} verification status updated to {verified}")
        except Exception as e:
            print(f"Error updating user verification: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            response = self.users_table.get_item(
                Key={'email': email.lower().strip()}
            )
            return response.get('Item')
        except ClientError as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by user_id using GSI"""
        try:
            response = self.users_table.query(
                IndexName='user_id-index',
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def authenticate_user(self, email: str, password_hash: str) -> bool:
        """Verify user password hash"""
        user = self.get_user_by_email(email)
        if not user:
            return False
        return user.get('password_hash') == password_hash
    
    # Conversation operations
    def create_conversation(self, user_id: str, title: str = None) -> str:
        """Create a new conversation"""
        import uuid
        conversation_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        try:
            self.conversations_table.put_item(
                Item={
                    'conversation_id': conversation_id,
                    'user_id': user_id,
                    'title': title or f"Chat {now[:10]}",
                    'created_at': now,
                    'updated_at': now
                }
            )
            return conversation_id
        except Exception as e:
            print(f"Error creating conversation: {e}")
            raise
    
    def get_user_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversations for a user"""
        try:
            response = self.conversations_table.query(
                IndexName='user_id-index',
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id},
                ScanIndexForward=False  # Descending order (newest first)
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def update_conversation(self, conversation_id: str):
        """Update conversation's updated_at timestamp"""
        try:
            self.conversations_table.update_item(
                Key={'conversation_id': conversation_id},
                UpdateExpression='SET updated_at = :now',
                ExpressionAttributeValues={':now': datetime.now().isoformat()}
            )
        except Exception as e:
            print(f"Error updating conversation: {e}")
    
    # Message operations
    def add_message(self, conversation_id: str, role: str, content: str, metadata: Dict = None) -> str:
        """Add a message to a conversation"""
        import uuid
        message_id = str(uuid.uuid4())
        
        # Data-security: sanitize stored content to strip PII/URLs and cap length
        content = self._sanitize_content(content)
        
        try:
            self.messages_table.put_item(
                Item={
                    'message_id': message_id,
                    'conversation_id': conversation_id,
                    'role': role,
                    'content': content,
                    'metadata': json.dumps(metadata) if metadata else None,
                    'created_at': datetime.now().isoformat()
                }
            )
            
            # Update conversation timestamp
            self.update_conversation(conversation_id)
            
            return message_id
        except Exception as e:
            print(f"Error adding message: {e}")
            raise
    
    def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """Get all messages for a conversation"""
        try:
            response = self.messages_table.query(
                IndexName='conversation_id-index',
                KeyConditionExpression='conversation_id = :cid',
                ExpressionAttributeValues={':cid': conversation_id},
                ScanIndexForward=True  # Ascending order (oldest first)
            )
            
            messages = response.get('Items', [])
            # Parse metadata JSON
            for msg in messages:
                if msg.get('metadata'):
                    try:
                        msg['metadata'] = json.loads(msg['metadata'])
                    except:
                        msg['metadata'] = {}
            
            return messages
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []

    # ---------- Data Security Helpers ----------
    def _sanitize_content(self, text: str) -> str:
        """Mask obvious PII and trim oversized payloads before persistence."""
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
    
    # Field operations
    def create_field(self, user_id: str, location: str, sowing_date: str, area_hectares: float = None,
                     email: str = None, latitude: float = None, longitude: float = None) -> str:
        """
        Create a new field with user email, user_id, location, and sowing_date.
        All stored in the fields table for easy querying.
        """
        import uuid
        field_id = str(uuid.uuid4())
        
        # If email not provided, try to get it from user
        if not email:
            user = self.get_user_by_id(user_id)
            if user:
                email = user.get('email')
        
        try:
            item = {
                'field_id': field_id,
                'user_id': user_id,
                'email': email.lower().strip() if email else None,
                'location': location,
                'crop_type': 'potato',
                'sowing_date': sowing_date,
                'is_active': True,
                'created_at': datetime.now().isoformat()
            }
            
            if area_hectares is not None:
                item['area_hectares'] = Decimal(str(area_hectares))
            if latitude is not None:
                item['latitude'] = Decimal(str(latitude))
            if longitude is not None:
                item['longitude'] = Decimal(str(longitude))
            
            self.fields_table.put_item(Item=item)
            print(f"Field created: {field_id} for user {user_id} ({email}) at {location}")
            return field_id
        except Exception as e:
            print(f"Error creating field: {e}")
            raise
    
    def update_field(self, field_id: str, location: str = None, sowing_date: str = None,
                     area_hectares: float = None, latitude: float = None, longitude: float = None) -> bool:
        """Update field information"""
        try:
            update_expression_parts = []
            expression_attribute_values = {}
            
            if location is not None:
                update_expression_parts.append("location = :loc")
                expression_attribute_values[":loc"] = location
            
            if sowing_date is not None:
                update_expression_parts.append("sowing_date = :dos")
                expression_attribute_values[":dos"] = sowing_date
            
            if area_hectares is not None:
                from decimal import Decimal
                update_expression_parts.append("area_hectares = :area")
                expression_attribute_values[":area"] = Decimal(str(area_hectares))
            
            if latitude is not None:
                from decimal import Decimal
                update_expression_parts.append("latitude = :lat")
                expression_attribute_values[":lat"] = Decimal(str(latitude))
            
            if longitude is not None:
                from decimal import Decimal
                update_expression_parts.append("longitude = :lon")
                expression_attribute_values[":lon"] = Decimal(str(longitude))
            
            if not update_expression_parts:
                return False
            
            update_expression = "SET " + ", ".join(update_expression_parts)
            
            self.fields_table.update_item(
                Key={'field_id': field_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            print(f"Field {field_id} updated successfully")
            return True
        except Exception as e:
            print(f"Error updating field: {e}")
            return False
    
    def get_user_fields(self, user_id: str) -> List[Dict]:
        """Get all fields for a user"""
        try:
            response = self.fields_table.query(
                IndexName='user_id-index',
                KeyConditionExpression='user_id = :uid',
                FilterExpression='is_active = :active',
                ExpressionAttributeValues={':uid': user_id, ':active': True}
            )
            
            fields = response.get('Items', [])
            # Convert Decimal to float for JSON serialization
            for field in fields:
                if 'area_hectares' in field:
                    field['area_hectares'] = float(field['area_hectares'])
                if 'latitude' in field:
                    field['latitude'] = float(field['latitude'])
                if 'longitude' in field:
                    field['longitude'] = float(field['longitude'])
            
            return fields
        except Exception as e:
            print(f"Error getting fields: {e}")
            return []
    
    def get_fields_by_email(self, email: str) -> List[Dict]:
        """Get all fields for a user by email"""
        try:
            response = self.fields_table.query(
                IndexName='email-index',
                KeyConditionExpression='email = :email',
                FilterExpression='is_active = :active',
                ExpressionAttributeValues={':email': email.lower().strip(), ':active': True}
            )
            
            fields = response.get('Items', [])
            # Convert Decimal to float for JSON serialization
            for field in fields:
                if 'area_hectares' in field:
                    field['area_hectares'] = float(field['area_hectares'])
                if 'latitude' in field:
                    field['latitude'] = float(field['latitude'])
                if 'longitude' in field:
                    field['longitude'] = float(field['longitude'])
            
            return fields
        except Exception as e:
            print(f"Error getting fields by email: {e}")
            return []
    
    # OTP operations
    def store_otp(self, email: str, otp_code: str, expires_in_minutes: int = 10):
        """Store OTP code"""
        from datetime import timedelta
        expires_at = (datetime.now() + timedelta(minutes=expires_in_minutes)).isoformat()
        
        try:
            self.otp_table.put_item(
                Item={
                    'email': email.lower().strip(),
                    'otp_code': otp_code,
                    'expires_at': expires_at,
                    'verified': False
                }
            )
        except Exception as e:
            print(f"Error storing OTP: {e}")
            raise
    
    def verify_otp(self, email: str, otp_code: str) -> bool:
        """Verify OTP code"""
        try:
            response = self.otp_table.get_item(
                Key={'email': email.lower().strip()}
            )
            
            item = response.get('Item')
            if not item:
                return False
            
            # Check if expired
            expires_at = datetime.fromisoformat(item['expires_at'])
            if datetime.now() > expires_at:
                return False
            
            # Check if already verified
            if item.get('verified'):
                return False
            
            # Verify OTP
            if item['otp_code'] == otp_code:
                # Mark as verified
                self.otp_table.update_item(
                    Key={'email': email.lower().strip()},
                    UpdateExpression='SET verified = :v',
                    ExpressionAttributeValues={':v': True}
                )
                return True
            
            return False
        except Exception as e:
            print(f"Error verifying OTP: {e}")
            return False

# Global instance
_dynamodb_service = None

def get_dynamodb_service() -> Optional[DynamoDBService]:
    """Get or create DynamoDB service instance"""
    global _dynamodb_service
    if _dynamodb_service is None:
        try:
            _dynamodb_service = DynamoDBService()
        except Exception as e:
            print(f"Failed to initialize DynamoDB service: {e}")
            return None
    return _dynamodb_service

