import asyncio
import json
from datetime import datetime

from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state
from app.tools.agent_communication_tools import ResourcePlanningTaskTool
from app.config import OPENAI_API_KEY, LLM_MODEL


async def test_agent_integration():
    """
    Test the integration between the Coordinator Agent and the Resource Planning Agent.
    """
    # Check if OpenAI API key is set
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    print(f"Using LLM model: {LLM_MODEL}")
    
    # Create the coordinator graph
    print("Initializing coordinator agent...")
    coordinator_graph = create_coordinator_graph()
    
    # Create initial state with some predefined event details
    state = create_initial_state()
    
    # Add initial system message
    state["messages"].append({
        "role": "system",
        "content": "The conversation has started. The coordinator agent will help plan your event.",
        "ephemeral": True
    })
    
    # Set some event details for testing
    state["event_details"] = {
        "event_type": "conference",
        "title": "Tech Innovation Summit 2025",
        "description": "A conference focused on emerging technologies and innovation",
        "attendee_count": 300,
        "scale": "medium",
        "timeline_start": "2025-06-15",
        "timeline_end": "2025-06-17",
        "budget": 75000,
        "location": "San Francisco"
    }
    
    # Set all information as collected for testing
    for category in state["information_collected"]:
        state["information_collected"][category] = True
    
    # Add some requirements
    state["requirements"] = {
        "stakeholders": ["speakers", "sponsors", "attendees"],
        "resources": ["venue", "catering", "AV equipment", "registration system"],
        "risks": ["weather issues", "speaker cancellations", "technical failures"],
        "success_criteria": ["attendee satisfaction", "sponsor ROI", "media coverage"],
        "budget": {"range": "$50,000-$100,000", "allocation_priorities": ["venue", "catering", "marketing"]},
        "location": {"preferences": ["downtown", "near airport"], "venue_type": "hotel or convention center", "space_requirements": "main hall and breakout rooms"}
    }
    
    # Add a proposal
    state["proposal"] = {
        "content": "This is a test proposal for the Tech Innovation Summit 2025.",
        "generated_at": datetime.utcnow().isoformat(),
        "status": "approved"
    }
    
    # Add a user message to trigger task delegation
    state["messages"].append({
        "role": "user",
        "content": "Please delegate tasks to the specialized agents to start implementing the event plan."
    })
    
    # Set the current phase to task delegation
    state["current_phase"] = "task_delegation"
    
    # Run the coordinator graph to delegate tasks
    print("\nDelegating tasks to specialized agents...")
    result = coordinator_graph.invoke(state, {"override_next": "delegate_tasks"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nCoordinator Agent:", assistant_messages[-1]["content"])
    
    # Print all agent assignments for debugging
    print("\nAll Agent Assignments:")
    for assignment in result["agent_assignments"]:
        print(f"- Agent Type: {assignment['agent_type']}")
        print(f"  Task: {assignment['task']}")
        print(f"  Status: {assignment['status']}")
        if "result" in assignment:
            print(f"  Result: {assignment['result'][:100]}..." if len(assignment['result']) > 100 else assignment['result'])
    
    # Check if tasks were delegated to the Resource Planning Agent
    resource_planning_tasks = [a for a in result["agent_assignments"] if a["agent_type"] == "resource_planning"]
    if resource_planning_tasks:
        print("\nResource Planning Agent Tasks:")
        for task in resource_planning_tasks:
            print(f"- Task: {task['task']}")
            print(f"  Status: {task['status']}")
            if task.get("result"):
                print(f"  Result: {task['result'][:100]}..." if len(task['result']) > 100 else task['result'])
    else:
        print("\nNo tasks were delegated to the Resource Planning Agent.")
    
    # Print the agent_results for debugging
    if "agent_results" in result:
        print("\nAgent Results:")
        for agent_type, results in result["agent_results"].items():
            print(f"- {agent_type}: {list(results.keys())}")
    else:
        print("\nNo agent_results found in the state.")
    
    # Check if there are any results from the Resource Planning Agent
    if "agent_results" in result and "resource_planning" in result["agent_results"]:
        resource_results = result["agent_results"]["resource_planning"]
        print("\nResource Planning Agent Results:")
        
        if "venue_options" in resource_results and resource_results["venue_options"]:
            print(f"\nVenue Options: {len(resource_results['venue_options'])} options found")
            for venue in resource_results["venue_options"][:2]:  # Show only first 2 for brevity
                print(f"- {venue['name']} ({venue['type']})")
                print(f"  Capacity: {venue['capacity']}, Price: ${venue['price_per_day']} per day")
            if len(resource_results["venue_options"]) > 2:
                print(f"- ... and {len(resource_results['venue_options']) - 2} more")
        
        if "selected_venue" in resource_results and resource_results["selected_venue"]:
            venue = resource_results["selected_venue"]
            print(f"\nSelected Venue: {venue.get('name', 'Unknown')} ({venue.get('type', 'Unknown')})")
            print(f"Capacity: {venue.get('capacity', 'Unknown')}, Price: ${venue.get('price_per_day', 'Unknown')} per day")
        
        if "service_providers" in resource_results and resource_results["service_providers"]:
            print(f"\nService Providers: {len(resource_results['service_providers'])} providers found")
            for provider in resource_results["service_providers"][:2]:  # Show only first 2 for brevity
                print(f"- {provider.get('name', 'Unknown')} ({provider.get('type', 'Unknown')})")
            if len(resource_results["service_providers"]) > 2:
                print(f"- ... and {len(resource_results['service_providers']) - 2} more")
        
        if "equipment_needs" in resource_results and resource_results["equipment_needs"]:
            print(f"\nEquipment Needs: {len(resource_results['equipment_needs'])} categories")
            for category in resource_results["equipment_needs"][:2]:  # Show only first 2 for brevity
                print(f"- {category.get('category', 'Unknown')}: {len(category.get('items', []))} items")
            if len(resource_results["equipment_needs"]) > 2:
                print(f"- ... and {len(resource_results['equipment_needs']) - 2} more categories")
        
        if "resource_plan" in resource_results and resource_results["resource_plan"]:
            print("\nResource Plan Summary:")
            if "summary" in resource_results["resource_plan"]:
                summary = resource_results["resource_plan"]["summary"]
                print(f"- Event Type: {summary.get('event_type', 'Unknown')}")
                print(f"- Location: {summary.get('location', 'Unknown')}")
                print(f"- Attendee Count: {summary.get('attendee_count', 'Unknown')}")
                print(f"- Total Cost: ${summary.get('total_cost', 'Unknown')}")
    
    # Now get a status report that includes the Resource Planning Agent results
    print("\nGenerating status report...")
    result = coordinator_graph.invoke(result, {"override_next": "provide_status"})
    
    # Print the status report
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nStatus Report:", assistant_messages[-1]["content"])
    
    # Test the ResourcePlanningTaskTool directly
    print("\n\n=== Testing ResourcePlanningTaskTool Directly ===")
    resource_planning_tool = ResourcePlanningTaskTool()
    task = "Find a suitable venue in downtown San Francisco near the airport that can accommodate 300 attendees and has a main hall and breakout rooms."
    event_details = {
        "event_type": "conference",
        "title": "Tech Innovation Summit 2025",
        "description": "A conference focused on emerging technologies and innovation",
        "attendee_count": 300,
        "scale": "medium",
        "timeline_start": "2025-06-15",
        "timeline_end": "2025-06-17",
        "budget": 75000,
        "location": "San Francisco"
    }
    requirements = {
        "stakeholders": ["speakers", "sponsors", "attendees"],
        "resources": ["venue", "catering", "AV equipment", "registration system"],
        "risks": ["weather issues", "speaker cancellations", "technical failures"],
        "success_criteria": ["attendee satisfaction", "sponsor ROI", "media coverage"],
        "budget": {"range": "$50,000-$100,000", "allocation_priorities": ["venue", "catering", "marketing"]},
        "location": {"preferences": ["downtown", "near airport"], "venue_type": "hotel or convention center", "space_requirements": "main hall and breakout rooms"}
    }
    
    print(f"Delegating task directly to Resource Planning Agent: {task}")
    task_result = resource_planning_tool._run(
        task=task,
        event_details=event_details,
        requirements=requirements
    )
    
    print("\nResource Planning Tool Result:")
    print(f"Task: {task_result['task']}")
    print(f"Response: {task_result['response'][:100]}..." if len(task_result['response']) > 100 else task_result['response'])
    
    if task_result.get("venue_options"):
        print(f"\nVenue Options: {len(task_result['venue_options'])} options found")
        for venue in task_result["venue_options"][:2]:  # Show only first 2 for brevity
            print(f"- {venue['name']} ({venue['type']})")
            print(f"  Capacity: {venue['capacity']}, Price: ${venue['price_per_day']} per day")
    
    if task_result.get("selected_venue"):
        venue = task_result["selected_venue"]
        print(f"\nSelected Venue: {venue.get('name', 'Unknown')} ({venue.get('type', 'Unknown')})")
        print(f"Capacity: {venue.get('capacity', 'Unknown')}, Price: ${venue.get('price_per_day', 'Unknown')} per day")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_agent_integration())
