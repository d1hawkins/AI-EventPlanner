import asyncio
import json
import os
from datetime import datetime

from app.graphs.financial_graph import create_financial_graph, create_initial_state
from app.config import OPENAI_API_KEY, LLM_MODEL


async def run_financial_chat():
    """
    Run an interactive chat with the financial agent.
    """
    # Check if OpenAI API key is set
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    print(f"Using LLM model: {LLM_MODEL}")
    
    # Create the financial graph
    print("Initializing financial agent...")
    financial_graph = create_financial_graph()
    
    # Create initial state
    state = create_initial_state()
    
    # Add initial system message (marked as ephemeral so it won't be displayed in the UI)
    state["messages"].append({
        "role": "system",
        "content": "The conversation has started. The financial agent will help manage finances for your event.",
        "ephemeral": True
    })
    
    # Add a dummy user message to trigger the initial response
    state["messages"].append({
        "role": "user",
        "content": "I need help managing the finances for an event."
    })
    
    # Run the financial graph
    result = financial_graph.invoke(state)
    
    # Print the assistant's first message
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nFinancial Agent:", assistant_messages[-1]["content"])
    
    # Main conversation loop
    print("\nType 'exit' to end the conversation.")
    print("Type 'debug' to print the current state for debugging.")
    print("Type 'budget' to allocate budget based on the current event details.")
    print("Type 'expenses' to track expenses.")
    print("Type 'contracts' to manage contracts.")
    print("Type 'report' to generate a financial report.")
    print("Type 'plan' to generate a comprehensive financial plan.")
    
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
            print("Budget:", json.dumps(result["budget"], indent=2) if result["budget"] else "None")
            print("Expenses:", json.dumps(result["expenses"], indent=2) if result["expenses"] else "None")
            print("Contracts:", json.dumps(result["contracts"], indent=2) if result["contracts"] else "None")
            print("Current Phase:", result["current_phase"])
            print("Next Steps:", result["next_steps"])
            if "financial_plan" in result and result["financial_plan"]:
                print("Financial Plan:", json.dumps(result["financial_plan"], indent=2))
            continue
        
        # Add user message to state
        result["messages"].append({
            "role": "user",
            "content": user_input
        })
        
        # Handle special commands
        if user_input.lower() == "budget":
            # Force the agent to allocate budget
            result = financial_graph.invoke(result, {"override_next": "allocate_budget"})
        elif user_input.lower() == "expenses":
            # Force the agent to track expenses
            result = financial_graph.invoke(result, {"override_next": "track_expenses"})
        elif user_input.lower() == "contracts":
            # Force the agent to manage contracts
            result = financial_graph.invoke(result, {"override_next": "manage_contracts"})
        elif user_input.lower() == "report":
            # Force the agent to generate a financial report
            result = financial_graph.invoke(result, {"override_next": "generate_financial_report"})
        elif user_input.lower() == "plan":
            # Force the agent to generate a financial plan
            result = financial_graph.invoke(result, {"override_next": "generate_financial_plan"})
        else:
            # Run the financial graph with normal flow
            result = financial_graph.invoke(result)
        
        # Print the assistant's response
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        if assistant_messages:
            print("\nFinancial Agent:", assistant_messages[-1]["content"])


if __name__ == "__main__":
    # Run the interactive chat
    asyncio.run(run_financial_chat())
