import asyncio
import json
from datetime import datetime, timedelta

from app.graphs.project_management_graph import create_project_management_graph, create_initial_state


async def test_project_management_agent():
    """Test the project management agent with various scenarios."""
    # Create the project management graph
    project_management_graph = create_project_management_graph()
    
    # Test case 1: Basic project planning
    print("\n=== Test Case 1: Basic Project Planning ===\n")
    
    # Create initial state
    state = create_initial_state()
    
    # Set event details
    state["event_details"] = {
        "event_type": "conference",
        "title": "Tech Innovation Summit 2025",
        "description": "A conference showcasing the latest technology innovations and trends",
        "attendee_count": 500,
        "scale": "medium",
        "timeline_start": (datetime.now() + timedelta(days=90)).isoformat(),
        "timeline_end": (datetime.now() + timedelta(days=92)).isoformat(),
        "budget": 100000,
        "location": "San Francisco"
    }
    
    # Add user message
    state["messages"].append({
        "role": "user",
        "content": "I need a project plan for our upcoming tech conference. It's a 3-day event with about 500 attendees. We need to track all tasks, milestones, and potential risks."
    })
    
    # Run the project management graph
    result = project_management_graph.invoke(state)
    
    # Print the response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    response = assistant_messages[-1]["content"] if assistant_messages else "No response"
    print(f"Response: {response[:500]}...\n")  # Print first 500 chars for brevity
    
    # Print summary
    print(f"Tasks: {len(result.get('tasks', []))}")
    print(f"Milestones: {len(result.get('milestones', []))}")
    print(f"Risks: {len(result.get('risks', []))}")
    print(f"Timeline: {'Generated' if result.get('timeline') else 'Not generated'}")
    print(f"Project Plan: {'Generated' if result.get('project_plan') else 'Not generated'}")
    
    # Test case 2: Task management
    print("\n=== Test Case 2: Task Management ===\n")
    
    # Create initial state with existing tasks
    state = create_initial_state()
    
    # Set event details
    state["event_details"] = {
        "event_type": "corporate",
        "title": "Annual Company Retreat",
        "description": "A team-building retreat for the company's employees",
        "attendee_count": 100,
        "scale": "small",
        "timeline_start": (datetime.now() + timedelta(days=60)).isoformat(),
        "timeline_end": (datetime.now() + timedelta(days=62)).isoformat(),
        "budget": 50000,
        "location": "Lake Tahoe"
    }
    
    # Add some existing tasks
    state["tasks"] = [
        {
            "id": "task1",
            "name": "Book venue",
            "description": "Find and book a suitable venue for the retreat",
            "status": "completed",
            "priority": "high",
            "assigned_to": "Resource Planning Agent",
            "dependencies": [],
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": (datetime.now() - timedelta(days=20)).isoformat(),
            "actual_start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "actual_end_date": (datetime.now() - timedelta(days=20)).isoformat(),
            "completion_percentage": 100,
            "notes": None
        },
        {
            "id": "task2",
            "name": "Plan activities",
            "description": "Plan team-building activities for the retreat",
            "status": "in_progress",
            "priority": "medium",
            "assigned_to": "Coordinator Agent",
            "dependencies": ["task1"],
            "start_date": (datetime.now() - timedelta(days=15)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=15)).isoformat(),
            "actual_start_date": (datetime.now() - timedelta(days=15)).isoformat(),
            "actual_end_date": None,
            "completion_percentage": 50,
            "notes": None
        }
    ]
    
    # Add user message
    state["messages"].append({
        "role": "user",
        "content": "I need to add a new task for arranging transportation to the retreat. It should be assigned to the Resource Planning Agent and should be completed by 2 weeks before the retreat."
    })
    
    # Run the project management graph
    result = project_management_graph.invoke(state)
    
    # Print the response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    response = assistant_messages[-1]["content"] if assistant_messages else "No response"
    print(f"Response: {response[:500]}...\n")  # Print first 500 chars for brevity
    
    # Print summary
    print(f"Tasks: {len(result.get('tasks', []))}")
    for task in result.get("tasks", []):
        print(f"- {task['name']} ({task['priority']} priority): {task['status']}, Assigned to: {task.get('assigned_to', 'Unassigned')}")
    
    # Test case 3: Risk management
    print("\n=== Test Case 3: Risk Management ===\n")
    
    # Create initial state with existing risks
    state = create_initial_state()
    
    # Set event details
    state["event_details"] = {
        "event_type": "wedding",
        "title": "Smith-Johnson Wedding",
        "description": "A wedding ceremony and reception",
        "attendee_count": 150,
        "scale": "medium",
        "timeline_start": (datetime.now() + timedelta(days=120)).isoformat(),
        "timeline_end": (datetime.now() + timedelta(days=120)).isoformat(),
        "budget": 30000,
        "location": "Napa Valley"
    }
    
    # Add some existing risks
    state["risks"] = [
        {
            "id": "risk1",
            "name": "Weather Issues",
            "description": "Outdoor ceremony may be affected by bad weather",
            "probability": "medium",
            "impact": "high",
            "status": "identified",
            "mitigation_plan": "Have a backup indoor location",
            "contingency_plan": "Set up tents or move indoors if weather forecast is poor",
            "owner": "Resource Planning Agent"
        }
    ]
    
    # Add user message
    state["messages"].append({
        "role": "user",
        "content": "I'm worried about vendor reliability. Can you add this as a risk and suggest how to mitigate it?"
    })
    
    # Run the project management graph
    result = project_management_graph.invoke(state)
    
    # Print the response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    response = assistant_messages[-1]["content"] if assistant_messages else "No response"
    print(f"Response: {response[:500]}...\n")  # Print first 500 chars for brevity
    
    # Print summary
    print(f"Risks: {len(result.get('risks', []))}")
    for risk in result.get("risks", []):
        print(f"- {risk['name']} (Probability: {risk.get('probability', 'unknown')}, Impact: {risk.get('impact', 'unknown')}): {risk.get('status', 'identified')}")
        if risk.get("mitigation_plan"):
            print(f"  Mitigation: {risk['mitigation_plan']}")


if __name__ == "__main__":
    asyncio.run(test_project_management_agent())
