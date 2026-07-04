# How to View User Email in DynamoDB

## 📍 Step-by-Step Guide

### Step 1: Open AWS DynamoDB Console
1. Go to: https://console.aws.amazon.com/dynamodb/
2. Make sure you're in the correct AWS region (e.g., `us-east-1`)

### Step 2: Find the Users Table
1. Click **"Tables"** in the left sidebar
2. Look for: **`potato-shield-users`**
3. Click on the table name

### Step 3: View Table Items
1. Click the **"Explore table items"** button (or tab)
2. You'll see all users in the table

### Step 4: Find the Email
The email is the **primary key** of the table, so it's easy to find:

**Table Structure:**
```
Partition Key (Primary Key): email
```

**Example Item:**
```json
{
  "email": "test@example.com",        ← This is the email (primary key)
  "user_id": "abc-123-def-456",
  "username": "testuser",
  "password_hash": "...",
  "created_at": "2024-11-04T...",
  "verified": false
}
```

## 🔍 Quick Ways to Find a User

### Method 1: Browse All Items
1. Click on `potato-shield-users` table
2. Click "Explore table items"
3. Scroll through the list - email is in the first column

### Method 2: Search by Email
1. Click on `potato-shield-users` table
2. Click "Explore table items"
3. Click "Query items" or "Get item"
4. Enter the email in the search field
5. Click "Run"

### Method 3: Use Filter
1. In "Explore table items"
2. Use the filter option
3. Filter by email attribute

## 📊 What You'll See

### Table View
```
┌─────────────────────┬──────────────────────┬─────────────┬──────────────┐
│ email (Partition)  │ user_id              │ username    │ created_at   │
├─────────────────────┼──────────────────────┼─────────────┼──────────────┤
│ test@example.com    │ abc-123-def-456      │ testuser    │ 2024-11-04...│
│ user2@example.com  │ xyz-789-ghi-012      │ user2       │ 2024-11-04...│
└─────────────────────┴──────────────────────┴─────────────┴──────────────┘
```

### JSON View (if available)
```json
{
  "email": "test@example.com",
  "user_id": "abc-123-def-456",
  "username": "testuser",
  "password_hash": "$2b$12$...",
  "created_at": "2024-11-04T18:30:00.000Z",
  "verified": false
}
```

## 🎯 Quick Test

1. **Register a user** in the frontend (e.g., `test@example.com`)
2. **Go to AWS Console** → DynamoDB → Tables
3. **Click** `potato-shield-users`
4. **Click** "Explore table items"
5. **Find** your email in the list!

## 💡 Pro Tips

- **Email is the Primary Key**: It's always visible in the first column
- **Sort**: Click column headers to sort
- **Search**: Use the search/filter box to find specific emails
- **Export**: You can export items to CSV if needed

## 📸 Visual Guide

```
AWS Console
└── DynamoDB
    └── Tables
        └── potato-shield-users  ← Click here
            └── Explore table items  ← Click here
                └── [Your emails listed here]  ← Email is the primary key!
```

---

**The email is always visible because it's the table's primary key!** 🎯

