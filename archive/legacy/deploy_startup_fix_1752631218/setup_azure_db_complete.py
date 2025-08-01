#!/usr/bin/env python
"""
Complete Azure Database Setup Script

This script performs the complete setup of the Azure PostgreSQL database for the AI Event Planner SaaS application.
It runs the migrations, seeds the database with SaaS data and event data, and verifies the setup.
"""

import os
import sys
import argparse
import subprocess
import time

def run_command(command, description, env=None):
    """Run a command and print the output."""
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
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True, env=cmd_env)
    
    print(result.stdout)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    return True

def setup_database(args):
    """Set up the database by running migrations and seeding data."""
    print("Starting complete Azure database setup...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Set up environment variables
    env = {
        "PYTHONPATH": current_dir
    }
    
    # Step 1: Create tables
    print("\nStep 1: Creating tables...")
    if not run_command("python scripts/create_azure_tables_direct.py --force", "Create tables", env=env):
        print("Error: Failed to create tables.")
        return False
    
    # Wait for migrations to complete
    print("Waiting for migrations to complete...")
    time.sleep(5)
    
    # Step 2: Seed SaaS data
    print("\nStep 2: Seeding SaaS data...")
    force_flag = "--force" if args.force else ""
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
    parser = argparse.ArgumentParser(description="Complete Azure Database Setup Script")
    parser.add_argument("--force", action="store_true", help="Force seeding even if data exists")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Set up the database
    if not setup_database(args):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
