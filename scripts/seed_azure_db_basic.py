#!/usr/bin/env python
"""
Seed Azure Database Script (Basic Version)

This script seeds the Azure PostgreSQL database with initial data for basic models only.
"""

import os
import sys
import argparse
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
    """Seed the database with initial data."""
    print("Seeding database with initial data...")
    
    # Set up the database connection
    host = "ai-event-planner-db.postgres.database.azure.com"
    port = 5432
    dbname = "eventplanner"
    user = "dbadmin@ai-event-planner-db"
    password = "VM*admin"
    sslmode = "require"
    
    # Set the DATABASE_URL environment variable
    os.environ["DATABASE_URL"] = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    
    # Import the SQLAlchemy models and create the tables
    try:
        # Add the project root to the Python path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sys.path.insert(0, project_root)
        
        # Import the SQLAlchemy models and session
        from sqlalchemy.orm import Session
        from app.db.base import engine
        from app.db.models import User, Conversation, Message, AgentState, Event, Task, Stakeholder
        
        # Create a session
        session = Session(engine)
        
        # Check if there are already users in the database
        existing_users = session.query(User).count()
        if existing_users > 0 and not args.force:
            print(f"Database already has {existing_users} users. Skipping seeding.")
            print("Use --force to seed the database anyway.")
            session.close()
            return True
        elif existing_users > 0 and args.force:
            print(f"Database already has {existing_users} users. Forcing seeding...")
            print("Deleting existing data...")
            
            # Delete existing data in reverse order of dependencies
            session.query(Stakeholder).delete()
            session.query(Task).delete()
            session.query(Event).delete()
            session.query(Message).delete()
            session.query(AgentState).delete()
            session.query(Conversation).delete()
            session.query(User).delete()
            session.commit()
            print("Existing data deleted.")
        
        # Create sample users
        print("Creating sample users...")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            is_active=True
        )
        
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            is_active=True
        )
        
        session.add_all([admin_user, test_user])
        session.commit()
        print(f"Created {session.query(User).count()} users.")
        
        # Create sample conversations
        print("Creating sample conversations...")
        conversation1 = Conversation(
            user_id=admin_user.id,
            title="Company Retreat Planning"
        )
        
        conversation2 = Conversation(
            user_id=admin_user.id,
            title="Product Launch Planning"
        )
        
        session.add_all([conversation1, conversation2])
        session.commit()
        print(f"Created {session.query(Conversation).count()} conversations.")
        
        # Create sample events
        print("Creating sample events...")
        event1 = Event(
            conversation_id=conversation1.id,
            title="Company Retreat",
            description="Annual company retreat for team building and planning",
            start_date=datetime.now() + timedelta(days=30),
            end_date=datetime.now() + timedelta(days=32),
            location="Mountain Resort",
            budget=15000,
            attendee_count=50,
            event_type="corporate"
        )
        
        event2 = Event(
            conversation_id=conversation2.id,
            title="Product Launch",
            description="Launch event for our new product line",
            start_date=datetime.now() + timedelta(days=15),
            end_date=datetime.now() + timedelta(days=15),
            location="Convention Center",
            budget=25000,
            attendee_count=200,
            event_type="corporate"
        )
        
        session.add_all([event1, event2])
        session.commit()
        print(f"Created {session.query(Event).count()} events.")
        
        # Create sample tasks
        print("Creating sample tasks...")
        task1 = Task(
            title="Book venue",
            description="Find and book a suitable venue for the retreat",
            status="completed",
            due_date=datetime.now() + timedelta(days=7),
            event_id=event1.id
        )
        
        task2 = Task(
            title="Arrange catering",
            description="Find a catering service for the retreat",
            status="in_progress",
            due_date=datetime.now() + timedelta(days=14),
            event_id=event1.id
        )
        
        task3 = Task(
            title="Send invitations",
            description="Send invitations to all attendees",
            status="not_started",
            due_date=datetime.now() + timedelta(days=7),
            event_id=event2.id
        )
        
        session.add_all([task1, task2, task3])
        session.commit()
        print(f"Created {session.query(Task).count()} tasks.")
        
        # Create sample stakeholders
        print("Creating sample stakeholders...")
        stakeholder1 = Stakeholder(
            name="John Smith",
            contact_info="john@example.com",
            role="CEO",
            notes="CEO of Acme Inc.",
            event_id=event1.id
        )
        
        stakeholder2 = Stakeholder(
            name="Jane Doe",
            contact_info="jane@example.com",
            role="Marketing Director",
            notes="Marketing Director of Acme Inc.",
            event_id=event2.id
        )
        
        session.add_all([stakeholder1, stakeholder2])
        session.commit()
        print(f"Created {session.query(Stakeholder).count()} stakeholders.")
        
        session.close()
        print("✅ Database seeded successfully.")
        return True
    except ImportError as e:
        print(f"Error importing SQLAlchemy models: {e}")
        print("Make sure you're running this script from the project root directory.")
        return False
    except Exception as e:
        print(f"Error seeding database: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Seed Azure Database Script (Basic Version)")
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
