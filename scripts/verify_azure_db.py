#!/usr/bin/env python
"""
Azure Database Verification Script

This script verifies the Azure PostgreSQL database state and migration status.
It provides detailed information about:
- Database connection
- Current schema
- Migration status
- Table structure
- Sample data counts
"""

import os
import sys
import argparse
from typing import List, Dict, Any

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def get_database_info() -> Dict[str, Any]:
    """
    Get comprehensive database information.

    Returns:
        Dictionary with database information
    """
    try:
        import psycopg2
        from psycopg2 import sql
    except ImportError:
        print("❌ psycopg2 not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        import psycopg2
        from psycopg2 import sql

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable is not set")
        return {}

    info = {}

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # PostgreSQL version
        cursor.execute("SELECT version();")
        info['version'] = cursor.fetchone()[0]

        # Database size
        cursor.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database()));
        """)
        info['size'] = cursor.fetchone()[0]

        # Current database name
        cursor.execute("SELECT current_database();")
        info['database'] = cursor.fetchone()[0]

        # Current user
        cursor.execute("SELECT current_user;")
        info['user'] = cursor.fetchone()[0]

        # Connection count
        cursor.execute("""
            SELECT count(*) FROM pg_stat_activity
            WHERE datname = current_database();
        """)
        info['connections'] = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return info

    except Exception as e:
        print(f"❌ Error getting database info: {e}")
        return {}


def check_migration_status() -> Dict[str, Any]:
    """
    Check the Alembic migration status.

    Returns:
        Dictionary with migration status
    """
    try:
        import psycopg2
    except ImportError:
        return {'error': 'psycopg2 not installed'}

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return {'error': 'DATABASE_URL not set'}

    status = {}

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Check if alembic_version table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'alembic_version'
            );
        """)
        status['alembic_table_exists'] = cursor.fetchone()[0]

        if status['alembic_table_exists']:
            # Get current version
            cursor.execute("SELECT version_num FROM alembic_version;")
            result = cursor.fetchone()
            status['current_version'] = result[0] if result else None
        else:
            status['current_version'] = None

        cursor.close()
        conn.close()

        return status

    except Exception as e:
        return {'error': str(e)}


def get_table_info() -> List[Dict[str, Any]]:
    """
    Get information about all tables in the database.

    Returns:
        List of dictionaries with table information
    """
    try:
        import psycopg2
    except ImportError:
        return []

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return []

    tables = []

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Get all tables with row counts and sizes
        cursor.execute("""
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                n_tup_ins AS inserts,
                n_tup_upd AS updates,
                n_tup_del AS deletes
            FROM pg_stat_user_tables
            ORDER BY tablename;
        """)

        for row in cursor.fetchall():
            table_info = {
                'schema': row[0],
                'name': row[1],
                'size': row[2],
                'inserts': row[3],
                'updates': row[4],
                'deletes': row[5]
            }

            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {row[1]};")
                table_info['rows'] = cursor.fetchone()[0]
            except:
                table_info['rows'] = 'N/A'

            tables.append(table_info)

        cursor.close()
        conn.close()

        return tables

    except Exception as e:
        print(f"❌ Error getting table info: {e}")
        return []


def check_table_structure() -> Dict[str, List[str]]:
    """
    Check the structure of key tables.

    Returns:
        Dictionary mapping table names to lists of column names
    """
    try:
        import psycopg2
    except ImportError:
        return {}

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return {}

    key_tables = [
        'users', 'events', 'conversations', 'messages',
        'organizations', 'organization_users', 'subscription_plans',
        'subscription_invoices'
    ]

    structure = {}

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        for table in key_tables:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position;
            """, (table,))

            columns = []
            for row in cursor.fetchall():
                col_info = f"{row[0]} ({row[1]}, {'NULL' if row[2] == 'YES' else 'NOT NULL'})"
                columns.append(col_info)

            if columns:
                structure[table] = columns

        cursor.close()
        conn.close()

        return structure

    except Exception as e:
        print(f"❌ Error checking table structure: {e}")
        return {}


def check_foreign_keys() -> List[Dict[str, str]]:
    """
    Check foreign key constraints in the database.

    Returns:
        List of foreign key information
    """
    try:
        import psycopg2
    except ImportError:
        return []

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return []

    foreign_keys = []

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name;
        """)

        for row in cursor.fetchall():
            foreign_keys.append({
                'table': row[0],
                'column': row[1],
                'references_table': row[2],
                'references_column': row[3]
            })

        cursor.close()
        conn.close()

        return foreign_keys

    except Exception as e:
        print(f"❌ Error checking foreign keys: {e}")
        return []


def main():
    """Main entry point for the verification script."""
    parser = argparse.ArgumentParser(
        description="Verify Azure PostgreSQL database state and migrations"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output including table structures"
    )

    args = parser.parse_args()

    print_section("Azure PostgreSQL Database Verification")

    # Check DATABASE_URL
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("\n❌ DATABASE_URL environment variable is not set!")
        print("Please set DATABASE_URL to your Azure PostgreSQL connection string.")
        sys.exit(1)

    # Mask password in URL for display
    masked_url = database_url
    if '@' in database_url:
        parts = database_url.split('@')
        if ':' in parts[0]:
            masked_url = parts[0].split(':')[0] + ':' + parts[0].split(':')[1] + ':****@' + '@'.join(parts[1:])

    print(f"\nDatabase URL: {masked_url}")

    # Database Info
    print_section("Database Information")
    db_info = get_database_info()
    if db_info:
        print(f"✅ PostgreSQL Version: {db_info.get('version', 'Unknown').split(',')[0]}")
        print(f"✅ Database Name: {db_info.get('database', 'Unknown')}")
        print(f"✅ Current User: {db_info.get('user', 'Unknown')}")
        print(f"✅ Database Size: {db_info.get('size', 'Unknown')}")
        print(f"✅ Active Connections: {db_info.get('connections', 'Unknown')}")
    else:
        print("❌ Failed to retrieve database information")

    # Migration Status
    print_section("Migration Status")
    migration_status = check_migration_status()
    if 'error' in migration_status:
        print(f"❌ Error: {migration_status['error']}")
    else:
        if migration_status.get('alembic_table_exists'):
            print("✅ Alembic version table exists")
            current_version = migration_status.get('current_version')
            if current_version:
                print(f"✅ Current migration version: {current_version}")
            else:
                print("⚠️  No migration version found in alembic_version table")
        else:
            print("❌ Alembic version table does not exist")
            print("   This indicates migrations have never been run on this database")

    # Table Information
    print_section("Tables")
    tables = get_table_info()
    if tables:
        print(f"\nFound {len(tables)} tables:\n")
        for table in tables:
            print(f"  📊 {table['name']}")
            print(f"      Rows: {table['rows']}, Size: {table['size']}")
            if args.verbose:
                print(f"      Stats: {table['inserts']} inserts, {table['updates']} updates, {table['deletes']} deletes")
    else:
        print("❌ No tables found or error retrieving table information")

    # Table Structure (verbose mode)
    if args.verbose:
        print_section("Table Structures")
        structures = check_table_structure()
        if structures:
            for table, columns in structures.items():
                print(f"\n  📋 {table}:")
                for col in columns:
                    print(f"      - {col}")
        else:
            print("No table structure information available")

        # Foreign Keys (verbose mode)
        print_section("Foreign Key Constraints")
        foreign_keys = check_foreign_keys()
        if foreign_keys:
            for fk in foreign_keys:
                print(f"  🔗 {fk['table']}.{fk['column']} -> {fk['references_table']}.{fk['references_column']}")
        else:
            print("No foreign key constraints found")

    # Summary
    print_section("Summary")

    if db_info and migration_status.get('alembic_table_exists') and tables:
        print("✅ Database is properly configured and migrated")
        print(f"   - {len(tables)} tables found")
        print(f"   - Migration version: {migration_status.get('current_version', 'Unknown')}")
    else:
        print("⚠️  Database may need attention:")
        if not db_info:
            print("   - Cannot connect to database")
        if not migration_status.get('alembic_table_exists'):
            print("   - Migrations need to be run")
        if not tables:
            print("   - No tables found")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
