#!/usr/bin/env python
"""
Check Azure PostgreSQL Database Schema Script

This script connects to the Azure PostgreSQL database and checks the schema,
verifying that all required tables exist and have the expected columns.
It can be used to troubleshoot database issues and verify that migrations
have been applied correctly.

Usage:
    python check_azure_db_schema.py [--verbose]
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("check_azure_db_schema")

# Expected tables and their key columns
EXPECTED_TABLES = {
    "users": ["id", "email", "username", "hashed_password", "is_active", "created_at"],
    "organizations": ["id", "name", "slug", "plan_id", "subscription_status", "max_users", "max_events", "features"],
    "organization_users": ["organization_id", "user_id", "role", "is_primary"],
    "subscription_plans": ["id", "name", "stripe_price_id", "price", "interval", "max_users", "max_events", "features"],
    "subscription_invoices": ["id", "organization_id", "stripe_invoice_id", "amount", "status"],
    "conversations": ["id", "user_id", "organization_id", "title", "created_at", "updated_at"],
    "messages": ["id", "conversation_id", "role", "content", "timestamp"],
    "agent_states": ["id", "conversation_id", "state_data", "updated_at"],
    "events": ["id", "conversation_id", "organization_id", "title", "event_type", "start_date", "end_date"],
    "tasks": ["id", "event_id", "title", "description", "status", "assigned_agent"],
    "stakeholders": ["id", "event_id", "name", "role", "contact_info"]
}

def load_azure_env():
    """Load environment variables from .env.azure file."""
    logger.info("Loading environment variables from .env.azure...")
    if not os.path.exists(".env.azure"):
        logger.error("Error: .env.azure file not found.")
        return False
    
    logger.info(f"env var file path: { os.path.abspath(".env.azure")}")
    load_dotenv(".env.azure", override=True)
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        logger.error("Error: DATABASE_URL not found in .env.azure file.")
        return False
    
    logger.info("✅ Loaded environment variables from .env.azure")
    logger.info(f"Using database URL: {os.getenv('DATABASE_URL')}")
    return True

def get_db_connection():
    """Create a database connection."""
    try:
        # Get the DATABASE_URL from environment
        database_url = os.getenv("DATABASE_URL")
        
        # Create SQLAlchemy engine
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )
        
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        
        return engine
    except SQLAlchemyError as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def check_table_exists(engine, table_name):
    """Check if a table exists in the database."""
    try:
        # Use SQLAlchemy's inspect to check if table exists (works for both SQLite and PostgreSQL)
        inspector = inspect(engine)
        exists = table_name in inspector.get_table_names()
        return exists
    except SQLAlchemyError as e:
        logger.error(f"Error checking if table exists: {e}")
        return False

def check_table_columns(engine, table_name, expected_columns, verbose=False):
    """Check if a table has the expected columns."""
    try:
        inspector = inspect(engine)
        columns = [col["name"] for col in inspector.get_columns(table_name)]
        
        if verbose:
            logger.info(f"Table {table_name} columns: {columns}")
        
        missing_columns = [col for col in expected_columns if col not in columns]
        
        if missing_columns:
            logger.warning(f"Table {table_name} is missing columns: {missing_columns}")
            return False
        
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error checking table columns: {e}")
        return False

def check_row_count(engine, table_name):
    """Check the number of rows in a table."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            return count
    except SQLAlchemyError as e:
        logger.error(f"Error checking row count: {e}")
        return -1

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Check Azure PostgreSQL Database Schema Script")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Load environment variables
    if not load_azure_env():
        return 1
    
    # Get database connection
    engine = get_db_connection()
    if not engine:
        return 1
    
    # Check tables
    all_tables_exist = True
    all_columns_exist = True
    
    logger.info("Checking database schema...")
    
    for table_name, expected_columns in EXPECTED_TABLES.items():
        exists = check_table_exists(engine, table_name)
        
        if exists:
            row_count = check_row_count(engine, table_name)
            logger.info(f"✅ Table {table_name} exists with {row_count} rows")
            
            columns_exist = check_table_columns(engine, table_name, expected_columns, args.verbose)
            if not columns_exist:
                all_columns_exist = False
        else:
            logger.error(f"❌ Table {table_name} does not exist")
            all_tables_exist = False
    
    if all_tables_exist and all_columns_exist:
        logger.info("✅ All expected tables and columns exist in the database")
        return 0
    else:
        if not all_tables_exist:
            logger.error("❌ Some expected tables are missing")
        if not all_columns_exist:
            logger.error("❌ Some expected columns are missing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
