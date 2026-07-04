# Where Data is Stored

## Database Location

### Main Database File
**Location:** `database/potato_care.db` (or `api/database/potato_care.db` if running from api directory)

**Full Path:** `C:\Users\satya\Desktop\Potato-Shield\database\potato_care.db`

This SQLite database contains:
- ✅ **Users** - Email, username, password hash, verification status
- ✅ **OTP Codes** - Temporary OTP codes for email verification
- ✅ **Fields** - User's potato fields (location, sowing date, area)
- ✅ **Conversations** - Chat sessions/conversations
- ✅ **Conversation Messages** - All chat messages
- ✅ **Disease History** - Historical disease records

### How to Access the Database

#### Option 1: Using SQLite Browser (Recommended)
1. Download DB Browser for SQLite: https://sqlitebrowser.org/
2. Open `database/potato_care.db`
3. Browse tables, run queries, view data

#### Option 2: Using Python SQLite
```python
import sqlite3

conn = sqlite3.connect('database/potato_care.db')
cursor = conn.cursor()

# View all users
cursor.execute("SELECT * FROM users")
for row in cursor.fetchall():
    print(row)

conn.close()
```

#### Option 3: Using Command Line
```bash
cd database
sqlite3 potato_care.db

# Then run SQL commands:
.tables          # List all tables
SELECT * FROM users;
SELECT * FROM fields;
.quit
```

## Database Schema

### Users Table
```sql
user_id TEXT PRIMARY KEY
email TEXT UNIQUE NOT NULL
username TEXT
password_hash TEXT
created_at TIMESTAMP
verified BOOLEAN
```

### Fields Table
```sql
field_id TEXT PRIMARY KEY
user_id TEXT (foreign key to users)
location TEXT
crop_type TEXT (default: 'potato')
sowing_date DATE
area_hectares REAL
is_active BOOLEAN
created_at TIMESTAMP
```

### Conversations Table
```sql
conversation_id TEXT PRIMARY KEY
user_id TEXT (foreign key to users)
title TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
```

### Conversation Messages Table
```sql
message_id TEXT PRIMARY KEY
conversation_id TEXT (foreign key to conversations)
role TEXT (user/assistant)
content TEXT
metadata TEXT (JSON)
created_at TIMESTAMP
```

## Short-Term Memory (In-Memory)

**Location:** RAM (not persisted to disk)

Stored in `ShortTermMemory` class in `src/memory/short_term_memory.py`

- Recent conversation history (last 3 chats)
- Session-based (cleared when server restarts)
- Key: `{session_id: deque([messages])}`

## Session Data (In-Memory)

**Location:** RAM (not persisted)

Stored in `api/main.py`:
- `active_sessions` - `{token: user_id}` mapping
- Cleared when server restarts
- Users need to login again after server restart

## Backup Recommendations

### Manual Backup
```bash
# Copy database file
copy database\potato_care.db database\potato_care_backup.db
```

### Automatic Backup Script
Create a backup script that runs daily/weekly to save the database.

## Important Notes

1. **Database is SQLite** - Single file, easy to backup
2. **Location is relative** - Depends on where you run the server from
3. **No data loss** - Database persists even if server restarts
4. **Sessions are temporary** - Active sessions are lost on server restart
5. **Migration is automatic** - Schema updates happen on server start

## Finding Your Database

If you're not sure where your database is:

```bash
# From project root
dir database\*.db

# Or search
dir /s potato_care.db
```

The database file will be created automatically when you first run the server.

