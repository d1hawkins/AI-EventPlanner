import asyncio
import json
from datetime import datetime

from app.graphs.marketing_communications_graph import create_marketing_communications_graph, create_initial_state
from app.tools.marketing_tools import (
    ChannelManagementTool,
    ContentCreationTool,
    AttendeeManagementTool,
    RegistrationFormCreationTool,
    CampaignCreationTool,
    MarketingPlanGenerationTool,
    CommunicationPlanGenerationTool
)
from app.config import OPENAI_API_KEY, LLM_MODEL


async def test_marketing_agent():
    """
    Test the Marketing & Communications Agent's functionality.
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
    
    # Create initial state with some predefined event details
    state = create_initial_state()
    
    # Add initial system message
    state["messages"].append({
        "role": "system",
        "content": "The conversation has started. The Marketing & Communications Agent will help with marketing strategies, content creation, and communication plans for the event.",
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
    
    # Test 1: Channel Management
    print("\n=== Test 1: Channel Management ===")
    
    # Add a user message to trigger channel management
    state["messages"].append({
        "role": "user",
        "content": "I need to set up a social media channel for our Tech Innovation Summit. It should target tech professionals and industry leaders."
    })
    
    # Run the marketing communications graph to manage channels
    result = marketing_graph.invoke(state, {"override_next": "manage_channels"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nMarketing & Communications Agent (Channel Management):", assistant_messages[-1]["content"])
    
    # Test 2: Content Creation
    print("\n=== Test 2: Content Creation ===")
    
    # Add a user message to trigger content creation
    result["messages"].append({
        "role": "user",
        "content": "Create a social media post announcing our Tech Innovation Summit. It should highlight the key speakers and technologies that will be featured."
    })
    
    # Run the marketing communications graph to create content
    result = marketing_graph.invoke(result, {"override_next": "create_content"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nMarketing & Communications Agent (Content Creation):", assistant_messages[-1]["content"])
    
    # Test 3: Attendee Management
    print("\n=== Test 3: Attendee Management ===")
    
    # Add a user message to trigger attendee management
    result["messages"].append({
        "role": "user",
        "content": "Add John Smith as an attendee with email john.smith@example.com. He registered today for a VIP ticket."
    })
    
    # Run the marketing communications graph to manage attendees
    result = marketing_graph.invoke(result, {"override_next": "manage_attendees"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nMarketing & Communications Agent (Attendee Management):", assistant_messages[-1]["content"])
    
    # Test 4: Registration Form Creation
    print("\n=== Test 4: Registration Form Creation ===")
    
    # Add a user message to trigger registration form creation
    result["messages"].append({
        "role": "user",
        "content": "Create a registration form for our event with fields for name, email, company, job title, and dietary restrictions. We'll have Early Bird, Regular, and VIP ticket options."
    })
    
    # Run the marketing communications graph to create a registration form
    result = marketing_graph.invoke(result, {"override_next": "create_registration_form"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nMarketing & Communications Agent (Registration Form Creation):", assistant_messages[-1]["content"])
    
    # Test 5: Campaign Creation
    print("\n=== Test 5: Campaign Creation ===")
    
    # Add a user message to trigger campaign creation
    result["messages"].append({
        "role": "user",
        "content": "Create an early bird registration campaign for our event. It should run for the next 30 days with a budget of $5,000. We want to target tech professionals through email and social media."
    })
    
    # Run the marketing communications graph to create a campaign
    result = marketing_graph.invoke(result, {"override_next": "create_campaign"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nMarketing & Communications Agent (Campaign Creation):", assistant_messages[-1]["content"])
    
    # Test 6: Marketing Plan Generation
    print("\n=== Test 6: Marketing Plan Generation ===")
    
    # Add a user message to trigger marketing plan generation
    result["messages"].append({
        "role": "user",
        "content": "Generate a comprehensive marketing plan for our Tech Innovation Summit. Our objectives are to increase awareness, drive registrations, and establish our event as a premier tech conference."
    })
    
    # Run the marketing communications graph to generate a marketing plan
    result = marketing_graph.invoke(result, {"override_next": "generate_marketing_plan"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nMarketing & Communications Agent (Marketing Plan):", assistant_messages[-1]["content"])
    
    # Test 7: Communication Plan Generation
    print("\n=== Test 7: Communication Plan Generation ===")
    
    # Add a user message to trigger communication plan generation
    result["messages"].append({
        "role": "user",
        "content": "Create a communication plan for our event that addresses attendees, speakers, sponsors, and media. We need to ensure clear and timely communication with all stakeholders."
    })
    
    # Run the marketing communications graph to generate a communication plan
    result = marketing_graph.invoke(result, {"override_next": "generate_communication_plan"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nMarketing & Communications Agent (Communication Plan):", assistant_messages[-1]["content"])
    
    # Print the final state for debugging
    print("\n=== Final State ===")
    print("Channels:", f"{len(result['channels'])} channels managed" if result["channels"] else "None")
    print("Content:", f"{len(result['content'])} content items created" if result["content"] else "None")
    print("Attendees:", f"{len(result['attendees'])} attendees managed" if result["attendees"] else "None")
    print("Registration Forms:", f"{len(result['registration_forms'])} forms created" if result["registration_forms"] else "None")
    print("Campaigns:", f"{len(result['campaigns'])} campaigns created" if result["campaigns"] else "None")
    print("Marketing Plan:", "Created" if result["marketing_plan"] else "None")
    print("Communication Plan:", "Created" if result["communication_plan"] else "None")
    
    # Test individual tools directly
    print("\n=== Testing Individual Tools ===")
    
    # Test ChannelManagementTool
    print("\nTesting ChannelManagementTool:")
    channel_tool = ChannelManagementTool()
    channel_result = channel_tool._run(
        name="LinkedIn",
        type="social media",
        target_audience=["Tech professionals", "Industry leaders", "Potential attendees"],
        cost=1500.0,
        content_requirements=["Professional tone", "Industry insights", "Event highlights"],
        schedule=[
            {"date": "2025-03-15", "content_type": "announcement", "frequency": "one-time"},
            {"date": "2025-04-01", "content_type": "speaker spotlight", "frequency": "weekly"}
        ]
    )
    print(f"Channel created: {channel_result['channel']['name']} ({channel_result['channel']['type']})")
    print(f"Target audience: {', '.join(channel_result['channel']['target_audience'])}")
    print(f"Content requirements: {', '.join(channel_result['channel']['content_requirements'])}")
    
    # Test ContentCreationTool
    print("\nTesting ContentCreationTool:")
    content_tool = ContentCreationTool()
    content_result = content_tool._run(
        title="Tech Summit Announcement",
        type="social post",
        channel="LinkedIn",
        content="Excited to announce the Tech Innovation Summit 2025! Join industry leaders and innovators for three days of cutting-edge discussions, workshops, and networking. Early bird registration now open!",
        target_audience=["Tech professionals", "Industry leaders"],
        publish_date="2025-03-15"
    )
    print(f"Content created: {content_result['content']['title']} ({content_result['content']['type']})")
    print(f"Channel: {content_result['content']['channel']}")
    print(f"Content: {content_result['content']['content'][:50]}...")
    if content_result.get("improvement_suggestions"):
        print(f"Improvement suggestions: {len(content_result['improvement_suggestions'])}")
    
    # Test AttendeeManagementTool
    print("\nTesting AttendeeManagementTool:")
    attendee_tool = AttendeeManagementTool()
    attendee_result = attendee_tool._run(
        name="Jane Doe",
        email="jane.doe@example.com",
        registration_date="2025-03-10",
        ticket_type="Early Bird",
        payment_status="paid",
        special_requirements=["Vegetarian meals", "Accessibility needs"],
        communication_preferences={"marketing": True, "updates": True, "surveys": False}
    )
    print(f"Attendee added: {attendee_result['attendee']['name']} ({attendee_result['attendee']['email']})")
    print(f"Ticket type: {attendee_result['attendee']['ticket_type']}")
    print(f"Payment status: {attendee_result['attendee']['payment_status']}")
    
    # Test RegistrationFormCreationTool
    print("\nTesting RegistrationFormCreationTool:")
    form_tool = RegistrationFormCreationTool()
    form_result = form_tool._run(
        title="Tech Innovation Summit Registration",
        description="Register for the premier tech conference of 2025",
        fields=[
            {"name": "Full Name", "type": "text", "required": True},
            {"name": "Email", "type": "email", "required": True},
            {"name": "Company", "type": "text", "required": True},
            {"name": "Job Title", "type": "text", "required": True},
            {"name": "Dietary Restrictions", "type": "text", "required": False}
        ],
        ticket_types=[
            {"name": "Early Bird", "price": 299.0, "description": "Limited time offer"},
            {"name": "Regular", "price": 499.0, "description": "Standard admission"},
            {"name": "VIP", "price": 999.0, "description": "Premium experience with exclusive access"}
        ],
        payment_methods=["Credit Card", "PayPal", "Invoice"],
        terms_and_conditions="Standard terms and conditions apply.",
        privacy_policy="We respect your privacy and will not share your information with third parties."
    )
    print(f"Registration form created: {form_result['registration_form']['title']}")
    print(f"Fields: {len(form_result['registration_form']['fields'])}")
    print(f"Ticket types: {len(form_result['registration_form']['ticket_types'])}")
    
    # Test CampaignCreationTool
    print("\nTesting CampaignCreationTool:")
    campaign_tool = CampaignCreationTool()
    campaign_result = campaign_tool._run(
        name="Early Bird Registration Campaign",
        description="Campaign to drive early registrations with special pricing",
        objectives=["Drive early registrations", "Generate buzz", "Build email list"],
        target_audience=["Tech professionals", "Previous attendees", "Industry leaders"],
        channels=["Email", "LinkedIn", "Twitter", "Industry newsletters"],
        start_date="2025-03-15",
        end_date="2025-04-15",
        budget=5000.0
    )
    print(f"Campaign created: {campaign_result['campaign']['name']}")
    print(f"Objectives: {', '.join(campaign_result['campaign']['objectives'])}")
    print(f"Channels: {', '.join(campaign_result['campaign']['channels'])}")
    print(f"Budget: ${campaign_result['campaign']['budget']:.2f}")
    
    # Test MarketingPlanGenerationTool
    print("\nTesting MarketingPlanGenerationTool:")
    plan_tool = MarketingPlanGenerationTool()
    plan_result = plan_tool._run(
        event_id="test-event-123",
        event_details=state["event_details"],
        objectives=["Increase awareness", "Drive registrations", "Establish brand presence"],
        target_audience=[
            {"name": "Tech Professionals", "description": "Working professionals in technology fields"},
            {"name": "Industry Leaders", "description": "C-level executives and decision makers"},
            {"name": "Tech Enthusiasts", "description": "Early adopters and technology enthusiasts"}
        ],
        unique_selling_points=["Cutting-edge content", "Networking opportunities", "Industry-leading speakers"],
        key_messages=["Stay ahead of tech trends", "Connect with industry leaders", "Gain actionable insights"],
        budget=75000.0
    )
    print(f"Marketing plan generated with {len(plan_result['marketing_plan']['channels'])} channels")
    print(f"Campaigns: {len(plan_result['marketing_plan']['campaigns'])}")
    print(f"Content calendar items: {len(plan_result['marketing_plan']['content_calendar'])}")
    print(f"Timeline phases: {len(plan_result['marketing_plan']['timeline'])}")
    
    # Test CommunicationPlanGenerationTool
    print("\nTesting CommunicationPlanGenerationTool:")
    comm_plan_tool = CommunicationPlanGenerationTool()
    comm_plan_result = comm_plan_tool._run(
        event_id="test-event-123",
        event_details=state["event_details"],
        stakeholder_groups=[
            {"name": "Attendees", "type": "attendees", "description": "Event attendees"},
            {"name": "Speakers", "type": "speakers", "description": "Event speakers"},
            {"name": "Sponsors", "type": "sponsors", "description": "Event sponsors"},
            {"name": "Media", "type": "media", "description": "Media contacts"}
        ],
        communication_objectives=[
            "Provide timely information",
            "Build excitement",
            "Ensure clear expectations",
            "Facilitate smooth event experience"
        ],
        key_messages={
            "Attendees": ["Event details", "What to expect", "How to prepare"],
            "Speakers": ["Speaking guidelines", "Schedule information", "Technical requirements"],
            "Sponsors": ["Sponsorship benefits", "Branding guidelines", "Setup information"],
            "Media": ["Press release information", "Media access details", "Interview opportunities"]
        }
    )
    print(f"Communication plan generated with {len(comm_plan_result['communication_plan']['stakeholder_groups'])} stakeholder groups")
    print(f"Communication schedule items: {len(comm_plan_result['communication_plan']['schedule'])}")
    print(f"Crisis scenarios: {len(comm_plan_result['communication_plan']['crisis_communication']['crisis_scenarios'])}")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_marketing_agent())
