#!/usr/bin/env python3
"""
Script to create database tables directly using SQLAlchemy.
"""

import os
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.abspath("."))

# Load environment variables
load_dotenv()

# Import the Base class and all models
from app.db.base import Base
from app.db.models import User, Conversation, Message, AgentState, Event, Task, Stakeholder
from app.db.models_updated import Organization, OrganizationUser, SubscriptionPlan, SubscriptionInvoice

def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    
    # Get database URL from environment variable
    database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    # Create engine
    engine = create_engine(database_url)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()
