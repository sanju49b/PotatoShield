# src/memory/long_term_memory.py
import sqlite3
from passlib.hash import bcrypt
from datetime import datetime
from typing import Optional, Dict, List

class LongTermMemory:
    """Manages persistent user data and field information"""
    
    def __init__(self, db_path: str = "database/potato_care.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
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
    
    def create_user(self, username: str, password: str) -> str:
        """Create new user with hashed password"""
        import uuid
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hash(password)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (user_id, username, password_hash) VALUES (?, ?, ?)",
                (user_id, username, password_hash)
            )
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            raise ValueError("Username already exists")
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Verify credentials and return user_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, password_hash FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result and bcrypt.verify(password, result[1]):
            return result[0]
        return None
    
    def add_field(self, user_id: str, location: str, sowing_date: str, 
                  area_hectares: float = None) -> str:
        """Add a new field for user"""
        import uuid
        field_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO fields 
               (field_id, user_id, location, sowing_date, area_hectares)
               VALUES (?, ?, ?, ?, ?)""",
            (field_id, user_id, location, sowing_date, area_hectares)
        )
        conn.commit()
        conn.close()
        return field_id
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Retrieve complete user profile with all fields"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get user data
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = dict(cursor.fetchone())
        
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