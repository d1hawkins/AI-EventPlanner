#!/usr/bin/env python3
"""
Script to verify that the project management agent writes project plans to the database
and that these plans are displayed on the Project Plan tab.
"""

import asyncio
import json
from datetime import datetime, timedelta

from app.db.base import SessionLocal
from app.db.models import Event, Task
from app.graphs.project_management_graph import create_project_management_graph, create_initial_state

async def verify_project_management_agent_writes_to_db():
    """
    Verify that the project management agent writes project plans to the database.
    
    This function:
    1. Creates a project management graph
    2. Initializes a state with event details
    3. Simulates a user request for a project plan
    4. Runs the project management graph
    5. Checks if tasks were written to the database
    
    Returns:
        bool: True if verification is successful, False otherwise
    """
    print("\n=== Verifying Project Management Agent Writes to Database ===\n")
    
    # Create the project management graph
    project_management_graph = create_project_management_graph()
    
    # Create initial state with event details
    state = create_initial_state()
    
    # Set event details
    event_id = "test_event_" + datetime.now().strftime("%Y%m%d%H%M%S")
    state["event_details"] = {
        "event_type": "conference",
        "title": "Test Conference",
        "description": "A test conference for verification",
        "attendee_count": 100,
        "scale": "small",
        "timeline_start": (datetime.now() + timedelta(days=30)).isoformat(),
        "timeline_end": (datetime.now() + timedelta(days=32)).isoformat(),
        "budget": 50000,
        "location": "Test Location"
    }
    
    # Add user message requesting a project plan
    state["messages"].append({
        "role": "user",
        "content": "I need a project plan for our upcoming conference. It's a 3-day event with about 100 attendees."
    })
    
    # Run the project management graph
    print("Running project management graph...")
    result = project_management_graph.invoke(state)
    print("Project management graph execution completed")
    
    # Check if tasks were created in the database
    db = SessionLocal()
    try:
        # Query for events created in the last minute
        recent_events = db.query(Event).filter(
            Event.created_at > datetime.utcnow() - timedelta(minutes=1)
        ).all()
        
        if not recent_events:
            print("No recent events found in the database")
            return False
        
        print(f"Found {len(recent_events)} recent events in the database")
        
        # Check if any of these events have tasks
        for event in recent_events:
            tasks = db.query(Task).filter(Task.event_id == event.id).all()
            if tasks:
                print(f"Event ID: {event.id}")
                print(f"Event Title: {event.title}")
                print(f"Event Type: {event.event_type}")
                print(f"Number of Tasks: {len(tasks)}")
                
                print("\nTasks:")
                for i, task in enumerate(tasks, 1):
                    print(f"  {i}. {task.title} - Status: {task.status}, Assigned to: {task.assigned_agent or 'Unassigned'}")
                
                return True
        
        print("No tasks found for recent events")
        return False
    
    finally:
        db.close()

def verify_tasks_display_on_website():
    """
    Verify that tasks are displayed on the Project Plan tab of the website.
    
    This function analyzes the JavaScript code to confirm that:
    1. There's a function to fetch tasks from the API
    2. There's a function to render tasks in the UI
    3. There's a mechanism to display tasks on the Project Plan tab
    
    Returns:
        bool: True if verification is successful, False otherwise
    """
    print("\n=== Verifying Tasks Display on Website ===\n")
    
    # Check if the necessary JavaScript functions exist
    with open("app/web/static/js/app.js", "r") as f:
        js_code = f.read()
    
    # Check for fetchTasks function
    if "function fetchTasks()" in js_code:
        print("✓ fetchTasks() function found")
    else:
        print("✗ fetchTasks() function not found")
        return False
    
    # Check for renderTasks function
    if "function renderTasks(tasks)" in js_code:
        print("✓ renderTasks() function found")
    else:
        print("✗ renderTasks() function not found")
        return False
    
    # Check for updateTaskStats function
    if "function updateTaskStats(tasks)" in js_code:
        print("✓ updateTaskStats() function found")
    else:
        print("✗ updateTaskStats() function not found")
        return False
    
    # Check for displayProjectPlan function
    if "function displayProjectPlan(content)" in js_code:
        print("✓ displayProjectPlan() function found")
    else:
        print("✗ displayProjectPlan() function not found")
        return False
    
    # Check for API endpoint call
    if "fetch(`/api/events/${currentEventId}/tasks`" in js_code:
        print("✓ API endpoint call to fetch tasks found")
    else:
        print("✗ API endpoint call to fetch tasks not found")
        return False
    
    # Check for task list rendering
    if "taskList.innerHTML = '';" in js_code and "tasks.forEach(task =>" in js_code:
        print("✓ Task list rendering code found")
    else:
        print("✗ Task list rendering code not found")
        return False
    
    # Check for Project Plan tab
    with open("app/web/static/index.html", "r") as f:
        html_code = f.read()
    
    if 'data-tab="project-plan"' in html_code and 'id="project-plan-content"' in html_code:
        print("✓ Project Plan tab found in HTML")
    else:
        print("✗ Project Plan tab not found in HTML")
        return False
    
    # Check for task list container
    if 'id="task-list"' in html_code:
        print("✓ Task list container found in HTML")
    else:
        print("✗ Task list container not found in HTML")
        return False
    
    return True

def verify_api_endpoints():
    """
    Verify that the API endpoints for tasks exist.
    
    This function checks if the API endpoints for retrieving and updating tasks exist.
    
    Returns:
        bool: True if verification is successful, False otherwise
    """
    print("\n=== Verifying API Endpoints ===\n")
    
    # Check if the necessary API endpoints exist
    with open("app/web/router.py", "r") as f:
        router_code = f.read()
    
    # Check for GET /events/{event_id}/tasks endpoint
    if "@router.get(\"/events/{event_id}/tasks\")" in router_code:
        print("✓ GET /events/{event_id}/tasks endpoint found")
    else:
        print("✗ GET /events/{event_id}/tasks endpoint not found")
        return False
    
    # Check for PUT /tasks/{task_id} endpoint
    if "@router.put(\"/tasks/{task_id}\")" in router_code:
        print("✓ PUT /tasks/{task_id} endpoint found")
    else:
        print("✗ PUT /tasks/{task_id} endpoint not found")
        return False
    
    return True

async def main():
    """
    Main function to run all verifications.
    """
    print("=== Project Management Verification ===")
    
    # Verify API endpoints
    api_endpoints_verified = verify_api_endpoints()
    
    # Verify tasks display on website
    tasks_display_verified = verify_tasks_display_on_website()
    
    # Verify project management agent writes to database
    db_write_verified = await verify_project_management_agent_writes_to_db()
    
    # Print summary
    print("\n=== Verification Summary ===")
    print(f"API Endpoints: {'✓ Verified' if api_endpoints_verified else '✗ Not Verified'}")
    print(f"Tasks Display on Website: {'✓ Verified' if tasks_display_verified else '✗ Not Verified'}")
    print(f"Project Management Agent Writes to Database: {'✓ Verified' if db_write_verified else '✗ Not Verified'}")
    
    # Overall verification result
    if api_endpoints_verified and tasks_display_verified and db_write_verified:
        print("\n✓ All verifications passed! Project plans with tasks are stored and displayed on the website.")
        return True
    else:
        print("\n✗ Some verifications failed. See details above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())
