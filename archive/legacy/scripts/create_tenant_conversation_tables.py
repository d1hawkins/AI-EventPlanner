#!/usr/bin/env python3
"""
Script to create tenant conversation tables directly in the database.
This bypasses the migration system to quickly set up the required tables.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import DATABASE_URL
from app.db.base import Base
from app.db.models_saas import Organization
from app.db.models_updated import User
from app.db.models import Event
from app.db.models_tenant_conversations import (
    TenantConversation, TenantMessage, TenantAgentState, 
    ConversationContext, ConversationParticipant
)

def create_tables():
    """Create all tenant conversation tables."""
    print("Creating tenant conversation tables...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("✅ Tenant conversation tables created successfully!")
    
    # Verify tables were created
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if tables exist by querying them (PostgreSQL)
        tables_to_check = [
            'tenant_conversations',
            'tenant_messages', 
            'tenant_agent_states',
            'conversation_contexts',
            'conversation_participants'
        ]
        
        for table_name in tables_to_check:
            result = session.execute(text(f"SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename='{table_name}'"))
            if result.fetchone():
                print(f"✅ Table '{table_name}' created successfully")
            else:
                print(f"❌ Table '{table_name}' not found")
        
    except Exception as e:
        print(f"Error verifying tables: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_tables()
