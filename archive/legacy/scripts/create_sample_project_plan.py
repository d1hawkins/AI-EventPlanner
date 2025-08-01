#!/usr/bin/env python3
"""
Script to create a sample project plan with tasks in the database.
This is useful for testing and demonstration purposes.
"""

from datetime import datetime, timedelta
import uuid

from app.db.base import SessionLocal
from app.db.models import User, Conversation, Event, Task
from sqlalchemy.orm import Session

def create_sample_user(db: Session):
    """Create a sample user if one doesn't exist."""
    # Check if a user already exists
    user = db.query(User).first()
    
    if not user:
        # Create a new user
        user = User(
            email="demo@example.com",
            username="demo_user",
            hashed_password="$2b$12$uVJ6JzKqlmIgvKNGxGBkAOOt8G0oCUJgG1pKPEKBnqx6g9.ju7ZMm",  # hashed 'password'
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created sample user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")
    
    return user

def create_sample_conversation(db: Session, user_id: int):
    """Create a sample conversation."""
    conversation = Conversation(
        user_id=user_id,
        title="Sample Event Planning",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    print(f"Created sample conversation: {conversation.title}")
    
    return conversation

def create_sample_event(db: Session, conversation_id: int):
    """Create a sample event."""
    event = Event(
        conversation_id=conversation_id,
        title="Tech Conference 2025",
        event_type="conference",
        description="A three-day technology conference featuring workshops, presentations, and networking opportunities.",
        start_date=datetime.utcnow() + timedelta(days=90),
        end_date=datetime.utcnow() + timedelta(days=93),
        location="San Francisco Convention Center",
        budget=150000,
        attendee_count=500,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    print(f"Created sample event: {event.title}")
    
    return event

def create_sample_tasks(db: Session, event_id: int):
    """Create sample tasks for the event."""
    tasks = [
        {
            "title": "Venue Booking",
            "description": "Book the convention center and confirm all requirements",
            "status": "completed",
            "assigned_agent": "resource_planning",
            "due_date": datetime.utcnow() + timedelta(days=10)
        },
        {
            "title": "Speaker Invitations",
            "description": "Identify and invite keynote speakers and session presenters",
            "status": "in_progress",
            "assigned_agent": "stakeholder_management",
            "due_date": datetime.utcnow() + timedelta(days=30)
        },
        {
            "title": "Marketing Campaign",
            "description": "Develop and launch marketing campaign for the conference",
            "status": "in_progress",
            "assigned_agent": "marketing_communications",
            "due_date": datetime.utcnow() + timedelta(days=45)
        },
        {
            "title": "Budget Finalization",
            "description": "Finalize budget allocation for all aspects of the conference",
            "status": "pending",
            "assigned_agent": "financial",
            "due_date": datetime.utcnow() + timedelta(days=15)
        },
        {
            "title": "Vendor Selection",
            "description": "Select vendors for catering, AV equipment, and other services",
            "status": "pending",
            "assigned_agent": "resource_planning",
            "due_date": datetime.utcnow() + timedelta(days=40)
        },
        {
            "title": "Registration System",
            "description": "Set up online registration system for attendees",
            "status": "not_started",
            "assigned_agent": "project_management",
            "due_date": datetime.utcnow() + timedelta(days=50)
        },
        {
            "title": "Compliance Check",
            "description": "Ensure all aspects of the event comply with regulations",
            "status": "not_started",
            "assigned_agent": "compliance_security",
            "due_date": datetime.utcnow() + timedelta(days=60)
        }
    ]
    
    created_tasks = []
    
    for task_data in tasks:
        task = Task(
            event_id=event_id,
            title=task_data["title"],
            description=task_data["description"],
            status=task_data["status"],
            assigned_agent=task_data["assigned_agent"],
            due_date=task_data["due_date"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(task)
        created_tasks.append(task)
    
    db.commit()
    
    for task in created_tasks:
        db.refresh(task)
    
    print(f"Created {len(created_tasks)} sample tasks")
    
    return created_tasks

def create_sample_project_plan():
    """Create a sample project plan with tasks in the database."""
    # Create a database session
    db = SessionLocal()
    
    try:
        # Create sample data
        user = create_sample_user(db)
        conversation = create_sample_conversation(db, user.id)
        event = create_sample_event(db, conversation.id)
        tasks = create_sample_tasks(db, event.id)
        
        print("\nSample project plan created successfully!")
        print(f"Event: {event.title}")
        print(f"Number of tasks: {len(tasks)}")
        
        return True
    
    except Exception as e:
        print(f"Error creating sample project plan: {str(e)}")
        db.rollback()
        return False
    
    finally:
        # Close the database session
        db.close()

if __name__ == "__main__":
    create_sample_project_plan()
