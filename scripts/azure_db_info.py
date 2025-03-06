#!/usr/bin/env python
"""
Azure Database Information Script

This script provides detailed information about the Azure PostgreSQL database
and the migrations that need to be run.
"""

import os
import sys
import argparse
import subprocess
from dotenv import load_dotenv

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        return result.stdout.strip(), True
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}", False

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
            # Get database version
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"Connected to PostgreSQL: {version[0]}")
            
            # Check if alembic_version table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                );
            """)
            alembic_exists = cursor.fetchone()[0]
            if alembic_exists:
                print("Alembic version table exists.")
                
                # Get current alembic version
                cursor.execute("SELECT version_num FROM alembic_version;")
                version_num = cursor.fetchone()
                if version_num:
                    print(f"Current alembic version: {version_num[0]}")
                else:
                    print("No alembic version found in the table.")
            else:
                print("Alembic version table does not exist. Migrations have not been run yet.")
            
            # List all tables in the database
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            if tables:
                print("\nTables in the database:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("\nNo tables found in the database.")
        
        conn.close()
        print("✅ Connection test successful.")
        return True
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_alembic_migrations():
    """Check the alembic migrations that need to be run."""
    print("\nChecking alembic migrations...")
    
    # Check if alembic is installed
    try:
        import alembic
        print(f"Alembic version: {alembic.__version__}")
    except ImportError:
        print("Installing alembic...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "alembic"])
        import alembic
        print(f"Alembic version: {alembic.__version__}")
    
    # Check the alembic.ini file
    if os.path.exists("alembic.ini"):
        print("Found alembic.ini file.")
    else:
        print("Error: alembic.ini file not found.")
        return False
    
    # Check the migrations directory
    if os.path.exists("migrations"):
        print("Found migrations directory.")
    else:
        print("Error: migrations directory not found.")
        return False
    
    # Check the migrations/versions directory
    if os.path.exists("migrations/versions"):
        print("Found migrations/versions directory.")
        
        # List all migration files
        migration_files = os.listdir("migrations/versions")
        if migration_files:
            print(f"Found {len(migration_files)} migration files:")
            for file in migration_files:
                print(f"  - {file}")
        else:
            print("No migration files found.")
    else:
        print("Error: migrations/versions directory not found.")
        return False
    
    # Check the current head revision
    output, success = run_command("alembic current")
    if success:
        print(f"Current alembic revision: {output}")
    else:
        print(f"Failed to get current alembic revision: {output}")
    
    # Check the head revision
    output, success = run_command("alembic heads")
    if success:
        print(f"Head alembic revision: {output}")
    else:
        print(f"Failed to get head alembic revision: {output}")
    
    # Check the history
    output, success = run_command("alembic history")
    if success:
        print(f"Alembic history: {output}")
    else:
        print(f"Failed to get alembic history: {output}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Azure Database Information Script")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Test the connection
    if not test_connection():
        return 1
    
    # Check alembic migrations
    if not check_alembic_migrations():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
