#!/usr/bin/env python
"""
Create Azure Tables Script

This script creates the database tables on the Azure PostgreSQL database.
"""

import os
import sys
import argparse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def test_connection():
    """Test the connection to the PostgreSQL database."""
    try:
        import psycopg2
    except ImportError:
        print("Installing psycopg2-binary...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        import psycopg2
    
    # Use hardcoded connection parameters for Azure PostgreSQL
    host = "ai-event-planner-db.postgres.database.azure.com"
    port = 5432
    dbname = "eventplanner"
    user = "dbadmin@ai-event-planner-db"  # Azure PostgreSQL requires username@hostname format
    password = "VM*admin"
    sslmode = "require"
    
    print(f"Testing connection to PostgreSQL database...")
    print(f"Connection details:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Database: {dbname}")
    print(f"  Username: {user}")
    print(f"  Password: {'*' * len(password)}")
    
    try:
        # Try to connect to the database
        print("Connecting to database...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            sslmode=sslmode
        )
        
        # Test the connection
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"Connected to PostgreSQL: {version[0]}")
        
        conn.close()
        print("✅ Connection test successful.")
        return True
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_tables(args):
    """Create the database tables."""
    print("Creating database tables...")
    
    # Set up the database connection
    host = "ai-event-planner-db.postgres.database.azure.com"
    port = 5432
    dbname = "eventplanner"
    user = "dbadmin@ai-event-planner-db"
    password = "VM*admin"
    sslmode = "require"
    
    # Create the SQLAlchemy engine
    database_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(database_url)
    
    # Add the project root to the Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, project_root)
    
    try:
        # Import the SQLAlchemy models
        from app.db.models import Base as BaseModel
        from app.db.models import User, Conversation, Message, AgentState, Event, Task, Stakeholder
        
        # Create the tables
        print("Creating tables...")
        BaseModel.metadata.create_all(engine)
        
        # Try to import SaaS models if they exist
        try:
            from app.db.models_saas import Base as BaseSaasModel
            from app.db.models_saas import Organization, OrganizationUser, SubscriptionPlan, SubscriptionInvoice
            
            # Create the SaaS tables
            print("Creating SaaS tables...")
            BaseSaasModel.metadata.create_all(engine)
            print("✅ All tables created successfully.")
        except ImportError:
            print("SaaS models not found, skipping SaaS tables.")
            print("✅ Basic tables created successfully.")
        
        return True
    except ImportError as e:
        print(f"Error importing SQLAlchemy models: {e}")
        print("Make sure you're running this script from the project root directory.")
        return False
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Create Azure Tables Script")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Test the connection
    if not test_connection():
        return 1
    
    # Create the tables
    if not create_tables(args):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
