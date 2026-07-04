"""
Script to check database location and contents
"""
import os
import sqlite3
import sys

# Get database path
db_paths = [
    "database/potato_care.db",
    "../database/potato_care.db",
    "api/database/potato_care.db",
]

print("🔍 Searching for database...")
print("=" * 50)

found_db = None
for db_path in db_paths:
    if os.path.exists(db_path):
        found_db = os.path.abspath(db_path)
        print(f"✅ Database found at: {found_db}")
        break

if not found_db:
    print("❌ Database not found. It will be created on first server start.")
    print("   Expected location: database/potato_care.db")
    sys.exit(0)

print(f"\n📊 Database Size: {os.path.getsize(found_db) / 1024:.2f} KB")
print("\n" + "=" * 50)

# Connect and show tables
try:
    conn = sqlite3.connect(found_db)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n📋 Tables in database ({len(tables)}):")
    for table in tables:
        table_name = table[0]
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        # Get columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        
        print(f"\n  📑 {table_name} ({count} rows)")
        print(f"     Columns: {', '.join(col_names)}")
    
    # Show sample users
    print("\n" + "=" * 50)
    print("\n👥 Users in database:")
    cursor.execute("SELECT user_id, email, username, created_at FROM users LIMIT 10")
    users = cursor.fetchall()
    
    if users:
        for user in users:
            user_id, email, username, created_at = user
            print(f"  - {email} ({username or 'no username'}) - {created_at}")
    else:
        print("  No users found")
    
    # Show sample fields
    print("\n" + "=" * 50)
    print("\n🌾 Fields in database:")
    cursor.execute("SELECT field_id, user_id, location, sowing_date FROM fields LIMIT 10")
    fields = cursor.fetchall()
    
    if fields:
        for field in fields:
            field_id, user_id, location, sowing_date = field
            print(f"  - {location} (sowed: {sowing_date})")
    else:
        print("  No fields found")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error reading database: {e}")

print("\n" + "=" * 50)
print("✅ Database check complete!")

