# src/memory/long_term_memory.py
import sqlite3
import os
from passlib.hash import bcrypt
from datetime import datetime
from typing import Optional, Dict, List

# Check if we should use DynamoDB (for production/Vercel)
USE_DYNAMODB = os.getenv('USE_DYNAMODB', 'false').lower() == 'true'

if USE_DYNAMODB:
    from .dynamodb_memory import DynamoDBLongTermMemory
    LongTermMemory = DynamoDBLongTermMemory
else:
    # SQLite implementation (for local development)
    class LongTermMemory:
        """Manages persistent user data and field information"""
        
        def __init__(self, db_path: str = "database/potato_care.db"):
            self.db_path = db_path
            import os
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self._init_database()
        
        def _init_database(self):
            """Initialize SQLite schema"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if users table exists and what columns it has
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                # Table exists, check if it needs migration
                cursor.execute("PRAGMA table_info(users)")
                columns = [column[1] for column in cursor.fetchall()]
                
                # Migrate old schema to new schema
                if 'email' not in columns:
                    # Old schema - migrate to new schema
                    print("Migrating database schema...")
                    
                    # Create new users table with email
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users_new (
                            user_id TEXT PRIMARY KEY,
                            email TEXT UNIQUE NOT NULL,
                            username TEXT,
                            password_hash TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            verified BOOLEAN DEFAULT 0
                        )
                    ''')
                    
                    # If old table has data, try to migrate (skip if username column doesn't exist)
                    if 'username' in columns:
                        cursor.execute("SELECT user_id, username, password_hash, created_at FROM users")
                        old_users = cursor.fetchall()
                        
                        for user in old_users:
                            user_id, username, password_hash, created_at = user
                            # Use username as email if no email exists
                            email = username if username else f"user_{user_id[:8]}@migrated.local"
                            cursor.execute('''
                                INSERT OR IGNORE INTO users_new (user_id, email, username, password_hash, created_at)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (user_id, email, username, password_hash, created_at))
                    
                    # Drop old table and rename new one
                    cursor.execute("DROP TABLE users")
                    cursor.execute("ALTER TABLE users_new RENAME TO users")
                    conn.commit()
                    print("Database migration completed!")
                else:
                    # Email column exists, but check if password_hash exists
                    if 'password_hash' not in columns:
                        # Add password_hash column if missing
                        try:
                            cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
                            conn.commit()
                            print("Added password_hash column to users table")
                        except sqlite3.OperationalError:
                            pass  # Column might already exist
            else:
                # Table doesn't exist, create new schema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        username TEXT,
                        password_hash TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        verified BOOLEAN DEFAULT 0
                    )
                ''')
            
            conn.commit()
            
            # OTP table for email verification
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS otp_codes (
                    email TEXT PRIMARY KEY,
                    otp_code TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    verified BOOLEAN DEFAULT 0
                )
            ''')
            
            # Conversations/Chats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Conversation messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            ''')
            
            # Fields table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fields (
                    field_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    location TEXT NOT NULL,  -- "lat,lon" or city name
                    crop_type TEXT DEFAULT 'potato',
                    sowing_date DATE NOT NULL,
                    area_hectares REAL,
                    latitude REAL,
                    longitude REAL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Ensure latitude/longitude columns exist for older schemas
            cursor.execute("PRAGMA table_info(fields)")
            field_columns = [column[1] for column in cursor.fetchall()]
            if 'latitude' not in field_columns:
                try:
                    cursor.execute("ALTER TABLE fields ADD COLUMN latitude REAL")
                except sqlite3.OperationalError:
                    pass
            if 'longitude' not in field_columns:
                try:
                    cursor.execute("ALTER TABLE fields ADD COLUMN longitude REAL")
                except sqlite3.OperationalError:
                    pass
            
            # Disease history (for learning patterns)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS disease_history (
                    report_id TEXT PRIMARY KEY,
                    field_id TEXT NOT NULL,
                    disease_type TEXT NOT NULL,
                    detected_date DATE NOT NULL,
                    crop_stage TEXT,
                    severity TEXT,
                    treatment_applied TEXT,
                    outcome TEXT,
                    FOREIGN KEY (field_id) REFERENCES fields(field_id)
                )
            ''')
            
            conn.commit()
            conn.close()
        
        def create_user(self, email: str, password: str = None, username: str = None, verified: bool = False) -> str:
            """Create new user with email and optional password"""
            import uuid
            email = email.lower().strip()
            user_id = str(uuid.uuid4())
            
            # Hash password if provided
            password_hash = None
            if password:
                try:
                    # Ensure password is a string
                    password_str = str(password)
                    password_hash = bcrypt.hash(password_str)
                    print(f"Password hashed successfully for user: {email}")
                except Exception as e:
                    print(f"Error hashing password: {e}")
                    raise ValueError(f"Failed to hash password: {str(e)}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (user_id, email, username, password_hash, verified) VALUES (?, ?, ?, ?, ?)",
                    (user_id, email, username or email.split('@')[0], password_hash, 1 if verified else 0)
                )
                conn.commit()
                print(f"User created successfully: {email} (verified: {verified})")
                return user_id
            except sqlite3.IntegrityError as e:
                print(f"Integrity error creating user {email}: {e}")
                raise ValueError("Email already exists")
            finally:
                conn.close()
        
        def authenticate_with_password(self, email: str, password: str) -> Optional[str]:
            """Authenticate user with email and password"""
            email = email.lower().strip()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute(
                    "SELECT user_id, password_hash FROM users WHERE email = ?",
                    (email,)
                )
                result = cursor.fetchone()
                
                if not result:
                    print(f"User not found for email: {email}")
                    return None
                
                user_id, stored_hash = result
                
                # If no password hash, user was created with OTP only
                if not stored_hash:
                    print(f"User {email} has no password hash (OTP-only user)")
                    return None
                
                # Verify password - handle both string and bytes
                try:
                    # Ensure password is a string
                    password_str = str(password) if password else ""
                    
                    # Verify password
                    if bcrypt.verify(password_str, stored_hash):
                        print(f"Password verified for user: {email}")
                        return user_id
                    else:
                        print(f"Password verification failed for user: {email}")
                        return None
                except Exception as e:
                    print(f"Error verifying password for {email}: {e}")
                    return None
                    
            except Exception as e:
                print(f"Database error during authentication: {e}")
                return None
            finally:
                conn.close()
        
        def store_otp(self, email: str, otp_code: str, expires_in_minutes: int = 10):
            """Store OTP code for email verification"""
            from datetime import datetime, timedelta
            expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO otp_codes (email, otp_code, expires_at, verified)
                   VALUES (?, ?, ?, 0)""",
                (email, otp_code, expires_at.isoformat())
            )
            conn.commit()
            conn.close()
        
        def verify_otp(self, email: str, otp_code: str) -> bool:
            """Verify OTP code"""
            from datetime import datetime
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT otp_code, expires_at FROM otp_codes WHERE email = ? AND verified = 0",
                (email,)
            )
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False
            
            stored_otp, expires_at = result
            if datetime.fromisoformat(expires_at) < datetime.now():
                return False
            
            if stored_otp == otp_code:
                # Mark OTP as verified and mark user as verified
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE otp_codes SET verified = 1 WHERE email = ?", (email,))
                cursor.execute("UPDATE users SET verified = 1 WHERE email = ?", (email,))
                conn.commit()
                conn.close()
                return True
            
            return False
        
        def get_user_by_email(self, email: str) -> Optional[Dict]:
            """Get user by email"""
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            result = cursor.fetchone()
            conn.close()
            return dict(result) if result else None
        
        def create_conversation(self, user_id: str, title: str = None) -> str:
            """Create a new conversation"""
            import uuid
            conversation_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (conversation_id, user_id, title) VALUES (?, ?, ?)",
                (conversation_id, user_id, title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            )
            conn.commit()
            conn.close()
            return conversation_id
        
        def get_user_conversations(self, user_id: str) -> List[Dict]:
            """Get all conversations for a user"""
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,)
            )
            conversations = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return conversations
        
        def add_message_to_conversation(self, conversation_id: str, role: str, content: str, metadata: Dict = None):
            """Add message to a conversation"""
            import uuid
            import json
            message_id = str(uuid.uuid4())
            
            # Data-security: sanitize stored content to strip PII/URLs and cap length
            content = self._sanitize_content(content)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO conversation_messages (message_id, conversation_id, role, content, metadata)
                   VALUES (?, ?, ?, ?, ?)""",
                (message_id, conversation_id, role, content, json.dumps(metadata) if metadata else None)
            )
            # Update conversation updated_at
            cursor.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE conversation_id = ?",
                (conversation_id,)
            )
            conn.commit()
            conn.close()
            return message_id
        
        def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
            """Get all messages for a conversation"""
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversation_messages WHERE conversation_id = ? ORDER BY created_at ASC",
                (conversation_id,)
            )
            messages = []
            for row in cursor.fetchall():
                msg = dict(row)
                if msg.get('metadata'):
                    import json
                    try:
                        msg['metadata'] = json.loads(msg['metadata'])
                    except:
                        msg['metadata'] = {}
                messages.append(msg)
            conn.close()
            return messages
        
        def add_field(self, user_id: str, location: str, sowing_date: str, 
                      area_hectares: float = None, field_id: str = None,
                      latitude: float = None, longitude: float = None) -> str:
            """Add a new field for user, or update if field_id is provided"""
            import uuid
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if field_id:
                # Update existing field
                cursor.execute(
                    """UPDATE fields 
                       SET location = ?, sowing_date = ?, area_hectares = ?, 
                           latitude = COALESCE(?, latitude), 
                           longitude = COALESCE(?, longitude)
                       WHERE field_id = ? AND user_id = ?""",
                    (location, sowing_date, area_hectares, latitude, longitude, field_id, user_id)
                )
                conn.commit()
                conn.close()
                return field_id
            else:
                # Create new field
                field_id = str(uuid.uuid4())
                cursor.execute(
                    """INSERT INTO fields 
                       (field_id, user_id, location, sowing_date, area_hectares, latitude, longitude)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (field_id, user_id, location, sowing_date, area_hectares, latitude, longitude)
                )
                conn.commit()
                conn.close()
                return field_id

        # ---------- Data Security Helpers ----------
        def _sanitize_content(self, text: str) -> str:
            """Mask obvious PII and trim oversized payloads before persistence."""
            if not text:
                return text
            import re
            cleaned = text
            # Mask emails, phones, long digit runs
            patterns = [
                re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
                re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),
                re.compile(r"\b\d{12,19}\b"),
            ]
            for pat in patterns:
                cleaned = pat.sub("[REDACTED]", cleaned)
            # Strip/mark URLs
            cleaned = re.sub(r"https?://\S+", "[LINK]", cleaned)
            # Cap length
            return cleaned[:2000]
        
        def update_field(self, field_id: str, user_id: str, location: str = None, 
                        sowing_date: str = None, area_hectares: float = None,
                        latitude: float = None, longitude: float = None) -> bool:
            """Update an existing field"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            values = []
            
            if location is not None:
                updates.append("location = ?")
                values.append(location)
            if sowing_date is not None:
                updates.append("sowing_date = ?")
                values.append(sowing_date)
            if area_hectares is not None:
                updates.append("area_hectares = ?")
                values.append(area_hectares)
            if latitude is not None:
                updates.append("latitude = ?")
                values.append(latitude)
            if longitude is not None:
                updates.append("longitude = ?")
                values.append(longitude)
            
            if not updates:
                conn.close()
                return False
            
            values.extend([field_id, user_id])
            query = f"UPDATE fields SET {', '.join(updates)} WHERE field_id = ? AND user_id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            updated = cursor.rowcount > 0
            conn.close()
            return updated
        
        def get_user_profile(self, user_id: str) -> Dict:
            """Retrieve complete user profile with all fields"""
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get user data
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user_row = cursor.fetchone()
            if not user_row:
                conn.close()
                return None
            user = dict(user_row)
            
            # Get all active fields
            cursor.execute(
                "SELECT * FROM fields WHERE user_id = ? AND is_active = 1",
                (user_id,)
            )
            user['fields'] = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return user
        
        def log_disease_event(self, field_id: str, disease_type: str, 
                             crop_stage: str, severity: str):
            """Track disease occurrences for pattern learning"""
            import uuid
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO disease_history 
                   (report_id, field_id, disease_type, detected_date, crop_stage, severity)
                   VALUES (?, ?, ?, date('now'), ?, ?)""",
                (str(uuid.uuid4()), field_id, disease_type, crop_stage, severity)
            )
            conn.commit()
            conn.close()