#!/usr/bin/env python
"""
Test PostgreSQL Connection

This script tests the connection to the PostgreSQL database specified in the .env.azure file.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

def load_azure_env():
    """Load environment variables from .env.azure file."""
    print("Loading environment variables from .env.azure...")
    if not os.path.exists(".env.azure"):
        print("Error: .env.azure file not found.")
        return False
    
    # Read the .env.azure file directly to get the DATABASE_URL
    with open(".env.azure", "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("DATABASE_URL="):
                # Extract the DATABASE_URL value
                database_url = line[len("DATABASE_URL="):].strip()
                # Remove any comments
                if "#" in database_url:
                    database_url = database_url.split("#")[0].strip()
                # Set the environment variable
                os.environ["DATABASE_URL"] = database_url
                print(f"✅ Loaded DATABASE_URL from .env.azure")
                return True
    
    print("Error: DATABASE_URL not found in .env.azure file.")
    return False

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
        
        # Check for common connection issues
        if "could not connect to server" in str(e):
            print("Possible causes:")
            print("  - The server is not running")
            print("  - The server is behind a firewall")
            print("  - The server address is incorrect")
        elif "password authentication failed" in str(e):
            print("Possible causes:")
            print("  - The username or password is incorrect")
        elif "database" in str(e) and "does not exist" in str(e):
            print("Possible causes:")
            print("  - The database name is incorrect")
        
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test PostgreSQL Connection")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Load environment variables from .env.azure
    if not load_azure_env():
        return 1
    
    # Test the connection
    if not test_connection():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
