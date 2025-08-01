import asyncio
import json
import os
from datetime import datetime

from app.graphs.compliance_security_graph import create_compliance_security_graph, create_initial_state
from app.config import OPENAI_API_KEY, LLM_MODEL


async def run_compliance_chat():
    """
    Run an interactive chat with the compliance and security agent.
    """
    # Check if OpenAI API key is set
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    print(f"Using LLM model: {LLM_MODEL}")
    
    # Create the compliance and security graph
    print("Initializing Compliance & Security Agent...")
    compliance_security_graph = create_compliance_security_graph()
    
    # Create initial state
    state = create_initial_state()
    
    # Add initial system message (marked as ephemeral so it won't be displayed in the UI)
    state["messages"].append({
        "role": "system",
        "content": "The conversation has started. The Compliance & Security Agent will help ensure regulatory compliance and security for your event.",
        "ephemeral": True
    })
    
    # Add a dummy user message to trigger the initial response
    state["messages"].append({
        "role": "user",
        "content": "I need help with compliance and security for an event."
    })
    
    # Run the compliance and security graph
    result = compliance_security_graph.invoke(state)
    
    # Print the assistant's first message
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nCompliance & Security Agent:", assistant_messages[-1]["content"])
    
    # Main conversation loop
    print("\nType 'exit' to end the conversation.")
    print("Type 'debug' to print the current state for debugging.")
    print("Type 'requirements' to track compliance requirements.")
    print("Type 'security' to plan security measures.")
    print("Type 'data' to implement data protection measures.")
    print("Type 'audit' to conduct a compliance audit.")
    print("Type 'incident' to plan incident response.")
    print("Type 'report' to generate a compliance report.")
    print("Type 'updates' to monitor regulatory updates.")
    
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
            print("Compliance Requirements:", json.dumps(result["compliance_requirements"], indent=2) if result["compliance_requirements"] else "None")
            print("Security Protocols:", json.dumps(result["security_protocols"], indent=2) if result["security_protocols"] else "None")
            print("Data Protection Measures:", json.dumps(result["data_protection_measures"], indent=2) if result["data_protection_measures"] else "None")
            print("Compliance Audits:", json.dumps(result["compliance_audits"], indent=2) if result["compliance_audits"] else "None")
            print("Incident Response Plans:", json.dumps(result["incident_response_plans"], indent=2) if result["incident_response_plans"] else "None")
            print("Compliance Reports:", json.dumps(result["compliance_reports"], indent=2) if result["compliance_reports"] else "None")
            print("Regulatory Updates:", json.dumps(result["regulatory_updates"], indent=2) if result["regulatory_updates"] else "None")
            print("Current Phase:", result["current_phase"])
            print("Next Steps:", result["next_steps"])
            continue
        
        # Add user message to state
        result["messages"].append({
            "role": "user",
            "content": user_input
        })
        
        # Handle special commands
        if user_input.lower() == "requirements":
            # Force the agent to track requirements
            result = compliance_security_graph.invoke(result, {"override_next": "track_requirements"})
        elif user_input.lower() == "security":
            # Force the agent to plan security measures
            result = compliance_security_graph.invoke(result, {"override_next": "plan_security"})
        elif user_input.lower() == "data":
            # Force the agent to implement data protection measures
            result = compliance_security_graph.invoke(result, {"override_next": "implement_data_protection"})
        elif user_input.lower() == "audit":
            # Force the agent to conduct a compliance audit
            result = compliance_security_graph.invoke(result, {"override_next": "conduct_audit"})
        elif user_input.lower() == "incident":
            # Force the agent to plan incident response
            result = compliance_security_graph.invoke(result, {"override_next": "plan_incident_response"})
        elif user_input.lower() == "report":
            # Force the agent to generate a compliance report
            result = compliance_security_graph.invoke(result, {"override_next": "generate_report"})
        elif user_input.lower() == "updates":
            # Force the agent to monitor regulatory updates
            result = compliance_security_graph.invoke(result, {"override_next": "monitor_updates"})
        else:
            # Run the compliance and security graph with normal flow
            result = compliance_security_graph.invoke(result)
        
        # Print the assistant's response
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        if assistant_messages:
            print("\nCompliance & Security Agent:", assistant_messages[-1]["content"])


if __name__ == "__main__":
    # Run the interactive chat
    asyncio.run(run_compliance_chat())
