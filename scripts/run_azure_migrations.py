#!/usr/bin/env python
"""
Azure Database Migration Script

This script runs database migrations against an Azure PostgreSQL database.
It uses the DATABASE_URL from the .env.azure file to connect to the database.
"""

import os
import sys
import subprocess
import argparse
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

def run_migrations():
    """Run database migrations using Alembic."""
    print("Running database migrations...")
    
    # Use hardcoded connection parameters for Azure PostgreSQL
    host = "ai-event-planner-db.postgres.database.azure.com"
    port = 5432
    dbname = "eventplanner"
    user = "dbadmin@ai-event-planner-db"  # Azure PostgreSQL requires username@hostname format
    password = "VM*admin"
    sslmode = "require"
    
    # Create a temporary script to run the migrations with the correct connection parameters
    temp_script = """
import os
import sys
from alembic import command
from alembic.config import Config

# Set the DATABASE_URL directly with the correct format for Azure PostgreSQL
os.environ["DATABASE_URL"] = "postgresql://{user}:{password}@{host}:{port}/{dbname}"

def run_migrations():
    \"\"\"Run database migrations using Alembic.\"\"\"
    print("Running database migrations...")
    
    # Get the directory of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    project_root = os.path.abspath(os.path.join(dir_path, ".."))
    
    # Create Alembic configuration
    alembic_cfg = Config(os.path.join(project_root, "alembic.ini"))
    
    try:
        # Run the migration
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")
    except Exception as e:
        print(f"Error running migrations: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
""".format(user=user, password=password, host=host, port=port, dbname=dbname)
    
    # Save the temporary script
    temp_script_path = "temp_migrate.py"
    with open(temp_script_path, "w") as f:
        f.write(temp_script)
    
    # Run the temporary script
    output, success = run_command(f"python {temp_script_path}")
    
    # Clean up the temporary script
    try:
        os.remove(temp_script_path)
    except:
        pass
    
    if not success:
        print(f"Failed to run migrations: {output}")
        
        # Try to install the PostgreSQL driver
        print("Attempting to install PostgreSQL driver...")
        driver_output, driver_success = run_command("pip install psycopg2-binary")
        if driver_success:
            print("✅ Successfully installed PostgreSQL driver")
            
            # Try running the migrations again with the correct connection parameters
            print("Trying migrations again with direct connection parameters...")
            
            # Create a temporary script that directly uses the connection parameters
            direct_script = """
import os
import sys
from alembic import command
from alembic.config import Config
import psycopg2

# Set up the connection parameters
host = "{host}"
port = {port}
dbname = "{dbname}"
user = "{user}"
password = "{password}"
sslmode = "require"

# Set the DATABASE_URL directly
os.environ["DATABASE_URL"] = "postgresql://{user}:{password}@{host}:{port}/{dbname}"

def run_migrations():
    \"\"\"Run database migrations using Alembic.\"\"\"
    print("Running database migrations...")
    
    # Test the connection first
    try:
        print("Testing database connection...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            sslmode=sslmode
        )
        conn.close()
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {{e}}")
        sys.exit(1)
    
    # Get the directory of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    project_root = os.path.abspath(os.path.join(dir_path, ".."))
    
    # Create Alembic configuration
    alembic_cfg = Config(os.path.join(project_root, "alembic.ini"))
    
    try:
        # Run the migration
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")
    except Exception as e:
        print(f"Error running migrations: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
""".format(user=user, password=password, host=host, port=port, dbname=dbname)
            
            # Save the direct script
            direct_script_path = "direct_migrate.py"
            with open(direct_script_path, "w") as f:
                f.write(direct_script)
            
            # Run the direct script
            direct_output, direct_success = run_command(f"python {direct_script_path}")
            
            # Clean up the direct script
            try:
                os.remove(direct_script_path)
            except:
                pass
            
            if not direct_success:
                print(f"Failed to run migrations with direct connection: {direct_output}")
                return False
            
            print(f"Migration output: {direct_output}")
            print("✅ Migrations completed successfully.")
            return True
        else:
            print(f"Failed to install PostgreSQL driver: {driver_output}")
            return False
    
    print(f"Migration output: {output}")
    print("✅ Migrations completed successfully.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Azure Database Migration Script")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Load environment variables from .env.azure
    if not load_azure_env():
        return 1
    
    # Print the DATABASE_URL (masked for security)
    database_url = os.environ.get("DATABASE_URL", "")
    if args.verbose and database_url:
        # Mask the password in the DATABASE_URL
        masked_url = database_url
        if "@" in database_url and ":" in database_url:
            parts = database_url.split("@")
            credentials = parts[0].split(":")
            if len(credentials) > 2:
                masked_url = f"{credentials[0]}:{credentials[1]}:****@{parts[1]}"
            else:
                masked_url = f"{credentials[0]}:****@{parts[1]}"
        print(f"Using DATABASE_URL: {masked_url}")
    
    # Run the migrations
    if not run_migrations():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
