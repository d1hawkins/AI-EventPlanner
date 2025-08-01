import asyncio
import json
from datetime import datetime

from app.graphs.stakeholder_management_graph import create_stakeholder_management_graph, create_initial_state
from app.tools.stakeholder_tools import (
    SpeakerManagementTool,
    SponsorManagementTool,
    VolunteerManagementTool,
    VIPManagementTool,
    StakeholderPlanGenerationTool
)
from app.config import OPENAI_API_KEY, LLM_MODEL


async def test_stakeholder_agent():
    """
    Test the Stakeholder Management Agent's functionality.
    """
    # Check if OpenAI API key is set
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    print(f"Using LLM model: {LLM_MODEL}")
    
    # Create the stakeholder management graph
    print("Initializing Stakeholder Management Agent...")
    stakeholder_graph = create_stakeholder_management_graph()
    
    # Create initial state with some predefined event details
    state = create_initial_state()
    
    # Add initial system message
    state["messages"].append({
        "role": "system",
        "content": "The conversation has started. The Stakeholder Management Agent will help manage stakeholders for your event.",
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
    
    # Test 1: Speaker Management
    print("\n=== Test 1: Speaker Management ===")
    
    # Add a user message to trigger speaker management
    state["messages"].append({
        "role": "user",
        "content": "I need help managing speakers for our Tech Innovation Summit. We need to find speakers for AI, blockchain, and sustainable tech topics."
    })
    
    # Run the stakeholder management graph to manage speakers
    result = stakeholder_graph.invoke(state, {"override_next": "manage_speakers"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nStakeholder Management Agent (Speaker Management):", assistant_messages[-1]["content"])
    
    # Test 2: Sponsor Management
    print("\n=== Test 2: Sponsor Management ===")
    
    # Add a user message to trigger sponsor management
    result["messages"].append({
        "role": "user",
        "content": "We need to find sponsors for our event. We're looking for tech companies that would be interested in sponsoring a tech innovation conference."
    })
    
    # Run the stakeholder management graph to manage sponsors
    result = stakeholder_graph.invoke(result, {"override_next": "manage_sponsors"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nStakeholder Management Agent (Sponsor Management):", assistant_messages[-1]["content"])
    
    # Test 3: Volunteer Management
    print("\n=== Test 3: Volunteer Management ===")
    
    # Add a user message to trigger volunteer management
    result["messages"].append({
        "role": "user",
        "content": "We need to recruit and manage volunteers for our event. We need people for registration, technical support, and hospitality roles."
    })
    
    # Run the stakeholder management graph to manage volunteers
    result = stakeholder_graph.invoke(result, {"override_next": "manage_volunteers"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nStakeholder Management Agent (Volunteer Management):", assistant_messages[-1]["content"])
    
    # Test 4: VIP Management
    print("\n=== Test 4: VIP Management ===")
    
    # Add a user message to trigger VIP management
    result["messages"].append({
        "role": "user",
        "content": "We need to identify and manage VIP attendees for our event. We want to invite tech industry leaders and provide them with special accommodations."
    })
    
    # Run the stakeholder management graph to manage VIPs
    result = stakeholder_graph.invoke(result, {"override_next": "manage_vips"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nStakeholder Management Agent (VIP Management):", assistant_messages[-1]["content"])
    
    # Test 5: Stakeholder Plan Generation
    print("\n=== Test 5: Stakeholder Plan Generation ===")
    
    # Add a user message to trigger stakeholder plan generation
    result["messages"].append({
        "role": "user",
        "content": "Can you create a comprehensive stakeholder management plan for the entire event?"
    })
    
    # Run the stakeholder management graph to generate a stakeholder plan
    result = stakeholder_graph.invoke(result, {"override_next": "generate_stakeholder_plan"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nStakeholder Management Agent (Stakeholder Plan):", assistant_messages[-1]["content"])
    
    # Print the final state for debugging
    print("\n=== Final State ===")
    print("Speakers:", f"{len(result['speakers'])} speakers managed" if result["speakers"] else "None")
    print("Sponsors:", f"{len(result['sponsors'])} sponsors managed" if result["sponsors"] else "None")
    print("Volunteers:", f"{len(result['volunteers'])} volunteers managed" if result["volunteers"] else "None")
    print("VIPs:", f"{len(result['vips'])} VIPs managed" if result["vips"] else "None")
    print("Stakeholder Plan:", "Created" if result["stakeholder_plan"] else "None")
    
    # Test individual tools directly
    print("\n=== Testing Individual Tools ===")
    
    # Test SpeakerManagementTool
    print("\nTesting SpeakerManagementTool:")
    speaker_tool = SpeakerManagementTool()
    speaker_result = speaker_tool._run(
        name="Dr. Sarah Chen",
        role="AI Research Director",
        topic="The Future of AI in Event Planning",
        bio="Leading AI researcher with 15+ years of experience",
        contact_info="sarah.chen@example.com",
        requirements=["High-speed internet", "Presentation display adapter"],
        confirmed=True
    )
    print(f"Speaker added: {speaker_result['speaker']['name']} ({speaker_result['speaker']['role']})")
    print(f"Topic: {speaker_result['speaker']['topic']}")
    print(f"Status: {speaker_result['management_details']['status']}")
    
    # Test SponsorManagementTool
    print("\nTesting SponsorManagementTool:")
    sponsor_tool = SponsorManagementTool()
    sponsor_result = sponsor_tool._run(
        name="TechCorp",
        level="Gold",
        contribution=25000.0,
        benefits=["Logo on main stage", "Booth in prime location", "5 free tickets", "Speaking opportunity"],
        contact_person="Maria Garcia",
        contact_info="maria.garcia@techcorp.com",
        confirmed=True
    )
    print(f"Sponsor added: {sponsor_result['sponsor']['name']} ({sponsor_result['sponsor']['level']})")
    print(f"Contribution: ${sponsor_result['sponsor']['contribution']:.2f}")
    print(f"Status: {sponsor_result['management_details']['status']}")
    
    # Test VolunteerManagementTool
    print("\nTesting VolunteerManagementTool:")
    volunteer_tool = VolunteerManagementTool()
    volunteer_result = volunteer_tool._run(
        name="Alex Johnson",
        role="Technical Support",
        skills=["AV equipment", "Troubleshooting", "Technical knowledge"],
        availability=["Full event", "Setup", "Teardown"],
        contact_info="alex.johnson@example.com",
        assigned_tasks=["Set up equipment", "Assist speakers", "Troubleshoot issues"],
        confirmed=True
    )
    print(f"Volunteer added: {volunteer_result['volunteer']['name']} ({volunteer_result['volunteer']['role']})")
    print(f"Skills: {', '.join(volunteer_result['volunteer']['skills'])}")
    print(f"Status: {volunteer_result['management_details']['status']}")
    
    # Test VIPManagementTool
    print("\nTesting VIPManagementTool:")
    vip_tool = VIPManagementTool()
    vip_result = vip_tool._run(
        name="Jonathan Reynolds",
        organization="Venture Capital Partners",
        role="Managing Partner",
        contact_info="jreynolds@vcpartners.com",
        special_requirements=["VIP lounge access", "Reserved parking"],
        confirmed=True
    )
    print(f"VIP added: {vip_result['vip']['name']} ({vip_result['vip']['organization']}, {vip_result['vip']['role']})")
    print(f"Requirements: {', '.join(vip_result['vip']['special_requirements'])}")
    print(f"Status: {vip_result['management_details']['status']}")
    
    # Test StakeholderPlanGenerationTool
    print("\nTesting StakeholderPlanGenerationTool:")
    plan_tool = StakeholderPlanGenerationTool()
    plan_result = plan_tool._run(
        event_id="test-event-123",
        event_details=state["event_details"],
        speakers=[speaker_result["speaker"]],
        sponsors=[sponsor_result["sponsor"]],
        volunteers=[volunteer_result["volunteer"]],
        vips=[vip_result["vip"]]
    )
    print(f"Stakeholder plan generated with {len(plan_result['stakeholder_plan']['communication_schedule'])} communication milestones")
    print(f"Speakers: {len(plan_result['stakeholder_plan']['speakers'])}")
    print(f"Sponsors: {len(plan_result['stakeholder_plan']['sponsors'])}")
    print(f"Volunteers: {len(plan_result['stakeholder_plan']['volunteers'])}")
    print(f"VIPs: {len(plan_result['stakeholder_plan']['vips'])}")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_stakeholder_agent())
