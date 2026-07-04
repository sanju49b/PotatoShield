"""
Database migration script to add email column to existing database
Run this once to migrate your database
"""
import sqlite3
import os

db_path = "database/potato_care.db"

if not os.path.exists(db_path):
    print("Database doesn't exist yet. It will be created automatically.")
    exit(0)

print("Migrating database...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current schema
cursor.execute("PRAGMA table_info(users)")
columns = [column[1] for column in cursor.fetchall()]
print(f"Current columns: {columns}")

if 'email' not in columns:
    print("Migrating users table to include email column...")
    
    # Create new table with email
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
    
    # Migrate existing data
    if 'username' in columns:
        cursor.execute("SELECT user_id, username, password_hash, created_at FROM users")
        old_users = cursor.fetchall()
        
        for user in old_users:
            user_id, username, password_hash, created_at = user
            # Use username as email if available, otherwise create placeholder
            email = username if username and '@' in username else f"user_{user_id[:8]}@migrated.local"
            cursor.execute('''
                INSERT OR IGNORE INTO users_new (user_id, email, username, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, email, username, password_hash, created_at))
    
    # Replace old table
    cursor.execute("DROP TABLE users")
    cursor.execute("ALTER TABLE users_new RENAME TO users")
    conn.commit()
    print("✓ Migration completed successfully!")
else:
    print("✓ Database already has email column. No migration needed.")

conn.close()
print("Done!")

