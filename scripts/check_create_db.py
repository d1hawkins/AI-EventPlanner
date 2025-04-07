#!/usr/bin/env python
"""
Check if the database exists and create it if it doesn't.
This script is used by the run-migrations.sh script to check if the eventplanner database
exists on the Azure PostgreSQL server and create it if it doesn't.
"""

import sys
import psycopg2

def check_create_database():
    """Check if the database exists and create it if it doesn't."""
    # Connection parameters for Azure PostgreSQL
    host = "ai-event-planner-db.postgres.database.azure.com"
    port = 5432
    dbname = "postgres"  # Connect to the default postgres database first
    user = "dbadmin@ai-event-planner-db"  # Azure PostgreSQL requires username@hostname format
    password = "VM*admin"
    sslmode = "require"
    
    try:
        # Connect to the default postgres database
        print(f"Connecting to PostgreSQL server at {host}...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            sslmode=sslmode
        )
        
        # Set autocommit to True to create database
        conn.autocommit = True
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if the eventplanner database exists
        print("Checking if 'eventplanner' database exists...")
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'eventplanner'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating 'eventplanner' database...")
            cursor.execute("CREATE DATABASE eventplanner")
            print("Database 'eventplanner' created successfully!")
        else:
            print("Database 'eventplanner' already exists.")
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
        print("Database check completed successfully.")
        return 0
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL server: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_create_database())
