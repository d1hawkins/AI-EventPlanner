#!/usr/bin/env python
"""
Create Azure Tables Direct Script

This script creates the necessary tables in the Azure PostgreSQL database using direct SQL statements
instead of relying on Alembic migrations.
"""

import os
import sys
import argparse
import json
from datetime import datetime, timedelta

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
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"Connected to PostgreSQL: {version[0]}")
        
        conn.close()
        print("✅ Connection test successful.")
        return True
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_tables(args):
    """Create the necessary tables in the database."""
    print("Creating tables in the database...")
    
    # Use hardcoded connection parameters for Azure PostgreSQL
    host = "ai-event-planner-db.postgres.database.azure.com"
    port = 5432
    dbname = "eventplanner"
    user = "dbadmin@ai-event-planner-db"
    password = "VM*admin"
    sslmode = "require"
    
    try:
        import psycopg2
        
        # Connect to the database
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            sslmode=sslmode
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if tables already exist
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('users', 'conversations', 'messages', 'events', 'tasks', 'stakeholders',
                              'organizations', 'subscription_plans', 'organization_users', 'subscription_invoices',
                              'event_templates', 'template_items')
        """)
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        if existing_tables and not args.force:
            print(f"Some tables already exist: {existing_tables}")
            print("Use --force to drop and recreate all tables.")
            cursor.close()
            conn.close()
            return True
        elif existing_tables and args.force:
            print(f"Some tables already exist: {existing_tables}")
            print("Forcing table creation...")
            
            # Drop existing tables in reverse order of dependencies
            print("Dropping existing tables...")
            cursor.execute("DROP TABLE IF EXISTS template_items CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS event_templates CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS subscription_invoices CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS organization_users CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS stakeholders CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS tasks CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS events CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS messages CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS conversations CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS organizations CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS subscription_plans CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS agent_states CASCADE;")
            conn.commit()
            print("Existing tables dropped.")
        
        # Create tables
        print("Creating tables...")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                username VARCHAR(255) NOT NULL UNIQUE,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title VARCHAR(255) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id),
                role VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create agent_states table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_states (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id),
                agent_type VARCHAR(50) NOT NULL,
                state JSONB NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create subscription_plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_plans (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                stripe_price_id VARCHAR(255),
                description TEXT,
                price INTEGER NOT NULL,
                interval VARCHAR(50) NOT NULL,
                max_users INTEGER NOT NULL,
                max_events INTEGER NOT NULL,
                features JSONB NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create organizations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organizations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(255) NOT NULL UNIQUE,
                plan_id INTEGER REFERENCES subscription_plans(id),
                subscription_status VARCHAR(50) NOT NULL DEFAULT 'active',
                max_users INTEGER NOT NULL,
                max_events INTEGER NOT NULL,
                features JSONB NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create organization_users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organization_users (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id),
                user_id INTEGER NOT NULL REFERENCES users(id),
                role VARCHAR(50) NOT NULL,
                is_primary BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                UNIQUE (organization_id, user_id)
            );
        """)
        
        # Create subscription_invoices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_invoices (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id),
                stripe_invoice_id VARCHAR(255),
                amount INTEGER NOT NULL,
                status VARCHAR(50) NOT NULL,
                invoice_date TIMESTAMP NOT NULL,
                due_date TIMESTAMP NOT NULL,
                paid_date TIMESTAMP,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id),
                organization_id INTEGER REFERENCES organizations(id),
                title VARCHAR(255) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                description TEXT,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                location VARCHAR(255),
                budget INTEGER,
                attendee_count INTEGER,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                event_id INTEGER NOT NULL REFERENCES events(id),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                assigned_agent VARCHAR(50),
                due_date DATE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create stakeholders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stakeholders (
                id SERIAL PRIMARY KEY,
                event_id INTEGER NOT NULL REFERENCES events(id),
                name VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                contact_info VARCHAR(255),
                notes TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create event_templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_templates (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER REFERENCES organizations(id),
                name VARCHAR(255) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                description TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create template_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template_items (
                id SERIAL PRIMARY KEY,
                template_id INTEGER NOT NULL REFERENCES event_templates(id),
                item_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                order_index INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        
        # Commit the changes
        conn.commit()
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("✅ Tables created successfully.")
        return True
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return False
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Create Azure Tables Direct Script")
    parser.add_argument("--force", action="store_true", help="Force table creation even if tables exist")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Test the connection
    if not test_connection():
        return 1
    
    # Create the tables
    if not create_tables(args):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
