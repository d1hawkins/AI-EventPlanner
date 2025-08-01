#!/usr/bin/env python
"""
Update Events with Organizations Script

This script updates the events with organization IDs.
"""

import os
import sys
import argparse
import random

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

def update_events():
    """Update the events with organization IDs."""
    print("Updating events with organization IDs...")
    
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
        
        # Import the SQLAlchemy models and session
        from sqlalchemy.orm import Session
        from app.db.base import engine
        from app.db.models import Event
        
        # Create a session
        session = Session(engine)
        
        # Get all events
        events = session.query(Event).all()
        
        # Get all organization IDs using raw SQL with psycopg2
        import psycopg2
        
        # Connect to the database
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            sslmode=sslmode
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Get all organization IDs
        cursor.execute("SELECT id FROM organizations")
        org_ids = [row[0] for row in cursor]
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        if not org_ids:
            print("No organizations found. Please run seed_azure_db_saas.py first.")
            session.close()
            return False
        
        # Update each event with a random organization ID
        for event in events:
            org_id = random.choice(org_ids)
            event.organization_id = org_id
            print(f"Updating event {event.id} with organization ID {org_id}")
        
        # Commit the changes
        session.commit()
        
        # Close the session
        session.close()
        
        print("✅ Events updated successfully.")
        return True
    except ImportError as e:
        print(f"Error importing SQLAlchemy models: {e}")
        print("Make sure you're running this script from the project root directory.")
        return False
    except Exception as e:
        print(f"Error updating events: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Update Events with Organizations Script")
    
    # Test the connection
    if not test_connection():
        return 1
    
    # Update the events
    if not update_events():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
