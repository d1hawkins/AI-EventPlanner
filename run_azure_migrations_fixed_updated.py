#!/usr/bin/env python
"""
Run Azure Migrations Script

This script runs the Alembic migrations on the Azure PostgreSQL database.
"""

import os
import sys
import argparse
import subprocess

def test_connection():
    """Test the connection to the PostgreSQL database."""
    try:
        import psycopg2
    except ImportError:
        print("Installing psycopg2-binary...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        import psycopg2
    
    # Get database connection details from environment variables
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("DATABASE_URL environment variable not set. Using default values.")
        # Use default connection parameters as fallback
        host = "ai-event-planner-db.postgres.database.azure.com"
        port = 5432
        dbname = "eventplanner"
        user = "dbadmin@ai-event-planner-db"  # Azure PostgreSQL requires username@hostname format
        password = "VM*admin"
        sslmode = "require"
    else:
        # Parse the DATABASE_URL
        print(f"Using DATABASE_URL from environment: {database_url.split('@')[0].split(':')[0]}:***@***")
        try:
            # Format: postgresql://username:password@hostname:port/dbname
            # or: postgresql://username@hostname:password@hostname:port/dbname (Azure format)
            if '@' in database_url.split('://')[1].split(':')[0]:
                # Azure format with username@hostname
                user_host = database_url.split('://')[1].split(':')[0]
                user = user_host
                password = database_url.split(':')[2].split('@')[0]
                host_port = database_url.split('@')[1].split('/')[0]
                if ':' in host_port:
                    host = host_port.split(':')[0]
                    port = int(host_port.split(':')[1])
                else:
                    host = host_port
                    port = 5432
                dbname = database_url.split('/')[-1]
            else:
                # Standard format
                user = database_url.split('://')[1].split(':')[0]
                password = database_url.split(':')[2].split('@')[0]
                host_port = database_url.split('@')[1].split('/')[0]
                if ':' in host_port:
                    host = host_port.split(':')[0]
                    port = int(host_port.split(':')[1])
                else:
                    host = host_port
                    port = 5432
                dbname = database_url.split('/')[-1]
            sslmode = "require"
        except Exception as e:
            print(f"Error parsing DATABASE_URL: {e}")
            print("Using default connection parameters.")
            host = "ai-event-planner-db.postgres.database.azure.com"
            port = 5432
            dbname = "eventplanner"
            user = "dbadmin@ai-event-planner-db"
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

def run_migrations(args):
    """Run the Alembic migrations."""
    print("Running Alembic migrations...")
    
    # Add the project root to the Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, project_root)
    
    try:
        # Run the Alembic migrations
        print("Running Alembic migrations...")
        
        # Use subprocess to run the alembic command
        cmd = ["alembic", "upgrade", "head"]
        # Alembic doesn't support --verbose flag for upgrade command
        env = os.environ.copy()
        if args.verbose:
            env["PYTHONVERBOSE"] = "1"
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print(result.stdout)
            print("✅ Migrations completed successfully.")
            return True
        else:
            print(f"Error running migrations: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running migrations: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run Azure Migrations Script")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Test the connection
    if not test_connection():
        return 1
    
    # Run the migrations
    if not run_migrations(args):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
