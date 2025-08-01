import asyncio
import json
import os
from datetime import datetime

from app.graphs.resource_planning_graph import create_resource_planning_graph, create_initial_state
from app.config import OPENAI_API_KEY, LLM_MODEL


async def run_resource_planning_chat():
    """
    Run an interactive chat with the resource planning agent.
    """
    # Check if OpenAI API key is set
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    print(f"Using LLM model: {LLM_MODEL}")
    
    # Create the resource planning graph
    print("Initializing resource planning agent...")
    resource_planning_graph = create_resource_planning_graph()
    
    # Create initial state
    state = create_initial_state()
    
    # Add initial system message (marked as ephemeral so it won't be displayed in the UI)
    state["messages"].append({
        "role": "system",
        "content": "The conversation has started. The resource planning agent will help plan resources for your event.",
        "ephemeral": True
    })
    
    # Add a dummy user message to trigger the initial response
    state["messages"].append({
        "role": "user",
        "content": "I need help planning resources for an event."
    })
    
    # Run the resource planning graph
    result = resource_planning_graph.invoke(state)
    
    # Print the assistant's first message
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nResource Planning Agent:", assistant_messages[-1]["content"])
    
    # Main conversation loop
    print("\nType 'exit' to end the conversation.")
    print("Type 'debug' to print the current state for debugging.")
    print("Type 'venues' to search for venues based on the current event details.")
    print("Type 'providers' to search for service providers.")
    print("Type 'equipment' to plan equipment needs.")
    print("Type 'plan' to generate a comprehensive resource plan.")
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit command
        if user_input.lower() == "exit":
            print("Ending conversation.")
            break
        
        # Check for debug command
        if user_input.lower() == "debug":
            print("\n=== Current State ===")
            print("Event Details:", json.dumps(result["event_details"], indent=2))
            print("Venue Options:", json.dumps(result["venue_options"], indent=2) if result["venue_options"] else "None")
            print("Selected Venue:", json.dumps(result["selected_venue"], indent=2) if result["selected_venue"] else "None")
            print("Service Providers:", json.dumps(result["service_providers"], indent=2) if result["service_providers"] else "None")
            print("Equipment Needs:", json.dumps(result["equipment_needs"], indent=2) if result["equipment_needs"] else "None")
            print("Current Phase:", result["current_phase"])
            print("Next Steps:", result["next_steps"])
            if "resource_plan" in result and result["resource_plan"]:
                print("Resource Plan Summary:", json.dumps(result["resource_plan"]["summary"], indent=2))
            continue
        
        # Add user message to state
        result["messages"].append({
            "role": "user",
            "content": user_input
        })
        
        # Handle special commands
        if user_input.lower() == "venues":
            # Force the agent to search for venues
            result = resource_planning_graph.invoke(result, {"override_next": "search_venues"})
        elif user_input.lower() == "providers":
            # Force the agent to search for service providers
            result = resource_planning_graph.invoke(result, {"override_next": "search_service_providers"})
        elif user_input.lower() == "equipment":
            # Force the agent to plan equipment needs
            result = resource_planning_graph.invoke(result, {"override_next": "plan_equipment"})
        elif user_input.lower() == "plan":
            # Force the agent to generate a resource plan
            result = resource_planning_graph.invoke(result, {"override_next": "generate_resource_plan"})
        else:
            # Run the resource planning graph with normal flow
            result = resource_planning_graph.invoke(result)
        
        # Print the assistant's response
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        if assistant_messages:
            print("\nResource Planning Agent:", assistant_messages[-1]["content"])


if __name__ == "__main__":
    # Run the interactive chat
    asyncio.run(run_resource_planning_chat())
