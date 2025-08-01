#!/usr/bin/env python
"""
Update Event Model Script

This script updates the Event model in the database to add the organization_id column.
"""

import os
import sys
import argparse

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

def update_event_model():
    """Update the Event model in the database."""
    print("Updating Event model in the database...")
    
    # Use hardcoded connection parameters for Azure PostgreSQL
    host = "ai-event-planner-db.postgres.database.azure.com"
    port = 5432
    dbname = "eventplanner"
    user = "dbadmin@ai-event-planner-db"
    password = "VM*admin"
    sslmode = "require"
    
    try:
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
        
        # Check if the organization_id column already exists
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'events' AND column_name = 'organization_id';")
        if cursor.fetchone():
            print("organization_id column already exists in events table.")
        else:
            # Add the organization_id column to the events table
            print("Adding organization_id column to events table...")
            cursor.execute("ALTER TABLE events ADD COLUMN organization_id INTEGER;")
            
            # Add the foreign key constraint
            print("Adding foreign key constraint...")
            cursor.execute("ALTER TABLE events ADD CONSTRAINT fk_events_organization FOREIGN KEY (organization_id) REFERENCES organizations (id);")
            
            # Commit the changes
            conn.commit()
            print("✅ Event model updated successfully.")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        return True
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return False
    except Exception as e:
        print(f"Error updating Event model: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Update Event Model Script")
    
    # Test the connection
    if not test_connection():
        return 1
    
    # Update the Event model
    if not update_event_model():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
