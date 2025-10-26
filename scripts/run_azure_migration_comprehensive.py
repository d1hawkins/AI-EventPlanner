#!/usr/bin/env python
"""
Comprehensive Azure Database Migration Script

This script runs Alembic migrations on the Azure PostgreSQL database with:
- Connection verification
- Detailed error reporting
- Retry logic
- Migration status checking
"""

import os
import sys
import time
import argparse
from typing import Optional, Tuple

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)


def verify_database_connection() -> Tuple[bool, Optional[str]]:
    """
    Verify connection to the PostgreSQL database.

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    print("Verifying database connection...")

    try:
        import psycopg2
    except ImportError:
        return False, "psycopg2 module not installed. Installing..."

    # Get DATABASE_URL from environment
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return False, "DATABASE_URL environment variable is not set"

    # Accept both 'postgres://' and 'postgresql://' URL schemes (both are valid for PostgreSQL)
    if not (database_url.startswith("postgresql") or database_url.startswith("postgres://")):
        return False, f"DATABASE_URL must be a PostgreSQL connection string. Got: {database_url[:20]}..."

    try:
        # Parse the DATABASE_URL to extract connection parameters
        from urllib.parse import urlparse
        parsed = urlparse(database_url)

        print(f"  Host: {parsed.hostname}")
        print(f"  Port: {parsed.port or 5432}")
        print(f"  Database: {parsed.path[1:]}")
        print(f"  Username: {parsed.username}")

        # Test connection
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Get PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to PostgreSQL: {version.split(',')[0]}")

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
            cursor.execute("SELECT version_num FROM alembic_version;")
            result = cursor.fetchone()
            current_version = result[0] if result else "None"
            print(f"  Current Alembic version: {current_version}")
        else:
            print("  No previous migrations found (alembic_version table doesn't exist)")

        # List current tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"  Current tables ({len(tables)}): {', '.join([t[0] for t in tables]) if tables else 'None'}")

        cursor.close()
        conn.close()

        return True, None

    except Exception as e:
        return False, f"Connection failed: {str(e)}"


def run_migrations_with_retry(max_retries: int = 3, retry_delay: int = 5) -> bool:
    """
    Run database migrations with retry logic.

    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries

    Returns:
        True if migrations succeeded, False otherwise
    """
    from alembic import command
    from alembic.config import Config

    print(f"\nRunning database migrations (max retries: {max_retries})...")

    # Get the directory of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Create Alembic configuration
    alembic_cfg = Config(os.path.join(dir_path, "..", "alembic.ini"))

    for attempt in range(1, max_retries + 1):
        try:
            print(f"\nAttempt {attempt}/{max_retries}...")

            # Check current revision
            print("Checking current database revision...")
            try:
                command.current(alembic_cfg)
            except Exception as e:
                print(f"  Warning: Could not get current revision: {e}")

            # Run upgrade to head
            print("Upgrading to head revision...")
            command.upgrade(alembic_cfg, "head")

            print("✅ Migrations completed successfully!")

            # Show final revision
            print("\nFinal database revision:")
            command.current(alembic_cfg)

            return True

        except Exception as e:
            print(f"❌ Migration attempt {attempt} failed: {e}")

            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"\n❌ All {max_retries} migration attempts failed.")
                return False

    return False


def verify_migration_success() -> bool:
    """
    Verify that migrations completed successfully.

    Returns:
        True if verification passed, False otherwise
    """
    print("\nVerifying migration success...")

    try:
        import psycopg2

        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not set")
            return False

        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Get current alembic version
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'alembic_version'
            );
        """)
        alembic_exists = cursor.fetchone()[0]

        if not alembic_exists:
            print("❌ alembic_version table not found")
            return False

        cursor.execute("SELECT version_num FROM alembic_version;")
        result = cursor.fetchone()
        current_version = result[0] if result else None

        if not current_version:
            print("❌ No migration version found")
            return False

        print(f"✅ Current migration version: {current_version}")

        # Check that key tables exist
        expected_tables = [
            'users', 'events', 'conversations', 'messages',
            'organizations', 'organization_users', 'subscription_plans'
        ]

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]

        missing_tables = [t for t in expected_tables if t not in existing_tables]

        if missing_tables:
            print(f"⚠️  Warning: Some expected tables are missing: {', '.join(missing_tables)}")
            print(f"   Existing tables: {', '.join(existing_tables)}")
        else:
            print(f"✅ All expected tables exist ({len(expected_tables)} tables)")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def main():
    """Main entry point for the migration script."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive Azure database migrations"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retry attempts (default: 3)"
    )
    parser.add_argument(
        "--retry-delay",
        type=int,
        default=5,
        help="Delay in seconds between retries (default: 5)"
    )
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Skip database connection verification"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Azure PostgreSQL Database Migration Script")
    print("=" * 70)

    # Step 1: Verify database connection
    if not args.skip_verification:
        success, error = verify_database_connection()
        if not success:
            print(f"\n❌ Database connection verification failed: {error}")
            sys.exit(1)
    else:
        print("\nSkipping database connection verification...")

    # Step 2: Run migrations
    if not run_migrations_with_retry(args.max_retries, args.retry_delay):
        print("\n❌ Migration failed")
        sys.exit(1)

    # Step 3: Verify migration success
    if not verify_migration_success():
        print("\n⚠️  Migration may not have completed successfully")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✅ Database migration completed successfully!")
    print("=" * 70)

    sys.exit(0)


if __name__ == "__main__":
    main()
