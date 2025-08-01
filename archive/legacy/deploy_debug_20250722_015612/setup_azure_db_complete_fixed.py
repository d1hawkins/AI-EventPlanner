#!/usr/bin/env python
"""
Complete Azure Database Setup Script (Fixed)

This script performs the complete setup of the Azure PostgreSQL database for the AI Event Planner SaaS application.
It runs the migrations, seeds the database with SaaS data and event data, and verifies the setup.
This fixed version uses environment variables for database connection and includes retry logic.
"""

import os
import sys
import argparse
import subprocess
import time

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the DATABASE_URL from the app config
from app.config import DATABASE_URL

def run_command(command, description, env=None, max_retries=3, retry_delay=5):
    """Run a command with retry logic and print the output."""
    print(f"\n{'=' * 80}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    if env:
        print(f"Environment: {env}")
    print(f"{'=' * 80}\n")
    
    # Create a copy of the current environment
    cmd_env = os.environ.copy()
    
    # Update with any additional environment variables
    if env:
        cmd_env.update(env)
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, env=cmd_env)
            
            print(result.stdout)
            
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying in {retry_delay} seconds (attempt {retry_count + 1}/{max_retries})...")
                    time.sleep(retry_delay)
                else:
                    print(f"Failed after {max_retries} attempts.")
                    return False
            else:
                return True
        except Exception as e:
            print(f"Exception: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying in {retry_delay} seconds (attempt {retry_count + 1}/{max_retries})...")
                time.sleep(retry_delay)
            else:
                print(f"Failed after {max_retries} attempts.")
                return False

def setup_database(args):
    """Set up the database by running migrations and seeding data."""
    print("Starting complete Azure database setup...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Set up environment variables
    env = {
        "PYTHONPATH": current_dir,
        "DATABASE_URL": DATABASE_URL
    }
    
    # Step 1: Create tables using the fixed script
    print("\nStep 1: Creating tables...")
    force_flag = "--force" if args.force else ""
    if not run_command(f"python scripts/create_azure_tables_direct_fixed.py {force_flag}", "Create tables", env=env):
        print("Error: Failed to create tables.")
        return False
    
    # Wait for table creation to complete
    print("Waiting for table creation to complete...")
    time.sleep(5)
    
    # Step 2: Seed SaaS data
    print("\nStep 2: Seeding SaaS data...")
    if not run_command(f"python scripts/seed_azure_db_direct.py {force_flag}", "Seed SaaS data", env=env):
        print("Error: Failed to seed SaaS data.")
        return False
    
    # Wait for SaaS data seeding to complete
    print("Waiting for SaaS data seeding to complete...")
    time.sleep(5)
    
    # Step 3: Seed event data
    print("\nStep 3: Seeding event data...")
    if not run_command(f"python scripts/seed_azure_db_events.py {force_flag}", "Seed event data", env=env):
        print("Error: Failed to seed event data.")
        return False
    
    # Wait for event data seeding to complete
    print("Waiting for event data seeding to complete...")
    time.sleep(5)
    
    # Step 4: Verify database setup
    print("\nStep 4: Verifying database setup...")
    if not run_command("python scripts/check_azure_db_schema_and_data.py", "Verify database setup", env=env):
        print("Error: Failed to verify database setup.")
        return False
    
    print("\n✅ Complete Azure database setup completed successfully.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Complete Azure Database Setup Script (Fixed)")
    parser.add_argument("--force", action="store_true", help="Force seeding even if data exists")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Set up the database
    if not setup_database(args):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
