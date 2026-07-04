# Fix Database Schema Error

If you see `sqlite3.OperationalError: no such column: email`, follow these steps:

## Option 1: Restart Server (Recommended)

The migration runs automatically when you restart the server:

1. **Stop the current server** (Ctrl+C in the terminal running the server)

2. **Restart the server:**
   ```bash
   python main.py
   ```

You should see: `"Migrating database schema..."` and `"Database migration completed!"`

## Option 2: Run Migration Manually

If automatic migration doesn't work:

```bash
cd api
python migrate_database.py
```

## Option 3: Delete Database (Fresh Start)

If you don't have important data, delete the database and let it recreate:

```bash
# Delete the database file
del database\potato_care.db

# Restart server - it will create a new database with correct schema
python main.py
```

## Verify Migration

After migration, the server should start without errors and registration should work.

