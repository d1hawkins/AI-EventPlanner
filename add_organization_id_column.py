"""
Migration script to add organization_id column to conversations table.

This script adds the missing organization_id column to the conversations table,
which is required for the tenant-aware state manager to work properly.
"""

import sqlite3
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get database URL from environment or use default
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///./app.db')

def add_organization_id_column():
    """Add organization_id column to conversations table."""
    try:
        # Create engine and session
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if the column already exists
        try:
            session.execute(text("SELECT organization_id FROM conversations LIMIT 1"))
            print("Column 'organization_id' already exists in conversations table.")
            return True
        except Exception:
            # Column doesn't exist, proceed with adding it
            pass
        
        # Add the column
        if 'sqlite' in DATABASE_URL:
            # SQLite syntax
            session.execute(text(
                "ALTER TABLE conversations ADD COLUMN organization_id INTEGER"
            ))
        else:
            # PostgreSQL syntax
            session.execute(text(
                "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS organization_id INTEGER"
            ))
        
        # Commit the changes
        session.commit()
        print("Successfully added 'organization_id' column to conversations table.")
        return True
    except Exception as e:
        print(f"Error adding organization_id column: {str(e)}")
        return False

if __name__ == "__main__":
    add_organization_id_column()
