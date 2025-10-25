#!/usr/bin/env python3
"""Create database tables in local PostgreSQL database."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.base import engine, Base
# Import all models to register them with Base
from app.db.models import *  # noqa
from app.db.models_saas import *  # noqa
from app.db.models_tenant_conversations import *  # noqa

def create_tables():
    """Create all database tables."""
    print("Creating database tables in local PostgreSQL...")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("\n✅ All tables created successfully!")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n📋 Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   - {table}")
            
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_tables()
