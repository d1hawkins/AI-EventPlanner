import asyncio
import json
import os
from datetime import datetime

from app.graphs.stakeholder_management_graph import create_stakeholder_management_graph, create_initial_state
from app.config import OPENAI_API_KEY, LLM_MODEL


async def run_stakeholder_chat():
    """
    Run an interactive chat with the stakeholder management agent.
    """
    # Check if OpenAI API key is set
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    print(f"Using LLM model: {LLM_MODEL}")
    
    # Create the stakeholder management graph
    print("Initializing stakeholder management agent...")
    stakeholder_graph = create_stakeholder_management_graph()
    
    # Create initial state
    state = create_initial_state()
    
    # Add initial system message (marked as ephemeral so it won't be displayed in the UI)
    state["messages"].append({
        "role": "system",
        "content": "The conversation has started. The stakeholder management agent will help manage stakeholders for your event.",
        "ephemeral": True
    })
    
    # Add a dummy user message to trigger the initial response
    state["messages"].append({
        "role": "user",
        "content": "I need help managing the stakeholders for an event."
    })
    
    # Run the stakeholder management graph
    result = stakeholder_graph.invoke(state)
    
    # Print the assistant's first message
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nStakeholder Management Agent:", assistant_messages[-1]["content"])
    
    # Main conversation loop
    print("\nType 'exit' to end the conversation.")
    print("Type 'debug' to print the current state for debugging.")
    print("Type 'speakers' to manage speakers for the event.")
    print("Type 'sponsors' to manage sponsors for the event.")
    print("Type 'volunteers' to manage volunteers for the event.")
    print("Type 'vips' to manage VIP attendees for the event.")
    print("Type 'plan' to generate a comprehensive stakeholder management plan.")
    
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
            print("Speakers:", json.dumps(result["speakers"], indent=2) if result["speakers"] else "None")
            print("Sponsors:", json.dumps(result["sponsors"], indent=2) if result["sponsors"] else "None")
            print("Volunteers:", json.dumps(result["volunteers"], indent=2) if result["volunteers"] else "None")
            print("VIPs:", json.dumps(result["vips"], indent=2) if result["vips"] else "None")
            print("Current Phase:", result["current_phase"])
            print("Next Steps:", result["next_steps"])
            if "stakeholder_plan" in result and result["stakeholder_plan"]:
                print("Stakeholder Plan:", json.dumps(result["stakeholder_plan"], indent=2))
            continue
        
        # Add user message to state
        result["messages"].append({
            "role": "user",
            "content": user_input
        })
        
        # Handle special commands
        if user_input.lower() == "speakers":
            # Force the agent to manage speakers
            result = stakeholder_graph.invoke(result, {"override_next": "manage_speakers"})
        elif user_input.lower() == "sponsors":
            # Force the agent to manage sponsors
            result = stakeholder_graph.invoke(result, {"override_next": "manage_sponsors"})
        elif user_input.lower() == "volunteers":
            # Force the agent to manage volunteers
            result = stakeholder_graph.invoke(result, {"override_next": "manage_volunteers"})
        elif user_input.lower() == "vips":
            # Force the agent to manage VIPs
            result = stakeholder_graph.invoke(result, {"override_next": "manage_vips"})
        elif user_input.lower() == "plan":
            # Force the agent to generate a stakeholder plan
            result = stakeholder_graph.invoke(result, {"override_next": "generate_stakeholder_plan"})
        else:
            # Run the stakeholder management graph with normal flow
            result = stakeholder_graph.invoke(result)
        
        # Print the assistant's response
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        if assistant_messages:
            print("\nStakeholder Management Agent:", assistant_messages[-1]["content"])


if __name__ == "__main__":
    # Run the interactive chat
    asyncio.run(run_stakeholder_chat())
