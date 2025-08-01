import asyncio
import json
import os
from datetime import datetime

from app.graphs.analytics_graph import create_analytics_graph, create_initial_state
from app.config import OPENAI_API_KEY, LLM_MODEL


async def run_analytics_chat():
    """
    Run an interactive chat with the analytics agent.
    """
    # Check if OpenAI API key is set
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    print(f"Using LLM model: {LLM_MODEL}")
    
    # Create the analytics graph
    print("Initializing analytics agent...")
    analytics_graph = create_analytics_graph()
    
    # Create initial state
    state = create_initial_state()
    
    # Add initial system message (marked as ephemeral so it won't be displayed in the UI)
    state["messages"].append({
        "role": "system",
        "content": "The conversation has started. The analytics agent will help analyze data for your event.",
        "ephemeral": True
    })
    
    # Add a dummy user message to trigger the initial response
    state["messages"].append({
        "role": "user",
        "content": "I need help with analytics for an event."
    })
    
    # Run the analytics graph
    result = analytics_graph.invoke(state)
    
    # Print the assistant's first message
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nAnalytics Agent:", assistant_messages[-1]["content"])
    
    # Main conversation loop
    print("\nType 'exit' to end the conversation.")
    print("Type 'debug' to print the current state for debugging.")
    print("Type 'data' to configure data sources.")
    print("Type 'metrics' to define metrics.")
    print("Type 'segments' to create attendee segments.")
    print("Type 'surveys' to design surveys.")
    print("Type 'reports' to generate reports.")
    print("Type 'roi' to calculate ROI.")
    print("Type 'attendees' to analyze attendee data.")
    print("Type 'insights' to generate insights.")
    
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
            print("Data Sources:", json.dumps(result["data_sources"], indent=2) if "data_sources" in result and result["data_sources"] else "None")
            print("Metrics:", json.dumps(result["metrics"], indent=2) if "metrics" in result and result["metrics"] else "None")
            print("Segments:", json.dumps(result["segments"], indent=2) if "segments" in result and result["segments"] else "None")
            print("Surveys:", json.dumps(result["surveys"], indent=2) if "surveys" in result and result["surveys"] else "None")
            print("Reports:", json.dumps(result["reports"], indent=2) if "reports" in result and result["reports"] else "None")
            print("ROI Analysis:", json.dumps(result["roi_analysis"], indent=2) if "roi_analysis" in result and result["roi_analysis"] else "None")
            print("Attendee Analytics:", json.dumps(result["attendee_analytics"], indent=2) if "attendee_analytics" in result and result["attendee_analytics"] else "None")
            print("Insights:", json.dumps(result["insights"], indent=2) if "insights" in result and result["insights"] else "None")
            print("Current Phase:", result["current_phase"])
            print("Next Steps:", result["next_steps"])
            continue
        
        # Add user message to state
        result["messages"].append({
            "role": "user",
            "content": user_input
        })
        
        # Handle special commands
        if user_input.lower() == "data":
            # Force the agent to configure data sources
            result = analytics_graph.invoke(result, {"override_next": "configure_data_sources"})
        elif user_input.lower() == "metrics":
            # Force the agent to define metrics
            result = analytics_graph.invoke(result, {"override_next": "define_metrics"})
        elif user_input.lower() == "segments":
            # Force the agent to create segments
            result = analytics_graph.invoke(result, {"override_next": "create_segments"})
        elif user_input.lower() == "surveys":
            # Force the agent to design surveys
            result = analytics_graph.invoke(result, {"override_next": "design_surveys"})
        elif user_input.lower() == "reports":
            # Force the agent to generate reports
            result = analytics_graph.invoke(result, {"override_next": "generate_reports"})
        elif user_input.lower() == "roi":
            # Force the agent to calculate ROI
            result = analytics_graph.invoke(result, {"override_next": "calculate_roi"})
        elif user_input.lower() == "attendees":
            # Force the agent to analyze attendees
            result = analytics_graph.invoke(result, {"override_next": "analyze_attendees"})
        elif user_input.lower() == "insights":
            # Force the agent to generate insights
            result = analytics_graph.invoke(result, {"override_next": "generate_insights"})
        else:
            # Run the analytics graph with normal flow
            result = analytics_graph.invoke(result)
        
        # Print the assistant's response
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        if assistant_messages:
            print("\nAnalytics Agent:", assistant_messages[-1]["content"])


if __name__ == "__main__":
    # Run the interactive chat
    asyncio.run(run_analytics_chat())
