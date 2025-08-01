#!/usr/bin/env python
"""
Seed Azure Database Script (Events Version)

This script seeds the Azure PostgreSQL database with initial data for events, conversations, etc.
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
    print("Seeding database with events data using direct SQL...")
    
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
        
        # Check if there are already events in the database
        cursor.execute("SELECT COUNT(*) FROM events")
        existing_events = cursor.fetchone()[0]
        
        if existing_events > 0 and not args.force:
            print(f"Database already has {existing_events} events. Skipping seeding.")
            print("Use --force to seed the database anyway.")
            cursor.close()
            conn.close()
            return True
        elif existing_events > 0 and args.force:
            print(f"Database already has {existing_events} events. Forcing seeding...")
            print("Deleting existing events data...")
            
            # Delete existing data in reverse order of dependencies
            cursor.execute("DELETE FROM stakeholders")
            cursor.execute("DELETE FROM tasks")
            cursor.execute("DELETE FROM events")
            cursor.execute("DELETE FROM messages")
            cursor.execute("DELETE FROM agent_states")
            cursor.execute("DELETE FROM conversations")
            conn.commit()
            print("Existing events data deleted.")
        
        # Get user IDs
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
        test_user = cursor.fetchone()
        
        if not admin_user or not test_user:
            print("Error: Required users not found in the database.")
            print("Please run seed_azure_db_direct.py first to create the basic data.")
            cursor.close()
            conn.close()
            return False
        
        admin_user_id = admin_user[0]
        test_user_id = test_user[0]
        
        # Create sample conversations
        print("Creating sample conversations...")
        
        # Admin conversation
        cursor.execute("""
            INSERT INTO conversations (
                user_id, title, created_at, updated_at
            ) VALUES (
                %s, 'Annual Conference Planning', NOW(), NOW()
            ) RETURNING id
        """, (admin_user_id,))
        admin_conversation_id = cursor.fetchone()[0]
        
        # Test user conversation
        cursor.execute("""
            INSERT INTO conversations (
                user_id, title, created_at, updated_at
            ) VALUES (
                %s, 'Team Building Retreat', NOW(), NOW()
            ) RETURNING id
        """, (test_user_id,))
        test_conversation_id = cursor.fetchone()[0]
        
        # Get the count of conversations
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conversation_count = cursor.fetchone()[0]
        print(f"Created {conversation_count} conversations.")
        
        # Create sample messages
        print("Creating sample messages...")
        
        # Admin conversation messages
        cursor.execute("""
            INSERT INTO messages (
                conversation_id, role, content, timestamp
            ) VALUES (
                %s, 'user', 'I need to plan an annual conference for 200 attendees.', NOW()
            )
        """, (admin_conversation_id,))
        
        cursor.execute("""
            INSERT INTO messages (
                conversation_id, role, content, timestamp
            ) VALUES (
                %s, 'assistant', 'I can help you plan your annual conference. What is the theme and when would you like to hold it?', NOW()
            )
        """, (admin_conversation_id,))
        
        # Test user conversation messages
        cursor.execute("""
            INSERT INTO messages (
                conversation_id, role, content, timestamp
            ) VALUES (
                %s, 'user', 'I need to organize a team building retreat for 50 people.', NOW()
            )
        """, (test_conversation_id,))
        
        cursor.execute("""
            INSERT INTO messages (
                conversation_id, role, content, timestamp
            ) VALUES (
                %s, 'assistant', 'I can help you plan your team building retreat. What activities are you interested in and when would you like to hold it?', NOW()
            )
        """, (test_conversation_id,))
        
        # Get the count of messages
        cursor.execute("SELECT COUNT(*) FROM messages")
        message_count = cursor.fetchone()[0]
        print(f"Created {message_count} messages.")
        
        # Create sample events
        print("Creating sample events...")
        
        # Get organization IDs
        cursor.execute("SELECT id FROM organizations")
        organizations = cursor.fetchall()
        
        if not organizations:
            print("Error: No organizations found in the database.")
            print("Please run seed_azure_db_direct.py first to create the organizations.")
            cursor.close()
            conn.close()
            return False
        
        org_ids = [org[0] for org in organizations]
        
        # Admin event
        cursor.execute("""
            INSERT INTO events (
                conversation_id, title, event_type, description, start_date, end_date, 
                location, budget, attendee_count, created_at, updated_at, organization_id
            ) VALUES (
                %s, 'Annual Tech Conference', 'Conference', 'Annual technology conference for industry professionals',
                %s, %s, 'Convention Center, New York', 50000, 200, NOW(), NOW(), %s
            ) RETURNING id
        """, (
            admin_conversation_id, 
            (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'), 
            (datetime.now() + timedelta(days=92)).strftime('%Y-%m-%d'),
            org_ids[0]
        ))
        admin_event_id = cursor.fetchone()[0]
        
        # Test user event
        cursor.execute("""
            INSERT INTO events (
                conversation_id, title, event_type, description, start_date, end_date, 
                location, budget, attendee_count, created_at, updated_at, organization_id
            ) VALUES (
                %s, 'Team Building Retreat', 'Retreat', 'Team building retreat for company employees',
                %s, %s, 'Mountain Resort, Colorado', 25000, 50, NOW(), NOW(), %s
            ) RETURNING id
        """, (
            test_conversation_id, 
            (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'), 
            (datetime.now() + timedelta(days=62)).strftime('%Y-%m-%d'),
            org_ids[1]
        ))
        test_event_id = cursor.fetchone()[0]
        
        # Get the count of events
        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]
        print(f"Created {event_count} events.")
        
        # Create sample tasks
        print("Creating sample tasks...")
        
        # Admin event tasks
        cursor.execute("""
            INSERT INTO tasks (
                event_id, title, description, status, assigned_agent, due_date, created_at, updated_at
            ) VALUES (
                %s, 'Book Venue', 'Book the convention center for the conference', 'pending', 'resource_planning',
                %s, NOW(), NOW()
            )
        """, (admin_event_id, (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')))
        
        cursor.execute("""
            INSERT INTO tasks (
                event_id, title, description, status, assigned_agent, due_date, created_at, updated_at
            ) VALUES (
                %s, 'Arrange Catering', 'Arrange catering for all conference days', 'pending', 'resource_planning',
                %s, NOW(), NOW()
            )
        """, (admin_event_id, (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')))
        
        # Test user event tasks
        cursor.execute("""
            INSERT INTO tasks (
                event_id, title, description, status, assigned_agent, due_date, created_at, updated_at
            ) VALUES (
                %s, 'Book Resort', 'Book the mountain resort for the retreat', 'pending', 'resource_planning',
                %s, NOW(), NOW()
            )
        """, (test_event_id, (datetime.now() + timedelta(days=20)).strftime('%Y-%m-%d')))
        
        # Get the count of tasks
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        print(f"Created {task_count} tasks.")
        
        # Create sample stakeholders
        print("Creating sample stakeholders...")
        
        # Admin event stakeholders
        cursor.execute("""
            INSERT INTO stakeholders (
                event_id, name, role, contact_info, notes, created_at, updated_at
            ) VALUES (
                %s, 'John Smith', 'Sponsor', 'john.smith@example.com', 'Main sponsor for the conference',
                NOW(), NOW()
            )
        """, (admin_event_id,))
        
        # Test user event stakeholders
        cursor.execute("""
            INSERT INTO stakeholders (
                event_id, name, role, contact_info, notes, created_at, updated_at
            ) VALUES (
                %s, 'Jane Doe', 'Facilitator', 'jane.doe@example.com', 'Team building activities facilitator',
                NOW(), NOW()
            )
        """, (test_event_id,))
        
        # Get the count of stakeholders
        cursor.execute("SELECT COUNT(*) FROM stakeholders")
        stakeholder_count = cursor.fetchone()[0]
        print(f"Created {stakeholder_count} stakeholders.")
        
        # Commit the changes
        conn.commit()
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("✅ Events database seeded successfully.")
        return True
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return False
    except Exception as e:
        print(f"Error seeding database: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Seed Azure Database Script (Events Version)")
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
