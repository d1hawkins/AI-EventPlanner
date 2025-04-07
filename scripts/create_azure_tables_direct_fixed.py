#!/usr/bin/env python
"""
Create Azure Tables Direct Script (Fixed)

This script creates the necessary tables in the Azure PostgreSQL database using direct SQL statements
instead of relying on Alembic migrations. It uses the DATABASE_URL environment variable instead of
hardcoded credentials.
"""

import os
import sys
import argparse
import json
import time
import urllib.parse
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the DATABASE_URL from the app config
from app.config import DATABASE_URL

def parse_database_url(url):
    """Parse the DATABASE_URL into connection parameters."""
    result = urllib.parse.urlparse(url)
    username = result.username
    password = urllib.parse.unquote(result.password) if result.password else ""
    database = result.path[1:]  # Remove the leading '/'
    hostname = result.hostname
    port = result.port or 5432  # Default PostgreSQL port
    
    # For Azure PostgreSQL, the username needs to include the hostname
    if hostname and "@" not in username and hostname.endswith("database.azure.com"):
        username = f"{username}@{hostname.split('.')[0]}"
    
    return {
        "host": hostname,
        "port": port,
        "dbname": database,
        "user": username,
        "password": password,
        "sslmode": "require" if hostname and hostname.endswith("database.azure.com") else "prefer"
    }

def test_connection(max_retries=5, retry_delay=5):
    """Test the connection to the PostgreSQL database with retry logic."""
    try:
        import psycopg2
    except ImportError:
        print("Installing psycopg2-binary...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        import psycopg2
    
    # Parse the DATABASE_URL
    conn_params = parse_database_url(DATABASE_URL)
    
    print(f"\nTesting connection to PostgreSQL database...")
    print(f"Connection details:")
    print(f"  Host: {conn_params['host']}")
    print(f"  Port: {conn_params['port']}")
    print(f"  Database: {conn_params['dbname']}")
    print(f"  Username: {conn_params['user']}")
    print(f"  Password: {'*' * len(conn_params['password'])}")
    print(f"  SSL Mode: {conn_params['sslmode']}")
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Try to connect to the database
            print(f"Connecting to database (attempt {retry_count + 1}/{max_retries})...")
            conn = psycopg2.connect(**conn_params)
            
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
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect after {max_retries} attempts.")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

def create_tables(args):
    """Create the necessary tables in the database."""
    print("Creating tables in the database...")
    
    # Parse the DATABASE_URL
    conn_params = parse_database_url(DATABASE_URL)
    
    try:
        import psycopg2
        
        # Connect to the database
        conn = psycopg2.connect(**conn_params)
        
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
    parser = argparse.ArgumentParser(description="Create Azure Tables Direct Script (Fixed)")
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
