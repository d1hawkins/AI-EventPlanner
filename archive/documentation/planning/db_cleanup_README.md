# Database Cleanup Scripts

This directory contains scripts for cleaning up the database, particularly for testing purposes when you want to start with a clean slate.

## Available Scripts

### 1. `clear_user_conversations.py`

A command-line script that deletes all conversations for a specific user.

**Usage:**
```bash
./clear_user_conversations.py --identifier <email_or_username_or_id> --type <email|username|id>
```

**Example:**
```bash
./clear_user_conversations.py --identifier test@example.com --type email
```

### 2. `clear_conversations.py`

An interactive script that provides a menu-driven interface for clearing conversations. This script can also be imported and used programmatically in other Python scripts.

**Usage as a script:**
```bash
./clear_conversations.py
```
Then follow the interactive prompts.

**Usage as a module:**
```python
from clear_conversations import clear_by_email, clear_by_username, clear_by_id, clear_all

# Clear conversations for a user by email
success, message = clear_by_email("test@example.com")
print(message)

# Clear conversations for a user by username
success, message = clear_by_username("testuser")
print(message)

# Clear conversations for a user by ID
success, message = clear_by_id(1)
print(message)

# Clear all conversations
success, message = clear_all()
print(message)
```

### 3. `reset_db.py`

A simple script that clears all conversations in the database with a single command.

**Usage:**
```bash
./reset_db.py
```

## How It Works

These scripts connect to the database using the existing configuration in your application. They use SQLAlchemy to query and delete conversations and related data.

When a conversation is deleted, all related data is also deleted due to the cascade settings in the SQLAlchemy models:
- Messages
- Agent states
- Events
- Tasks
- Stakeholders

## Notes

- These scripts are intended for development and testing purposes only.
- Make sure you have a backup of your database before running these scripts in a production environment.
- The scripts use the database configuration from your `.env` file.
