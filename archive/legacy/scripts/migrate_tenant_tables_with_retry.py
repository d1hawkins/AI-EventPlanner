#!/usr/bin/env python3
import time
import logging
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, TimeoutError

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_with_retry(max_retries=5, delay=10):
    """Run tenant conversation migrations with retry logic for Azure deployment."""
    
    # Get database URL from environment or use default
    database_url = os.getenv('DATABASE_URL', 'postgresql://dbadmin:VM*admin@ai-event-planner-db.postgres.database.azure.com:5432/eventplanner')
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: Creating tenant conversation tables...")
            
            # Import models after path is set
            from app.db.base import Base
            from app.db.models_tenant_conversations import (
                TenantConversation, TenantMessage, TenantAgentState, 
                ConversationContext, ConversationParticipant
            )
            
            engine = create_engine(database_url, connect_args={"connect_timeout": 30})
            
            # Create all tenant conversation tables
            Base.metadata.create_all(engine)
            
            # Verify tables were created
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'tenant_%'
                """))
                tables = [row[0] for row in result.fetchall()]
                
                expected_tables = ['tenant_conversations', 'tenant_messages', 'tenant_agent_states']
                for table in expected_tables:
                    if table in tables:
                        print(f"✅ Table '{table}' created successfully")
                    else:
                        print(f"⚠️ Table '{table}' not found")
            
            print("✅ Tenant conversation tables migration completed successfully")
            return True
            
        except (OperationalError, TimeoutError) as e:
            if "connection" in str(e).lower() and attempt < max_retries - 1:
                print(f"⚠️ Connection failed (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                print(f"Error: {e}")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                continue
            else:
                print(f"❌ Migration failed: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    return False

if __name__ == "__main__":
    success = migrate_with_retry()
    sys.exit(0 if success else 1)
