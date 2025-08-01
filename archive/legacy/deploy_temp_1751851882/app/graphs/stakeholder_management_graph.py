from typing import Dict, List, Any, TypedDict, Literal, Optional
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.utils.llm_factory import get_llm
from app.tools.stakeholder_tools import (
    SpeakerManagementTool,
    SponsorManagementTool,
    VolunteerManagementTool,
    VIPManagementTool,
    StakeholderPlanGenerationTool
)
from app.tools.event_tools import RequirementsTool, MonitoringTool, ReportingTool
from app.tools.stakeholder_search_tool import StakeholderSearchTool


# Define the state schema for the Stakeholder Management Agent
class StakeholderManagementStateDict(TypedDict):
    """State for the stakeholder management agent."""
    
    messages: List[Dict[str, str]]
    event_details: Dict[str, Any]
    speakers: List[Dict[str, Any]]
    sponsors: List[Dict[str, Any]]
    volunteers: List[Dict[str, Any]]
    vips: List[Dict[str, Any]]
    current_phase: str
    next_steps: List[str]
    stakeholder_plan: Optional[Dict[str, Any]]


# Define the system prompt for the Stakeholder Management Agent
STAKEHOLDER_MANAGEMENT_SYSTEM_PROMPT = """You are the Stakeholder Management Agent for an event planning system. Your role is to:

1. Coordinate with speakers, sponsors, volunteers, and VIPs
2. Manage stakeholder relationships and communications
3. Create engagement strategies for different stakeholder groups
4. Ensure stakeholder needs and requirements are met
5. Develop comprehensive stakeholder management plans

Your primary responsibilities include:

Speaker Management:
- Speaker identification and recruitment
- Topic coordination
- Speaker requirements management
- Schedule optimization

Sponsor Management:
- Sponsor acquisition and relationship management
- Sponsorship package development
- Benefit fulfillment
- ROI tracking

Volunteer Management:
- Role definition and assignment
- Volunteer recruitment
- Training coordination
- Schedule management

VIP Management:
- VIP identification and invitation
- Special requirements handling
- VIP experience enhancement
- Relationship maintenance

Your current state:
Current phase: {current_phase}
Event details: {event_details}
Speakers: {speakers}
Sponsors: {sponsors}
Volunteers: {volunteers}
VIPs: {vips}
Next steps: {next_steps}

Follow these guidelines:
1. Analyze the event requirements to understand stakeholder needs
2. Identify and recruit appropriate speakers, sponsors, and volunteers
3. Develop engagement strategies for each stakeholder group
4. Create communication schedules and templates
5. Ensure all stakeholder requirements are documented and addressed
6. Generate comprehensive stakeholder management plans

Respond to the coordinator agent or user in a helpful, professional manner. Ask clarifying questions when needed to gather complete stakeholder requirements.
"""


def create_stakeholder_management_graph():
    """
    Create the stakeholder management agent graph.
    
    Returns:
        Compiled LangGraph for the stakeholder management agent
    """
    # Initialize the LLM
    llm = get_llm(temperature=0.2)
    
    # Initialize tools
    tools = [
        SpeakerManagementTool(),
        SponsorManagementTool(),
        VolunteerManagementTool(),
        VIPManagementTool(),
        StakeholderPlanGenerationTool(),
        RequirementsTool(),
        MonitoringTool(),
        ReportingTool(),
        StakeholderSearchTool()
    ]
    
    # Create the tool node
    tool_node = ToolNode(tools)
    
    # Define the nodes
    def analyze_stakeholders(state: StakeholderManagementStateDict) -> StakeholderManagementStateDict:
        """
        Analyze event requirements to determine stakeholder needs.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Get the last message
        last_message = state["messages"][-1]["content"] if state["messages"] else ""
        
        # Create a prompt for the LLM to analyze stakeholder requirements
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps analyze event stakeholder requirements.
Based on the event details and conversation, extract key information about:
1. Speaker requirements (types of speakers, topics, etc.)
2. Sponsor requirements (sponsorship levels, benefits, etc.)
3. Volunteer requirements (roles, skills, etc.)
4. VIP requirements (special accommodations, etc.)

Provide a structured analysis of the stakeholder requirements for this event."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}

Analyze these event details and the conversation to determine the stakeholder requirements for this event. Focus on speaker, sponsor, volunteer, and VIP needs.""")
        ])
        
        # Analyze requirements using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Add the analysis to messages
        state["messages"].append({
            "role": "assistant",
            "content": result.content
        })
        
        # Update phase and next steps
        state["current_phase"] = "stakeholder_analysis"
        state["next_steps"] = ["manage_speakers", "manage_sponsors", "manage_volunteers", "manage_vips"]
        
        return state
    
    def manage_speakers(state: StakeholderManagementStateDict) -> StakeholderManagementStateDict:
        """
        Manage speakers for the event.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with speaker information
        """
        # Create a prompt for the LLM to determine speaker needs
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps identify speaker needs for events.
Based on the event details and conversation, determine:
1. What types of speakers are needed
2. Potential speaker topics
3. Speaker requirements
4. Presentation schedule considerations

Provide specific recommendations for speakers that would be appropriate for this event."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Current speakers: {state['speakers']}

Identify speaker needs for this event and recommend specific speakers with topics. If speakers are already identified, suggest improvements or additions.""")
        ])
        
        # Determine speaker needs using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the SpeakerManagementTool to add speakers
        speaker_management_tool = SpeakerManagementTool()
        
        # If no speakers exist yet, create some based on the event type
        if not state["speakers"]:
            event_type = state["event_details"].get("event_type", "").lower()
            
            if "conference" in event_type or "tech" in event_type:
                # Add tech conference speakers
                speakers = [
                    {
                        "name": "Dr. Sarah Chen",
                        "role": "AI Research Director",
                        "topic": "The Future of AI in Event Planning",
                        "bio": "Leading AI researcher with 15+ years of experience",
                        "contact_info": "sarah.chen@example.com",
                        "requirements": ["High-speed internet", "Presentation display adapter"],
                        "confirmed": True
                    },
                    {
                        "name": "Michael Rodriguez",
                        "role": "CTO, TechVentures",
                        "topic": "Emerging Technologies in 2025",
                        "bio": "Technology executive and frequent keynote speaker",
                        "contact_info": "michael.r@techventures.com",
                        "requirements": ["Wireless microphone", "Demo table"],
                        "confirmed": False
                    },
                    {
                        "name": "Dr. Aisha Johnson",
                        "role": "Professor of Computer Science",
                        "topic": "Ethical Considerations in Technology",
                        "bio": "Award-winning researcher and author",
                        "contact_info": "ajohnson@university.edu",
                        "requirements": ["Podium", "Water"],
                        "confirmed": False
                    }
                ]
            elif "wedding" in event_type or "social" in event_type:
                # Add wedding/social event speakers
                speakers = [
                    {
                        "name": "James Wilson",
                        "role": "Best Man",
                        "topic": "Toast to the Couple",
                        "bio": "Childhood friend of the groom",
                        "contact_info": "james.wilson@example.com",
                        "requirements": ["Wireless microphone"],
                        "confirmed": True
                    },
                    {
                        "name": "Emma Thompson",
                        "role": "Maid of Honor",
                        "topic": "Celebratory Speech",
                        "bio": "Sister of the bride",
                        "contact_info": "emma.t@example.com",
                        "requirements": ["Wireless microphone"],
                        "confirmed": True
                    }
                ]
            elif "corporate" in event_type or "business" in event_type:
                # Add corporate event speakers
                speakers = [
                    {
                        "name": "Jennifer Martinez",
                        "role": "CEO",
                        "topic": "Company Vision and Strategy",
                        "bio": "Company founder with 20+ years of industry experience",
                        "contact_info": "jmartinez@company.com",
                        "requirements": ["Teleprompter", "Wireless microphone"],
                        "confirmed": True
                    },
                    {
                        "name": "Robert Chang",
                        "role": "VP of Sales",
                        "topic": "Annual Sales Performance",
                        "bio": "Sales leader with record-breaking results",
                        "contact_info": "rchang@company.com",
                        "requirements": ["Presentation clicker", "Dual screens"],
                        "confirmed": True
                    },
                    {
                        "name": "Lisa Johnson",
                        "role": "Industry Expert",
                        "topic": "Market Trends and Opportunities",
                        "bio": "Renowned industry analyst and consultant",
                        "contact_info": "lisa.johnson@consultancy.com",
                        "requirements": ["Wireless microphone", "Whiteboard"],
                        "confirmed": False
                    }
                ]
            else:
                # Generic speakers for other event types
                speakers = [
                    {
                        "name": "Alex Rivera",
                        "role": "Keynote Speaker",
                        "topic": "Main Presentation",
                        "bio": "Expert in the field with 10+ years of experience",
                        "contact_info": "alex.rivera@example.com",
                        "requirements": ["Wireless microphone", "Presentation system"],
                        "confirmed": False
                    },
                    {
                        "name": "Jordan Smith",
                        "role": "Guest Speaker",
                        "topic": "Special Topic Presentation",
                        "bio": "Specialist with unique insights",
                        "contact_info": "jordan.smith@example.com",
                        "requirements": ["Podium", "Water"],
                        "confirmed": False
                    }
                ]
            
            # Add speakers to state
            for speaker_data in speakers:
                speaker_result = speaker_management_tool._run(
                    name=speaker_data["name"],
                    role=speaker_data["role"],
                    topic=speaker_data["topic"],
                    bio=speaker_data["bio"],
                    contact_info=speaker_data["contact_info"],
                    requirements=speaker_data["requirements"],
                    confirmed=speaker_data["confirmed"]
                )
                
                state["speakers"].append(speaker_result["speaker"])
        
        # Add speaker management to messages
        speaker_summary = "Current Speakers:\n"
        for speaker in state["speakers"]:
            status = "Confirmed" if speaker.get("confirmed", False) else "Pending"
            speaker_summary += f"- {speaker['name']} ({speaker['role']}): {speaker['topic']} - {status}\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"{result.content}\n\n{speaker_summary}\n\nI've identified and managed the speakers for this event. Would you like to add more speakers or modify the existing ones?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "speaker_management"
        state["next_steps"] = ["manage_sponsors", "manage_volunteers", "manage_vips", "generate_stakeholder_plan"]
        
        return state
    
    def manage_sponsors(state: StakeholderManagementStateDict) -> StakeholderManagementStateDict:
        """
        Manage sponsors for the event.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with sponsor information
        """
        # Create a prompt for the LLM to determine sponsor needs
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps identify sponsor needs for events.
Based on the event details and conversation, determine:
1. What types of sponsors are needed
2. Appropriate sponsorship levels
3. Benefits to offer sponsors
4. Sponsor acquisition strategy

Provide specific recommendations for sponsors that would be appropriate for this event."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Current sponsors: {state['sponsors']}

Identify sponsor needs for this event and recommend specific sponsors. If sponsors are already identified, suggest improvements or additions.""")
        ])
        
        # Determine sponsor needs using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the SponsorManagementTool to add sponsors
        sponsor_management_tool = SponsorManagementTool()
        
        # If no sponsors exist yet, create some based on the event type
        if not state["sponsors"]:
            event_type = state["event_details"].get("event_type", "").lower()
            
            if "conference" in event_type or "tech" in event_type:
                # Add tech conference sponsors
                sponsors = [
                    {
                        "name": "TechCorp",
                        "level": "Gold",
                        "contribution": 25000.0,
                        "benefits": ["Logo on main stage", "Booth in prime location", "5 free tickets", "Speaking opportunity"],
                        "contact_person": "Maria Garcia",
                        "contact_info": "maria.garcia@techcorp.com",
                        "confirmed": True
                    },
                    {
                        "name": "InnovateSoft",
                        "level": "Silver",
                        "contribution": 15000.0,
                        "benefits": ["Logo on website", "Booth", "3 free tickets"],
                        "contact_person": "David Kim",
                        "contact_info": "david.kim@innovatesoft.com",
                        "confirmed": True
                    },
                    {
                        "name": "DataSystems",
                        "level": "Bronze",
                        "contribution": 5000.0,
                        "benefits": ["Logo on website", "1 free ticket"],
                        "contact_person": "Sarah Johnson",
                        "contact_info": "sjohnson@datasystems.com",
                        "confirmed": False
                    }
                ]
            elif "wedding" in event_type or "social" in event_type:
                # Add wedding/social event sponsors (family members)
                sponsors = [
                    {
                        "name": "Johnson Family",
                        "level": "Primary",
                        "contribution": 10000.0,
                        "benefits": ["Special acknowledgment", "Reserved seating"],
                        "contact_person": "Robert Johnson",
                        "contact_info": "rjohnson@example.com",
                        "confirmed": True
                    },
                    {
                        "name": "Smith Family",
                        "level": "Secondary",
                        "contribution": 5000.0,
                        "benefits": ["Acknowledgment in program", "Reserved seating"],
                        "contact_person": "Mary Smith",
                        "contact_info": "msmith@example.com",
                        "confirmed": True
                    }
                ]
            elif "corporate" in event_type or "business" in event_type:
                # Add corporate event sponsors
                sponsors = [
                    {
                        "name": "Global Partners Inc.",
                        "level": "Platinum",
                        "contribution": 50000.0,
                        "benefits": ["Co-branding on all materials", "VIP access", "Speaking opportunity", "10 free tickets"],
                        "contact_person": "Thomas Wright",
                        "contact_info": "twright@globalpartners.com",
                        "confirmed": True
                    },
                    {
                        "name": "Regional Suppliers Co.",
                        "level": "Gold",
                        "contribution": 25000.0,
                        "benefits": ["Logo on main materials", "VIP access", "5 free tickets"],
                        "contact_person": "Jessica Lee",
                        "contact_info": "jlee@regionalsuppliers.com",
                        "confirmed": False
                    }
                ]
            else:
                # Generic sponsors for other event types
                sponsors = [
                    {
                        "name": "Main Sponsor",
                        "level": "Gold",
                        "contribution": 10000.0,
                        "benefits": ["Logo on all materials", "Booth", "5 free tickets"],
                        "contact_person": "Contact Person",
                        "contact_info": "contact@mainsponsor.com",
                        "confirmed": False
                    },
                    {
                        "name": "Supporting Sponsor",
                        "level": "Silver",
                        "contribution": 5000.0,
                        "benefits": ["Logo on website", "3 free tickets"],
                        "contact_person": "Contact Person",
                        "contact_info": "contact@supportingsponsor.com",
                        "confirmed": False
                    }
                ]
            
            # Add sponsors to state
            for sponsor_data in sponsors:
                sponsor_result = sponsor_management_tool._run(
                    name=sponsor_data["name"],
                    level=sponsor_data["level"],
                    contribution=sponsor_data["contribution"],
                    benefits=sponsor_data["benefits"],
                    contact_person=sponsor_data["contact_person"],
                    contact_info=sponsor_data["contact_info"],
                    confirmed=sponsor_data["confirmed"]
                )
                
                state["sponsors"].append(sponsor_result["sponsor"])
        
        # Add sponsor management to messages
        sponsor_summary = "Current Sponsors:\n"
        for sponsor in state["sponsors"]:
            status = "Confirmed" if sponsor.get("confirmed", False) else "Pending"
            sponsor_summary += f"- {sponsor['name']} ({sponsor['level']}): ${sponsor['contribution']:.2f} - {status}\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"{result.content}\n\n{sponsor_summary}\n\nI've identified and managed the sponsors for this event. Would you like to add more sponsors or modify the existing ones?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "sponsor_management"
        state["next_steps"] = ["manage_volunteers", "manage_vips", "generate_stakeholder_plan"]
        
        return state
    
    def manage_volunteers(state: StakeholderManagementStateDict) -> StakeholderManagementStateDict:
        """
        Manage volunteers for the event.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with volunteer information
        """
        # Create a prompt for the LLM to determine volunteer needs
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps identify volunteer needs for events.
Based on the event details and conversation, determine:
1. What volunteer roles are needed
2. How many volunteers are required for each role
3. Skills required for each role
4. Volunteer recruitment and management strategy

Provide specific recommendations for volunteer roles and requirements."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Current volunteers: {state['volunteers']}

Identify volunteer needs for this event and recommend specific roles. If volunteers are already identified, suggest improvements or additions.""")
        ])
        
        # Determine volunteer needs using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the VolunteerManagementTool to add volunteers
        volunteer_management_tool = VolunteerManagementTool()
        
        # If no volunteers exist yet, create some based on the event type and size
        if not state["volunteers"]:
            event_type = state["event_details"].get("event_type", "").lower()
            attendee_count = state["event_details"].get("attendee_count", 100)
            
            # Scale number of volunteers based on attendee count
            num_volunteers = max(3, attendee_count // 50)
            
            volunteers = []
            
            # Registration volunteers
            for i in range(max(1, num_volunteers // 3)):
                volunteers.append({
                    "name": f"Registration Volunteer {i+1}",
                    "role": "Registration",
                    "skills": ["Organization", "Customer service", "Attention to detail"],
                    "availability": ["Full event", "Setup"],
                    "contact_info": f"registration{i+1}@example.com",
                    "assigned_tasks": ["Check in attendees", "Distribute materials", "Answer questions"],
                    "confirmed": i == 0  # First volunteer confirmed, others pending
                })
            
            # Technical support volunteers
            for i in range(max(1, num_volunteers // 3)):
                volunteers.append({
                    "name": f"Tech Support Volunteer {i+1}",
                    "role": "Technical Support",
                    "skills": ["AV equipment", "Troubleshooting", "Technical knowledge"],
                    "availability": ["Full event", "Setup", "Teardown"],
                    "contact_info": f"techsupport{i+1}@example.com",
                    "assigned_tasks": ["Set up equipment", "Assist speakers", "Troubleshoot issues"],
                    "confirmed": i == 0  # First volunteer confirmed, others pending
                })
            
            # Hospitality volunteers
            for i in range(max(1, num_volunteers // 3)):
                volunteers.append({
                    "name": f"Hospitality Volunteer {i+1}",
                    "role": "Hospitality",
                    "skills": ["Customer service", "Communication", "Problem-solving"],
                    "availability": ["Full event"],
                    "contact_info": f"hospitality{i+1}@example.com",
                    "assigned_tasks": ["Greet attendees", "Direct to sessions", "Assist with refreshments"],
                    "confirmed": i == 0  # First volunteer confirmed, others pending
                })
            
            # Add volunteers to state
            for volunteer_data in volunteers:
                volunteer_result = volunteer_management_tool._run(
                    name=volunteer_data["name"],
                    role=volunteer_data["role"],
                    skills=volunteer_data["skills"],
                    availability=volunteer_data["availability"],
                    contact_info=volunteer_data["contact_info"],
                    assigned_tasks=volunteer_data["assigned_tasks"],
                    confirmed=volunteer_data["confirmed"]
                )
                
                state["volunteers"].append(volunteer_result["volunteer"])
        
        # Add volunteer management to messages
        volunteer_summary = "Current Volunteers:\n"
        for volunteer in state["volunteers"]:
            status = "Confirmed" if volunteer.get("confirmed", False) else "Pending"
            volunteer_summary += f"- {volunteer['name']} ({volunteer['role']}): {status}\n"
            if volunteer.get("assigned_tasks"):
                volunteer_summary += f"  Tasks: {', '.join(volunteer['assigned_tasks'])}\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"{result.content}\n\n{volunteer_summary}\n\nI've identified and managed the volunteers for this event. Would you like to add more volunteers or modify the existing ones?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "volunteer_management"
        state["next_steps"] = ["manage_vips", "generate_stakeholder_plan"]
        
        return state
    
    def manage_vips(state: StakeholderManagementStateDict) -> StakeholderManagementStateDict:
        """
        Manage VIP attendees for the event.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with VIP information
        """
        # Create a prompt for the LLM to determine VIP needs
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps identify VIP needs for events.
Based on the event details and conversation, determine:
1. Who should be considered VIPs for this event
2. Special accommodations needed for VIPs
3. VIP experience enhancement strategies
4. VIP relationship management approach

Provide specific recommendations for VIP management."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Current VIPs: {state['vips']}

Identify VIP needs for this event and recommend specific VIPs to invite. If VIPs are already identified, suggest improvements or additions.""")
        ])
        
        # Determine VIP needs using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the VIPManagementTool to add VIPs
        vip_management_tool = VIPManagementTool()
        
        # If no VIPs exist yet, create some based on the event type
        if not state["vips"]:
            event_type = state["event_details"].get("event_type", "").lower()
            
            if "conference" in event_type or "tech" in event_type:
                # Add tech conference VIPs
                vips = [
                    {
                        "name": "Dr. Elizabeth Chen",
                        "organization": "Tech Innovation Institute",
                        "role": "Director of Research",
                        "special_requirements": ["Reserved seating", "Private meeting room", "Airport pickup"],
                        "contact_info": "echen@techinnovation.org",
                        "confirmed": True
                    },
                    {
                        "name": "Jonathan Reynolds",
                        "organization": "Venture Capital Partners",
                        "role": "Managing Partner",
                        "special_requirements": ["VIP lounge access", "Reserved parking"],
                        "contact_info": "jreynolds@vcpartners.com",
                        "confirmed": False
                    }
                ]
            elif "wedding" in event_type or "social" in event_type:
                # Add wedding/social event VIPs
                vips = [
                    {
                        "name": "Grandparents of the Bride",
                        "organization": "Family",
                        "role": "Honored Guests",
                        "special_requirements": ["Accessible seating", "Special dietary needs", "Early arrival"],
                        "contact_info": "family@example.com",
                        "confirmed": True
                    },
                    {
                        "name": "Distinguished Family Friend",
                        "organization": "Family Connection",
                        "role": "Special Guest",
                        "special_requirements": ["Reserved seating", "Transportation assistance"],
                        "contact_info": "friend@example.com",
                        "confirmed": True
                    }
                ]
            elif "corporate" in event_type or "business" in event_type:
                # Add corporate event VIPs
                vips = [
                    {
                        "name": "Richard Thompson",
                        "organization": "Parent Company",
                        "role": "CEO",
                        "special_requirements": ["Private meeting room", "Security detail", "Special dietary needs"],
                        "contact_info": "rthompson@parentcompany.com",
                        "confirmed": True
                    },
                    {
                        "name": "Board Members",
                        "organization": "Company Board",
                        "role": "Board of Directors",
                        "special_requirements": ["Reserved seating", "Private reception", "Detailed briefing materials"],
                        "contact_info": "board@company.com",
                        "confirmed": True
                    }
                ]
            else:
                # Generic VIPs for other event types
                vips = [
                    {
                        "name": "Primary VIP",
                        "organization": "Key Organization",
                        "role": "Distinguished Guest",
                        "special_requirements": ["Reserved seating", "VIP reception"],
                        "contact_info": "vip@example.com",
                        "confirmed": False
                    },
                    {
                        "name": "Secondary VIP",
                        "organization": "Partner Organization",
                        "role": "Special Guest",
                        "special_requirements": ["Reserved seating"],
                        "contact_info": "vip2@example.com",
                        "confirmed": False
                    }
                ]
            
            # Add VIPs to state
            for vip_data in vips:
                vip_result = vip_management_tool._run(
                    name=vip_data["name"],
                    organization=vip_data["organization"],
                    role=vip_data["role"],
                    contact_info=vip_data["contact_info"],
                    special_requirements=vip_data["special_requirements"],
                    confirmed=vip_data["confirmed"]
                )
                
                state["vips"].append(vip_result["vip"])
        
        # Add VIP management to messages
        vip_summary = "Current VIPs:\n"
        for vip in state["vips"]:
            status = "Confirmed" if vip.get("confirmed", False) else "Pending"
            vip_summary += f"- {vip['name']} ({vip['organization']}, {vip['role']}): {status}\n"
            if vip.get("special_requirements"):
                vip_summary += f"  Requirements: {', '.join(vip['special_requirements'])}\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"{result.content}\n\n{vip_summary}\n\nI've identified and managed the VIPs for this event. Would you like to add more VIPs or modify the existing ones?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "vip_management"
        state["next_steps"] = ["generate_stakeholder_plan"]
        
        return state
    
    def generate_stakeholder_plan(state: StakeholderManagementStateDict) -> StakeholderManagementStateDict:
        """
        Generate a comprehensive stakeholder management plan.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with stakeholder plan
        """
        # Use the StakeholderPlanGenerationTool to generate a plan
        stakeholder_plan_tool = StakeholderPlanGenerationTool()
        
        # Generate a unique event ID
        import uuid
        event_id = str(uuid.uuid4())
        
        # Generate the stakeholder plan
        plan_result = stakeholder_plan_tool._run(
            event_id=event_id,
            event_details=state["event_details"],
            speakers=state["speakers"],
            sponsors=state["sponsors"],
            volunteers=state["volunteers"],
            vips=state["vips"]
        )
        
        # Update state with stakeholder plan
        state["stakeholder_plan"] = plan_result.get("stakeholder_plan", {})
        
        # Add the stakeholder plan to messages
        state["messages"].append({
            "role": "assistant",
            "content": f"I've generated a comprehensive stakeholder management plan for this event:\n\n{plan_result['summary']}\n\nThis plan includes speaker management, sponsor engagement, volunteer coordination, and VIP handling strategies. Would you like to make any adjustments to this plan?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "plan_generation"
        state["next_steps"] = ["finalize_plan"]
        
        return state
    
    def generate_response(state: StakeholderManagementStateDict) -> StakeholderManagementStateDict:
        """
        Generate a response to the user or coordinator agent.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create the stakeholder management prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=STAKEHOLDER_MANAGEMENT_SYSTEM_PROMPT.format(
                current_phase=state["current_phase"],
                event_details=state["event_details"],
                speakers=state["speakers"],
                sponsors=state["sponsors"],
                volunteers=state["volunteers"],
                vips=state["vips"],
                next_steps=state["next_steps"]
            )),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Generate response using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Add the response to messages
        new_message = {
            "role": "assistant",
            "content": result.content
        }
        state["messages"].append(new_message)
        
        return state
    
    # Create the graph
    workflow = StateGraph(StakeholderManagementStateDict)
    
    # Add nodes
    workflow.add_node("analyze_stakeholders", analyze_stakeholders)
    workflow.add_node("manage_speakers", manage_speakers)
    workflow.add_node("manage_sponsors", manage_sponsors)
    workflow.add_node("manage_volunteers", manage_volunteers)
    workflow.add_node("manage_vips", manage_vips)
    workflow.add_node("generate_stakeholder_plan", generate_stakeholder_plan)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("tools", tool_node)
    
    # Add edges
    workflow.add_edge("analyze_stakeholders", "manage_speakers")
    workflow.add_edge("manage_speakers", "manage_sponsors")
    workflow.add_edge("manage_sponsors", "manage_volunteers")
    workflow.add_edge("manage_volunteers", "manage_vips")
    workflow.add_edge("manage_vips", "generate_stakeholder_plan")
    workflow.add_edge("generate_stakeholder_plan", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Set the entry point
    workflow.set_entry_point("analyze_stakeholders")
    
    return workflow.compile()


def create_initial_state() -> StakeholderManagementStateDict:
    """
    Create the initial state for the stakeholder management agent.
    
    Returns:
        Initial state dictionary
    """
    return {
        "messages": [],
        "event_details": {
            "event_type": None,
            "title": None,
            "description": None,
            "attendee_count": None,
            "scale": None,
            "timeline_start": None,
            "timeline_end": None,
            "budget": None,
            "location": None
        },
        "speakers": [],
        "sponsors": [],
        "volunteers": [],
        "vips": [],
        "current_phase": "stakeholder_analysis",
        "next_steps": ["analyze_stakeholders"],
        "stakeholder_plan": None
    }
