#!/usr/bin/env python
"""
Setup Azure PostgreSQL Database Script

This script sets up the Azure PostgreSQL database for the SaaS application:
1. Runs migrations to create/update the database schema
2. Seeds the database with initial data

Usage:
    python setup_azure_db.py [options]

Options:
    --admin-email EMAIL       Admin user email (default: admin@example.com)
    --admin-username USERNAME Admin username (default: admin)
    --admin-password PASSWORD Admin password (default: password123)
    --org-name NAME           Default organization name (default: Default Organization)
    --org-slug SLUG           Default organization slug (default: default)
    --skip-org                Skip creating default organization
    --skip-migrations         Skip running migrations
    --skip-seed               Skip seeding the database
"""

import os
import sys
import argparse
import subprocess
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("setup_azure_db")

def run_command(command):
    """Run a shell command and return the output."""
    try:
        logger.info(f"Running command: {command}")
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        return result.stdout.strip(), True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        return f"Error: {e.stderr}", False

def run_migrations():
    """Run database migrations using the run_azure_migrations.py script."""
    logger.info("Running database migrations...")
    
    # Check if the script exists
    if not os.path.exists("scripts/run_azure_migrations.py"):
        logger.error("Error: scripts/run_azure_migrations.py not found.")
        return False
    
    # Run the migrations script
    output, success = run_command("python scripts/run_azure_migrations.py")
    
    if not success:
        logger.error(f"Failed to run migrations: {output}")
        return False
    
    logger.info("✅ Migrations completed successfully")
    return True

def seed_database(admin_email, admin_username, admin_password, org_name, org_slug, skip_org):
    """Seed the database using the seed_azure_db.py script."""
    logger.info("Seeding database...")
    
    # Check if the script exists
    if not os.path.exists("seed_azure_db.py"):
        logger.error("Error: seed_azure_db.py not found.")
        return False
    
    # Build the command
    command = f"python seed_azure_db.py --admin-email {admin_email} --admin-username {admin_username} --admin-password {admin_password} --org-name \"{org_name}\" --org-slug {org_slug}"
    
    if skip_org:
        command += " --skip-org"
    
    # Run the seed script
    output, success = run_command(command)
    
    if not success:
        logger.error(f"Failed to seed database: {output}")
        return False
    
    logger.info("✅ Database seeded successfully")
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Setup Azure PostgreSQL Database Script")
    parser.add_argument("--admin-email", default="admin@example.com", help="Admin user email")
    parser.add_argument("--admin-username", default="admin", help="Admin username")
    parser.add_argument("--admin-password", default="password123", help="Admin password")
    parser.add_argument("--org-name", default="Default Organization", help="Default organization name")
    parser.add_argument("--org-slug", default="default", help="Default organization slug")
    parser.add_argument("--skip-org", action="store_true", help="Skip creating default organization")
    parser.add_argument("--skip-migrations", action="store_true", help="Skip running migrations")
    parser.add_argument("--skip-seed", action="store_true", help="Skip seeding the database")
    
    args = parser.parse_args()
    
    # Run migrations
    if not args.skip_migrations:
        if not run_migrations():
            return 1
    else:
        logger.info("Skipping migrations...")
    
    # Seed database
    if not args.skip_seed:
        if not seed_database(
            args.admin_email, 
            args.admin_username, 
            args.admin_password, 
            args.org_name, 
            args.org_slug, 
            args.skip_org
        ):
            return 1
    else:
        logger.info("Skipping database seeding...")
    
    logger.info("Database setup completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
