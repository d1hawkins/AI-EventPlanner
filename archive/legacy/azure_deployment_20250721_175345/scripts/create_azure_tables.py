#!/usr/bin/env python
"""
Create Azure Database Tables Script

This script creates the database tables directly using SQLAlchemy models,
without relying on alembic migrations.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

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

def create_tables():
    """Create database tables using SQLAlchemy models."""
    print("Creating database tables...")
    
    # Set up the database connection
    host = "ai-event-planner-db.postgres.database.azure.com"
    port = 5432
    dbname = "eventplanner"
    user = "dbadmin@ai-event-planner-db"
    password = "VM*admin"
    sslmode = "require"
    
    # Set the DATABASE_URL environment variable
    os.environ["DATABASE_URL"] = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    
    # Import the SQLAlchemy models and create the tables
    try:
        # Add the project root to the Python path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sys.path.insert(0, project_root)
        
        # Import the SQLAlchemy models
        from app.db.base import Base, engine
        
        # Import all models to ensure they are registered with Base
        from app.db.models import User, Conversation, Message, AgentState, Event, Task, Stakeholder
        
        # Import SaaS models if they exist
        try:
            from app.db.models_saas import Organization, OrganizationUser, SubscriptionPlan, SubscriptionInvoice
            print("SaaS models imported successfully.")
        except ImportError:
            print("SaaS models not found, skipping.")
        
        # Create the tables
        Base.metadata.create_all(bind=engine)
        
        # Print the tables that were created
        print("Tables created:")
        for table in Base.metadata.tables:
            print(f"  - {table}")
        
        print("✅ Database tables created successfully.")
        return True
    except ImportError as e:
        print(f"Error importing SQLAlchemy models: {e}")
        print("Make sure you're running this script from the project root directory.")
        return False
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Create Azure Database Tables Script")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Test the connection
    if not test_connection():
        return 1
    
    # Create the tables
    if not create_tables():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
