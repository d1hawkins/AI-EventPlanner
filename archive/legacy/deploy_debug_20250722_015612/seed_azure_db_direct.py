#!/usr/bin/env python
"""
Seed Azure Database Script (Direct SQL Version)

This script seeds the Azure PostgreSQL database with initial data for SaaS models using direct SQL.
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

def seed_database(args):
    """Seed the database with initial data using direct SQL."""
    print("Seeding database with SaaS data using direct SQL...")
    
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
        
        # Check if there are already subscription plans in the database
        cursor.execute("SELECT COUNT(*) FROM subscription_plans")
        existing_plans = cursor.fetchone()[0]
        
        if existing_plans > 0 and not args.force:
            print(f"Database already has {existing_plans} subscription plans. Skipping seeding.")
            print("Use --force to seed the database anyway.")
            cursor.close()
            conn.close()
            return True
        elif existing_plans > 0 and args.force:
            print(f"Database already has {existing_plans} subscription plans. Forcing seeding...")
            print("Deleting existing SaaS data...")
            
            # Delete existing data in reverse order of dependencies
            cursor.execute("DELETE FROM organization_users")
            cursor.execute("DELETE FROM organizations")
            cursor.execute("DELETE FROM subscription_plans")
            cursor.execute("DELETE FROM subscription_invoices")
            conn.commit()
            print("Existing SaaS data deleted.")
        
        # Create users if they don't exist
        print("Creating sample users...")
        
        # Check if admin user exists
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            # Create admin user
            cursor.execute("""
                INSERT INTO users (email, username, hashed_password, is_active, created_at)
                VALUES ('admin@example.com', 'admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', true, NOW())
                RETURNING id
            """)
            admin_user_id = cursor.fetchone()[0]
            print(f"Created admin user with ID {admin_user_id}")
        else:
            admin_user_id = admin_user[0]
            print(f"Using existing admin user with ID {admin_user_id}")
        
        # Check if test user exists
        cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
        test_user = cursor.fetchone()
        
        if not test_user:
            # Create test user
            cursor.execute("""
                INSERT INTO users (email, username, hashed_password, is_active, created_at)
                VALUES ('test@example.com', 'testuser', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', true, NOW())
                RETURNING id
            """)
            test_user_id = cursor.fetchone()[0]
            print(f"Created test user with ID {test_user_id}")
        else:
            test_user_id = test_user[0]
            print(f"Using existing test user with ID {test_user_id}")
        
        # Create sample subscription plans
        print("Creating sample subscription plans...")
        
        # Basic plan
        cursor.execute("""
            INSERT INTO subscription_plans (
                name, stripe_price_id, description, price, interval, max_users, max_events, 
                features, is_active, created_at, updated_at
            ) VALUES (
                'Basic', 'price_basic', 'Basic plan with limited features', 999, 'month', 5, 10,
                '{"basic": true, "advanced": false, "premium": false}', true, NOW(), NOW()
            ) RETURNING id
        """)
        basic_plan_id = cursor.fetchone()[0]
        
        # Premium plan
        cursor.execute("""
            INSERT INTO subscription_plans (
                name, stripe_price_id, description, price, interval, max_users, max_events, 
                features, is_active, created_at, updated_at
            ) VALUES (
                'Premium', 'price_premium', 'Premium plan with all features', 2999, 'month', 20, 50,
                '{"basic": true, "advanced": true, "premium": true}', true, NOW(), NOW()
            ) RETURNING id
        """)
        premium_plan_id = cursor.fetchone()[0]
        
        # Get the count of subscription plans
        cursor.execute("SELECT COUNT(*) FROM subscription_plans")
        plan_count = cursor.fetchone()[0]
        print(f"Created {plan_count} subscription plans.")
        
        # Create sample organizations
        print("Creating sample organizations...")
        
        # Acme Inc.
        cursor.execute("""
            INSERT INTO organizations (
                name, slug, plan_id, subscription_status, max_users, max_events, 
                features, created_at, updated_at
            ) VALUES (
                'Acme Inc.', 'acme', %s, 'active', 5, 10,
                '{"basic": true, "advanced": false, "premium": false}', NOW(), NOW()
            ) RETURNING id
        """, (basic_plan_id,))
        org1_id = cursor.fetchone()[0]
        
        # XYZ Corp
        cursor.execute("""
            INSERT INTO organizations (
                name, slug, plan_id, subscription_status, max_users, max_events, 
                features, created_at, updated_at
            ) VALUES (
                'XYZ Corp', 'xyz', %s, 'active', 20, 50,
                '{"basic": true, "advanced": true, "premium": true}', NOW(), NOW()
            ) RETURNING id
        """, (premium_plan_id,))
        org2_id = cursor.fetchone()[0]
        
        # Get the count of organizations
        cursor.execute("SELECT COUNT(*) FROM organizations")
        org_count = cursor.fetchone()[0]
        print(f"Created {org_count} organizations.")
        
        # Create organization users
        print("Creating organization users...")
        
        # Admin user in Acme Inc.
        cursor.execute("""
            INSERT INTO organization_users (
                organization_id, user_id, role, is_primary, created_at, updated_at
            ) VALUES (
                %s, %s, 'admin', true, NOW(), NOW()
            )
        """, (org1_id, admin_user_id))
        
        # Test user in XYZ Corp
        cursor.execute("""
            INSERT INTO organization_users (
                organization_id, user_id, role, is_primary, created_at, updated_at
            ) VALUES (
                %s, %s, 'admin', true, NOW(), NOW()
            )
        """, (org2_id, test_user_id))
        
        # Get the count of organization users
        cursor.execute("SELECT COUNT(*) FROM organization_users")
        org_user_count = cursor.fetchone()[0]
        print(f"Created {org_user_count} organization users.")
        
        # Update events with organization IDs
        print("Updating events with organization IDs...")
        
        # Get all events
        cursor.execute("SELECT id FROM events")
        events = cursor.fetchall()
        
        # Update each event with a random organization ID
        import random
        org_ids = [org1_id, org2_id]
        
        for event in events:
            event_id = event[0]
            org_id = random.choice(org_ids)
            cursor.execute("UPDATE events SET organization_id = %s WHERE id = %s", (org_id, event_id))
            print(f"Updated event {event_id} with organization ID {org_id}")
        
        # Commit the changes
        conn.commit()
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("✅ SaaS database seeded successfully.")
        return True
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return False
    except Exception as e:
        print(f"Error seeding database: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Seed Azure Database Script (Direct SQL Version)")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("--force", action="store_true", help="Force seeding even if data exists")
    
    args = parser.parse_args()
    
    # Test the connection
    if not test_connection():
        return 1
    
    # Seed the database
    if not seed_database(args):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
