#!/usr/bin/env python
"""
Create Azure Tables Direct

This script creates the database tables directly using SQLAlchemy models.
It's used as a fallback if the Alembic migrations fail.
"""

import os
import sys
import argparse

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

def create_tables():
    """Create database tables directly using SQLAlchemy models."""
    try:
        # Import the SQLAlchemy models and engine
        from app.db.base import Base
        from app.db.session import engine
        
        # Import all models to ensure they're registered with the metadata
        from app.db.models import User, Event, Organization, Conversation, Message
        from app.db.models_saas import Subscription, SubscriptionPlan, UserOrganization
        from app.db.models_updated import Event, Organization, User
        
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully.")
        return True
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Create Azure Tables Direct")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Create the tables
    if not create_tables():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
