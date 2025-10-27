#!/usr/bin/env python3
"""
Drop all tables and reload database with migrations.

This script:
1. Connects to the PostgreSQL database
2. Drops ALL tables (including alembic_version)
3. Runs Alembic migrations from scratch

WARNING: This will delete ALL data in the database!
"""

import os
import sys
from urllib.parse import urlparse, quote, urlunparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("ERROR: psycopg2 not installed. Install with: pip install psycopg2-binary")
    sys.exit(1)


def get_database_url():
    """Get and validate DATABASE_URL from environment."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    # Convert postgres:// to postgresql:// for SQLAlchemy compatibility
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        print("INFO: Converted postgres:// URL to postgresql:// for SQLAlchemy 2.0 compatibility")

    return database_url


def encode_database_url(database_url):
    """URL-encode username and password for psycopg2."""
    try:
        parsed = urlparse(database_url)

        print(f"Database connection info:")
        print(f"  Host: {parsed.hostname}")
        print(f"  Port: {parsed.port or 5432}")
        print(f"  Database: {parsed.path[1:] if parsed.path else 'unknown'}")
        print(f"  Username: {parsed.username}")

        # Reconstruct URL with URL-encoded username and password
        if parsed.username and parsed.password:
            encoded_username = quote(parsed.username, safe='')
            encoded_password = quote(parsed.password, safe='')
            netloc = f"{encoded_username}:{encoded_password}@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            encoded_url = urlunparse((parsed.scheme, netloc, parsed.path,
                                    parsed.params, parsed.query, parsed.fragment))
            print("  Using URL-encoded credentials for psycopg2 compatibility")
            return encoded_url

        return database_url
    except Exception as e:
        print(f"ERROR: Could not parse DATABASE_URL: {e}")
        sys.exit(1)


def drop_all_tables(connection_url):
    """Drop all tables in the database."""
    print("\n" + "="*60)
    print("DROPPING ALL TABLES")
    print("="*60)

    try:
        # Connect to database
        conn = psycopg2.connect(connection_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Get list of all tables
        cur.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tables = cur.fetchall()

        if not tables:
            print("✅ No tables found in database - already clean")
            cur.close()
            conn.close()
            return True

        print(f"\nFound {len(tables)} tables to drop:")
        for table in tables:
            print(f"  - {table[0]}")

        # Drop all tables with CASCADE to handle foreign keys
        print("\nDropping tables...")
        for table in tables:
            table_name = table[0]
            try:
                cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
                print(f"  ✅ Dropped: {table_name}")
            except Exception as e:
                print(f"  ⚠️  Error dropping {table_name}: {e}")

        # Verify all tables are dropped
        cur.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public';
        """)
        remaining = cur.fetchall()

        cur.close()
        conn.close()

        if remaining:
            print(f"\n⚠️  WARNING: {len(remaining)} tables still exist:")
            for table in remaining:
                print(f"  - {table[0]}")
            return False

        print("\n✅ Successfully dropped all tables")
        return True

    except Exception as e:
        print(f"\n❌ ERROR dropping tables: {e}")
        return False


def run_migrations():
    """Run Alembic migrations from scratch."""
    print("\n" + "="*60)
    print("RUNNING MIGRATIONS")
    print("="*60)

    try:
        # Import alembic after ensuring tables are dropped
        from alembic import command
        from alembic.config import Config

        # Get alembic config
        alembic_ini = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'alembic.ini')
        if not os.path.exists(alembic_ini):
            print(f"ERROR: alembic.ini not found at {alembic_ini}")
            return False

        alembic_cfg = Config(alembic_ini)

        # Set the DATABASE_URL for Alembic
        database_url = get_database_url()

        # Escape % for ConfigParser (Alembic's INI parser)
        database_url_for_config = database_url.replace('%', '%%')
        alembic_cfg.set_main_option('sqlalchemy.url', database_url_for_config)

        print("\nRunning migrations to head...")
        command.upgrade(alembic_cfg, 'head')

        print("\n✅ Migrations completed successfully")
        return True

    except Exception as e:
        print(f"\n❌ ERROR running migrations: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_database():
    """Verify database state after migrations."""
    print("\n" + "="*60)
    print("VERIFYING DATABASE")
    print("="*60)

    database_url = get_database_url()
    encoded_url = encode_database_url(database_url)

    try:
        conn = psycopg2.connect(encoded_url)
        cur = conn.cursor()

        # Get all tables
        cur.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tables = cur.fetchall()

        print(f"\nTables in database ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")

        # Check alembic_version
        if any(t[0] == 'alembic_version' for t in tables):
            cur.execute("SELECT version_num FROM alembic_version;")
            version = cur.fetchone()
            if version:
                print(f"\n✅ Current migration version: {version[0]}")
            else:
                print("\n⚠️  alembic_version table exists but is empty")
        else:
            print("\n⚠️  alembic_version table not found")

        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"\n❌ ERROR verifying database: {e}")
        return False


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("DROP AND RELOAD DATABASE SCRIPT")
    print("="*60)
    print("\n⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print("Press Ctrl+C to cancel, or wait 5 seconds to continue...")

    import time
    for i in range(5, 0, -1):
        print(f"  Starting in {i}...", end='\r')
        time.sleep(1)
    print("\n")

    # Get and encode database URL
    database_url = get_database_url()
    encoded_url = encode_database_url(database_url)

    # Step 1: Drop all tables
    if not drop_all_tables(encoded_url):
        print("\n❌ FAILED to drop all tables")
        sys.exit(1)

    # Step 2: Run migrations
    if not run_migrations():
        print("\n❌ FAILED to run migrations")
        sys.exit(1)

    # Step 3: Verify database
    if not verify_database():
        print("\n⚠️  WARNING: Database verification had issues")

    print("\n" + "="*60)
    print("✅ DATABASE DROP AND RELOAD COMPLETE")
    print("="*60)
    print("\nDatabase is now fresh with all migrations applied.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
