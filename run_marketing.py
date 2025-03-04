import asyncio
import json
import os
from datetime import datetime

from app.graphs.marketing_communications_graph import create_marketing_communications_graph, create_initial_state
from app.config import OPENAI_API_KEY, LLM_MODEL


async def run_marketing_agent():
    """
    Run the Marketing & Communications Agent.
    """
    # Check if OpenAI API key is set
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    print(f"Using LLM model: {LLM_MODEL}")
    
    # Create the marketing communications graph
    print("Initializing Marketing & Communications Agent...")
    marketing_graph = create_marketing_communications_graph()
    
    # Create initial state
    state = create_initial_state()
    
    # Add initial system message
    state["messages"].append({
        "role": "system",
        "content": "The conversation has started. The Marketing & Communications Agent will help you with marketing strategies, content creation, and communication plans for your event.",
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
    
    # Add a welcome message
    state["messages"].append({
        "role": "assistant",
        "content": "Hello! I'm your Marketing & Communications Agent for the Tech Innovation Summit 2025. I can help you with:\n\n- Developing marketing strategies\n- Creating content for various channels\n- Managing attendee registrations\n- Designing communication plans\n- Setting up marketing campaigns\n\nWhat aspect of marketing or communications would you like to work on today?"
    })
    
    # Interactive conversation loop
    try:
        while True:
            # Get user input
            user_input = input("\nYou: ")
            
            # Exit condition
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nExiting Marketing & Communications Agent. Goodbye!")
                break
            
            # Add user message to state
            state["messages"].append({
                "role": "user",
                "content": user_input
            })
            
            # Run the marketing communications graph
            print("\nProcessing...")
            result = marketing_graph.invoke(state)
            
            # Update state
            state = result
            
            # Print the assistant's response
            assistant_messages = [m for m in state["messages"] if m["role"] == "assistant" and not m.get("ephemeral", False)]
            if assistant_messages:
                print(f"\nMarketing & Communications Agent: {assistant_messages[-1]['content']}")
    
    except KeyboardInterrupt:
        print("\n\nExiting Marketing & Communications Agent. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")


if __name__ == "__main__":
    # Run the marketing agent
    asyncio.run(run_marketing_agent())
