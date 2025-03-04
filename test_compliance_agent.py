import asyncio
import json
from datetime import datetime

from app.graphs.compliance_security_graph import create_compliance_security_graph, create_initial_state
from app.config import OPENAI_API_KEY, LLM_MODEL


async def test_compliance_agent():
    """
    Test the Compliance & Security Agent's functionality.
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
    
    # Create initial state with some predefined event details
    state = create_initial_state()
    
    # Add initial system message
    state["messages"].append({
        "role": "system",
        "content": "The conversation has started. The Compliance & Security Agent will help ensure regulatory compliance and security for your event.",
        "ephemeral": True
    })
    
    # Set some event details for testing
    state["event_details"] = {
        "event_type": "conference",
        "title": "Tech Innovation Summit 2025",
        "description": "A conference focused on emerging technologies and innovation",
        "attendee_count": 500,
        "scale": "medium",
        "timeline_start": "2025-06-15",
        "timeline_end": "2025-06-17",
        "budget": 100000,
        "location": "San Francisco"
    }
    
    # Test 1: Analyze Compliance Requirements
    print("\n=== Test 1: Analyze Compliance Requirements ===")
    
    # Add a user message to trigger compliance analysis
    state["messages"].append({
        "role": "user",
        "content": "I need to understand the compliance requirements for our Tech Innovation Summit in San Francisco. It's a 3-day conference with about 500 attendees."
    })
    
    # Run the compliance and security graph to analyze requirements
    result = compliance_security_graph.invoke(state, {"override_next": "analyze_requirements"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nCompliance & Security Agent (Requirements Analysis):", assistant_messages[-1]["content"])
    
    # Test 2: Track Requirements
    print("\n=== Test 2: Track Requirements ===")
    
    # Add a user message to trigger requirement tracking
    result["messages"].append({
        "role": "user",
        "content": "I need to track and manage these compliance requirements. What documentation do I need and what are the verification steps?"
    })
    
    # Run the compliance and security graph to track requirements
    result = compliance_security_graph.invoke(result, {"override_next": "track_requirements"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nCompliance & Security Agent (Requirement Tracking):", assistant_messages[-1]["content"])
    
    # Test 3: Plan Security
    print("\n=== Test 3: Plan Security ===")
    
    # Add a user message to trigger security planning
    result["messages"].append({
        "role": "user",
        "content": "I need to plan security measures for the event. What should I consider for physical security, access control, and emergency response?"
    })
    
    # Run the compliance and security graph to plan security
    result = compliance_security_graph.invoke(result, {"override_next": "plan_security"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nCompliance & Security Agent (Security Planning):", assistant_messages[-1]["content"])
    
    # Test 4: Implement Data Protection
    print("\n=== Test 4: Implement Data Protection ===")
    
    # Add a user message to trigger data protection implementation
    result["messages"].append({
        "role": "user",
        "content": "I need to implement data protection measures for the event. We'll be collecting attendee personal information, contact details, and payment information."
    })
    
    # Run the compliance and security graph to implement data protection
    result = compliance_security_graph.invoke(result, {"override_next": "implement_data_protection"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nCompliance & Security Agent (Data Protection):", assistant_messages[-1]["content"])
    
    # Test 5: Conduct Audit
    print("\n=== Test 5: Conduct Audit ===")
    
    # Add a user message to trigger compliance audit
    result["messages"].append({
        "role": "user",
        "content": "I need to conduct a compliance audit to ensure we're meeting all requirements. What should this audit cover?"
    })
    
    # Run the compliance and security graph to conduct audit
    result = compliance_security_graph.invoke(result, {"override_next": "conduct_audit"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nCompliance & Security Agent (Compliance Audit):", assistant_messages[-1]["content"])
    
    # Test 6: Plan Incident Response
    print("\n=== Test 6: Plan Incident Response ===")
    
    # Add a user message to trigger incident response planning
    result["messages"].append({
        "role": "user",
        "content": "I need to plan incident response procedures for potential security breaches, medical emergencies, and evacuations."
    })
    
    # Run the compliance and security graph to plan incident response
    result = compliance_security_graph.invoke(result, {"override_next": "plan_incident_response"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nCompliance & Security Agent (Incident Response):", assistant_messages[-1]["content"])
    
    # Test 7: Generate Report
    print("\n=== Test 7: Generate Report ===")
    
    # Add a user message to trigger report generation
    result["messages"].append({
        "role": "user",
        "content": "I need a comprehensive compliance and security report that I can share with stakeholders."
    })
    
    # Run the compliance and security graph to generate report
    result = compliance_security_graph.invoke(result, {"override_next": "generate_report"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nCompliance & Security Agent (Report):", assistant_messages[-1]["content"])
    
    # Test 8: Monitor Updates
    print("\n=== Test 8: Monitor Updates ===")
    
    # Add a user message to trigger regulatory update monitoring
    result["messages"].append({
        "role": "user",
        "content": "Are there any recent or upcoming regulatory changes that might affect our event compliance?"
    })
    
    # Run the compliance and security graph to monitor updates
    result = compliance_security_graph.invoke(result, {"override_next": "monitor_updates"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nCompliance & Security Agent (Regulatory Updates):", assistant_messages[-1]["content"])
    
    # Print the final state for debugging
    print("\n=== Final State ===")
    print("Compliance Requirements:", f"{len(result['compliance_requirements'])} requirements identified" if result["compliance_requirements"] else "None")
    print("Security Protocols:", f"{len(result['security_protocols'])} protocols defined" if result["security_protocols"] else "None")
    print("Data Protection Measures:", f"{len(result['data_protection_measures'])} measures implemented" if result["data_protection_measures"] else "None")
    print("Compliance Audits:", f"{len(result['compliance_audits'])} audits conducted" if result["compliance_audits"] else "None")
    print("Incident Response Plans:", f"{len(result['incident_response_plans'])} plans created" if result["incident_response_plans"] else "None")
    print("Compliance Reports:", f"{len(result['compliance_reports'])} reports generated" if result["compliance_reports"] else "None")
    print("Regulatory Updates:", f"{len(result['regulatory_updates'])} updates identified" if result["regulatory_updates"] else "None")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_compliance_agent())
