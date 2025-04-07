#!/usr/bin/env python
"""
Check Azure Database Schema and Data Script

This script checks the Azure PostgreSQL database schema and data to verify everything is set up correctly.
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

def check_schema_and_data():
    """Check the database schema and data."""
    print("Checking database schema and data...")
    
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
        
        # Check tables
        print("\n=== Tables ===")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        for table in tables:
            print(f"- {table[0]}")
        
        # Check users
        print("\n=== Users ===")
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
        for user in users:
            print(f"- User {user[0]}: {user[1]} ({user[2]})")
        
        # Check organizations
        print("\n=== Organizations ===")
        cursor.execute("SELECT id, name, slug, subscription_status FROM organizations")
        organizations = cursor.fetchall()
        for org in organizations:
            print(f"- Organization {org[0]}: {org[1]} ({org[2]}, {org[3]})")
        
        # Check subscription plans
        print("\n=== Subscription Plans ===")
        cursor.execute("SELECT id, name, price, interval FROM subscription_plans")
        plans = cursor.fetchall()
        for plan in plans:
            print(f"- Plan {plan[0]}: {plan[1]} (${plan[2]/100:.2f}/{plan[3]})")
        
        # Check organization users
        print("\n=== Organization Users ===")
        cursor.execute("""
            SELECT ou.organization_id, o.name, ou.user_id, u.username, ou.role
            FROM organization_users ou
            JOIN organizations o ON ou.organization_id = o.id
            JOIN users u ON ou.user_id = u.id
        """)
        org_users = cursor.fetchall()
        for org_user in org_users:
            print(f"- Organization {org_user[0]} ({org_user[1]}): User {org_user[2]} ({org_user[3]}) as {org_user[4]}")
        
        # Check conversations
        print("\n=== Conversations ===")
        cursor.execute("""
            SELECT c.id, c.title, c.user_id, u.username
            FROM conversations c
            JOIN users u ON c.user_id = u.id
        """)
        conversations = cursor.fetchall()
        for conversation in conversations:
            print(f"- Conversation {conversation[0]}: {conversation[1]} (User: {conversation[3]})")
        
        # Check events
        print("\n=== Events ===")
        cursor.execute("""
            SELECT e.id, e.title, e.event_type, e.organization_id, o.name
            FROM events e
            JOIN organizations o ON e.organization_id = o.id
        """)
        events = cursor.fetchall()
        for event in events:
            print(f"- Event {event[0]}: {event[1]} ({event[2]}, Organization: {event[4]})")
        
        # Check tasks
        print("\n=== Tasks ===")
        cursor.execute("""
            SELECT t.id, t.title, t.status, t.event_id, e.title
            FROM tasks t
            JOIN events e ON t.event_id = e.id
        """)
        tasks = cursor.fetchall()
        for task in tasks:
            print(f"- Task {task[0]}: {task[1]} ({task[2]}, Event: {task[4]})")
        
        # Check stakeholders
        print("\n=== Stakeholders ===")
        cursor.execute("""
            SELECT s.id, s.name, s.role, s.event_id, e.title
            FROM stakeholders s
            JOIN events e ON s.event_id = e.id
        """)
        stakeholders = cursor.fetchall()
        for stakeholder in stakeholders:
            print(f"- Stakeholder {stakeholder[0]}: {stakeholder[1]} ({stakeholder[2]}, Event: {stakeholder[4]})")
        
        # Check event-organization relationship
        print("\n=== Event-Organization Relationship ===")
        cursor.execute("""
            SELECT e.id, e.title, e.organization_id, o.name
            FROM events e
            JOIN organizations o ON e.organization_id = o.id
        """)
        event_orgs = cursor.fetchall()
        for event_org in event_orgs:
            print(f"- Event {event_org[0]} ({event_org[1]}) belongs to Organization {event_org[2]} ({event_org[3]})")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("\n✅ Database schema and data check completed successfully.")
        return True
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return False
    except Exception as e:
        print(f"Error checking schema and data: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Check Azure Database Schema and Data Script")
    
    # Test the connection
    if not test_connection():
        return 1
    
    # Check the schema and data
    if not check_schema_and_data():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
