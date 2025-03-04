#!/usr/bin/env python3
"""
Script to verify that project plans with tasks exist in the database.
"""

from app.db.base import SessionLocal
from app.db.models import Task, Event

def verify_project_plans():
    """
    Query the database to verify that project plans with tasks exist.
    """
    # Create a database session
    db = SessionLocal()
    
    try:
        # Query all tasks
        tasks = db.query(Task).all()
        
        if not tasks:
            print("No tasks found in the database.")
            return False
        
        print(f"Found {len(tasks)} tasks in the database:")
        
        # Group tasks by event
        events_with_tasks = {}
        
        for task in tasks:
            if task.event_id not in events_with_tasks:
                # Get the associated event
                event = db.query(Event).filter(Event.id == task.event_id).first()
                events_with_tasks[task.event_id] = {
                    "event": event,
                    "tasks": []
                }
            
            events_with_tasks[task.event_id]["tasks"].append(task)
        
        # Print event and task details
        for event_id, data in events_with_tasks.items():
            event = data["event"]
            event_tasks = data["tasks"]
            
            print(f"\nEvent ID: {event_id}")
            print(f"Event Title: {event.title}")
            print(f"Event Type: {event.event_type}")
            print(f"Number of Tasks: {len(event_tasks)}")
            
            print("\nTasks:")
            for i, task in enumerate(event_tasks, 1):
                print(f"  {i}. {task.title} - Status: {task.status}, Assigned to: {task.assigned_agent or 'Unassigned'}")
        
        return True
    
    finally:
        # Close the database session
        db.close()

if __name__ == "__main__":
    verify_project_plans()
