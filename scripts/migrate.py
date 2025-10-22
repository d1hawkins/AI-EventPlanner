#!/usr/bin/env python
import os
import sys
from alembic import command
from alembic.config import Config

def run_migrations():
    """Run database migrations using Alembic."""
    print("Running database migrations...")
    
    # Get the directory of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # Create Alembic configuration
    alembic_cfg = Config(os.path.join(dir_path, "..", "alembic.ini"))
    
    try:
        # Run the migration
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")
    except Exception as e:
        print(f"Error running migrations: {e}")
        sys.exit(1)

def main():
    """Main entry point for the migration script."""
    run_migrations()

if __name__ == "__main__":
    main()
