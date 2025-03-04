from typing import Dict, List, Any, TypedDict, Literal, Optional
from datetime import datetime, timedelta
import uuid

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.utils.llm_factory import get_llm
from app.tools.marketing_tools import (
    ChannelManagementTool,
    ContentCreationTool,
    AttendeeManagementTool,
    RegistrationFormCreationTool,
    CampaignCreationTool,
    MarketingPlanGenerationTool,
    CommunicationPlanGenerationTool
)
from app.schemas.marketing import (
    MarketingChannel,
    MarketingContent,
    Attendee,
    RegistrationForm,
    MarketingCampaign,
    MarketingPlan,
    CommunicationPlan
)


# Define the state schema
class MarketingStateDict(TypedDict):
    """State for the marketing and communications agent."""
    
    messages: List[Dict[str, str]]
    event_details: Dict[str, Any]
    channels: List[Dict[str, Any]]
    content: List[Dict[str, Any]]
    attendees: List[Dict[str, Any]]
    registration_forms: List[Dict[str, Any]]
    campaigns: List[Dict[str, Any]]
    marketing_plan: Optional[Dict[str, Any]]
    communication_plan: Optional[Dict[str, Any]]
    current_task: str


# Define the system prompt
MARKETING_SYSTEM_PROMPT = """You are the Marketing & Communications Agent for an event planning system. Your role is to:

1. Develop comprehensive marketing strategies for events
2. Create and manage marketing content across various channels
3. Design and implement communication plans for different stakeholder groups
4. Manage attendee registrations and communications
5. Track and analyze marketing performance metrics

You have expertise in:
- Digital marketing (social media, email, web)
- Content creation and management
- Attendee engagement and communication
- Registration management
- Marketing analytics and reporting

Your current state:
Event details: {event_details}
Marketing channels: {channels}
Marketing content: {content}
Attendees: {attendees}
Registration forms: {registration_forms}
Marketing campaigns: {campaigns}
Marketing plan: {marketing_plan}
Communication plan: {communication_plan}
Current task: {current_task}

Respond to the user in a helpful, professional manner. Provide strategic marketing advice and practical implementation steps. When creating marketing content, focus on clear messaging, audience targeting, and measurable outcomes.
"""


def create_marketing_communications_graph():
    """
    Create the marketing and communications agent graph.
    
    Returns:
        Compiled LangGraph for the marketing and communications agent
    """
    # Initialize the LLM
    llm = get_llm(temperature=0.2)
    
    # Initialize tools
    tools = [
        ChannelManagementTool(),
        ContentCreationTool(),
        AttendeeManagementTool(),
        RegistrationFormCreationTool(),
        CampaignCreationTool(),
        MarketingPlanGenerationTool(),
        CommunicationPlanGenerationTool()
    ]
    
    # Create the tool node
    tool_node = ToolNode(tools)
    
    # Define the nodes
    def assess_request(state: MarketingStateDict) -> MarketingStateDict:
        """
        Assess the user's request and determine the next action.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with next node to execute
        """
        # Get the last message
        last_message = state["messages"][-1]["content"] if state["messages"] else ""
        
        # Simple keyword-based routing
        if any(keyword in last_message.lower() for keyword in ["channel", "platform", "social media", "email", "website"]):
            state["current_task"] = "manage_channels"
        elif any(keyword in last_message.lower() for keyword in ["content", "post", "message", "write", "create content"]):
            state["current_task"] = "create_content"
        elif any(keyword in last_message.lower() for keyword in ["attendee", "registration", "sign up", "register"]):
            state["current_task"] = "manage_attendees"
        elif any(keyword in last_message.lower() for keyword in ["form", "registration form", "sign up form"]):
            state["current_task"] = "create_registration_form"
        elif any(keyword in last_message.lower() for keyword in ["campaign", "promotion", "advertise"]):
            state["current_task"] = "create_campaign"
        elif any(keyword in last_message.lower() for keyword in ["marketing plan", "strategy", "overall plan"]):
            state["current_task"] = "generate_marketing_plan"
        elif any(keyword in last_message.lower() for keyword in ["communication plan", "stakeholder", "communicate"]):
            state["current_task"] = "generate_communication_plan"
        else:
            # Default to generating a response
            state["current_task"] = "generate_response"
        
        return state
    
    def generate_response(state: MarketingStateDict) -> MarketingStateDict:
        """
        Generate a response to the user.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create the marketing prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=MARKETING_SYSTEM_PROMPT.format(
                event_details=state["event_details"],
                channels=state["channels"],
                content=state["content"],
                attendees=state["attendees"],
                registration_forms=state["registration_forms"],
                campaigns=state["campaigns"],
                marketing_plan=state["marketing_plan"],
                communication_plan=state["communication_plan"],
                current_task=state["current_task"]
            )),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Generate response using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Add the response to messages
        state["messages"].append({
            "role": "assistant",
            "content": result.content
        })
        
        return state
    
    # Create the graph
    workflow = StateGraph(MarketingStateDict)
    
    # Add nodes
    workflow.add_node("assess_request", assess_request)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("tools", tool_node)
    
    # Add edges
    workflow.add_conditional_edges(
        "assess_request",
        lambda state: "generate_response"  # Simplified to always go to generate_response
    )
    
    workflow.add_edge("generate_response", END)
    
    # Set the entry point
    workflow.set_entry_point("assess_request")
    
    return workflow.compile()


def create_initial_state() -> MarketingStateDict:
    """
    Create the initial state for the marketing and communications agent.
    
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
        "channels": [],
        "content": [],
        "attendees": [],
        "registration_forms": [],
        "campaigns": [],
        "marketing_plan": None,
        "communication_plan": None,
        "current_task": "generate_response"
    }
