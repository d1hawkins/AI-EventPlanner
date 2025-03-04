import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.graphs.project_management_graph import create_project_management_graph, create_initial_state
from app.utils.llm_factory import get_llm


async def run_project_management_agent(event_details: Dict[str, Any], user_input: str) -> Dict[str, Any]:
    """
    Run the project management agent with the given event details and user input.
    
    Args:
        event_details: Event details
        user_input: User input message
        
    Returns:
        Dictionary with the agent's response
    """
    # Create the project management graph
    project_management_graph = create_project_management_graph()
    
    # Create initial state
    state = create_initial_state()
    
    # Update state with event details
    for key, value in event_details.items():
        if key in state["event_details"]:
            state["event_details"][key] = value
    
    # Add user message
    state["messages"].append({
        "role": "user",
        "content": user_input
    })
    
    # Run the project management graph
    result = project_management_graph.invoke(state)
    
    # Extract the response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    response = assistant_messages[-1]["content"] if assistant_messages else "No response from Project Management Agent"
    
    return {
        "response": response,
        "tasks": result.get("tasks", []),
        "milestones": result.get("milestones", []),
        "risks": result.get("risks", []),
        "timeline": result.get("timeline"),
        "project_plan": result.get("project_plan")
    }


async def main():
    """Run the project management agent with sample data."""
    # Sample event details
    event_details = {
        "event_type": "conference",
        "title": "Tech Innovation Summit 2025",
        "description": "A conference showcasing the latest technology innovations and trends",
        "attendee_count": 500,
        "scale": "medium",
        "timeline_start": (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + 
                          timedelta(days=90)).isoformat(),
        "timeline_end": (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + 
                        timedelta(days=92)).isoformat(),
        "budget": 100000,
        "location": "San Francisco"
    }
    
    # Sample user input
    user_input = "I need a project plan for our upcoming tech conference. It's a 3-day event with about 500 attendees. We need to track all tasks, milestones, and potential risks."
    
    # Run the project management agent
    result = await run_project_management_agent(event_details, user_input)
    
    # Print the response
    print("\n=== Project Management Agent Response ===\n")
    print(result["response"])
    
    # Print summary of tasks, milestones, and risks
    print("\n=== Tasks ===\n")
    for task in result.get("tasks", [])[:3]:  # Show only first 3 for brevity
        print(f"- {task['name']} ({task['priority']} priority): {task['status']}, Assigned to: {task.get('assigned_to', 'Unassigned')}")
    if len(result.get("tasks", [])) > 3:
        print(f"... and {len(result.get('tasks', [])) - 3} more tasks")
    
    print("\n=== Milestones ===\n")
    for milestone in result.get("milestones", [])[:3]:  # Show only first 3 for brevity
        print(f"- {milestone['name']}: {milestone['status']}, Date: {milestone.get('date', 'No date set')}")
    if len(result.get("milestones", [])) > 3:
        print(f"... and {len(result.get('milestones', [])) - 3} more milestones")
    
    print("\n=== Risks ===\n")
    for risk in result.get("risks", [])[:3]:  # Show only first 3 for brevity
        print(f"- {risk['name']} (Probability: {risk.get('probability', 'unknown')}, Impact: {risk.get('impact', 'unknown')}): {risk.get('status', 'identified')}")
    if len(result.get("risks", [])) > 3:
        print(f"... and {len(result.get('risks', [])) - 3} more risks")
    
    # Print project plan summary if available
    if result.get("project_plan"):
        print("\n=== Project Plan Summary ===\n")
        print(f"Status: {result['project_plan'].get('status_summary', 'Unknown')}")
        print(f"Tasks: {len(result['project_plan'].get('tasks', []))}")
        print(f"Milestones: {len(result['project_plan'].get('milestones', []))}")
        print(f"Risks: {len(result['project_plan'].get('risks', []))}")


if __name__ == "__main__":
    asyncio.run(main())
