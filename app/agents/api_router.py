"""
FastAPI router for agent endpoints with tenant context.

This module provides FastAPI endpoints for interacting with agents
with tenant context and subscription-based access controls.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.db.models_updated import Event
from app.auth.dependencies import get_current_user
from app.middleware.tenant import get_tenant_id, require_tenant
from app.subscription.feature_control import get_feature_control
from app.agents.agent_factory import get_agent_factory
from app.agents.agent_router import (
    get_agent_response,
    get_conversation_history,
    list_conversations,
    delete_conversation
)


# Define request and response models
class AgentFeedbackRequest(BaseModel):
    """Request model for submitting feedback for an agent response."""
    
    conversation_id: str = Field(..., description="Conversation ID")
    message_index: int = Field(..., description="Index of the message in the conversation")
    rating: int = Field(..., description="Rating (1-5)", ge=1, le=5)
    comment: Optional[str] = Field(None, description="Optional feedback comment")


class AgentFeedbackResponse(BaseModel):
    """Response model for submitting feedback for an agent response."""
    
    message: str = Field(..., description="Success message")
    conversation_id: str = Field(..., description="Conversation ID")
    message_index: int = Field(..., description="Index of the message in the conversation")
    organization_id: Optional[int] = Field(None, description="Organization ID")


class AttachEventRequest(BaseModel):
    """Request model for attaching an event to a conversation."""
    
    conversation_id: str = Field(..., description="Conversation ID")
    event_id: int = Field(..., description="Event ID")


class AttachEventResponse(BaseModel):
    """Response model for attaching an event to a conversation."""
    
    message: str = Field(..., description="Success message")
    conversation_id: str = Field(..., description="Conversation ID")
    event_id: int = Field(..., description="Event ID")
    organization_id: Optional[int] = Field(None, description="Organization ID")

class AgentMessageRequest(BaseModel):
    """Agent message request model."""
    
    agent_type: str = Field(..., description="Type of agent to use")
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID (optional)")


class AgentMessageResponse(BaseModel):
    """Agent message response model."""
    
    response: str = Field(..., description="Agent response")
    conversation_id: str = Field(..., description="Conversation ID")
    agent_type: str = Field(..., description="Type of agent used")
    organization_id: Optional[int] = Field(None, description="Organization ID")


class AgentMetadata(BaseModel):
    """Agent metadata model."""
    
    agent_type: str = Field(..., description="Type of agent")
    name: str = Field(..., description="Display name of the agent")
    description: str = Field(..., description="Description of the agent's capabilities")
    icon: str = Field(..., description="Icon identifier for the agent")
    available: bool = Field(..., description="Whether the agent is available for the current subscription")
    subscription_tier: str = Field(..., description="Minimum subscription tier required for this agent")


class AgentAvailabilityResponse(BaseModel):
    """Agent availability response model."""
    
    agents: List[AgentMetadata] = Field(..., description="List of agents with availability information")
    organization_id: Optional[int] = Field(None, description="Organization ID")
    subscription_tier: str = Field(..., description="Current subscription tier")


class ConversationHistoryResponse(BaseModel):
    """Conversation history response model."""
    
    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[Dict[str, Any]] = Field(..., description="Conversation messages")
    agent_type: str = Field(..., description="Type of agent used")
    organization_id: Optional[int] = Field(None, description="Organization ID")


class ConversationsListResponse(BaseModel):
    """Conversations list response model."""
    
    conversations: List[Dict[str, Any]] = Field(..., description="List of conversations")
    total: int = Field(..., description="Total number of conversations")
    limit: int = Field(..., description="Maximum number of conversations returned")
    offset: int = Field(..., description="Offset for pagination")
    organization_id: Optional[int] = Field(None, description="Organization ID")


class DeleteConversationResponse(BaseModel):
    """Delete conversation response model."""
    
    message: str = Field(..., description="Success message")
    conversation_id: str = Field(..., description="Conversation ID")
    organization_id: Optional[int] = Field(None, description="Organization ID")


class AgentAnalyticsResponse(BaseModel):
    """Agent analytics response model."""
    
    total_conversations: int = Field(..., description="Total number of conversations")
    conversations_by_agent: List[Dict[str, Any]] = Field(..., description="Conversations by agent type")
    messages_by_agent: List[Dict[str, Any]] = Field(..., description="Messages by agent type")
    conversations_by_date: List[Dict[str, Any]] = Field(..., description="Conversations by date")
    organization_id: Optional[int] = Field(None, description="Organization ID")


# Agent metadata definitions
AGENT_METADATA = {
    "coordinator": {
        "name": "Event Coordinator",
        "description": "Orchestrates the event planning process and delegates tasks to specialized agents",
        "icon": "bi-diagram-3",
        "subscription_tier": "free"
    },
    "resource_planning": {
        "name": "Resource Planner",
        "description": "Plans and manages resources needed for your event",
        "icon": "bi-calendar-check",
        "subscription_tier": "free"
    },
    "financial": {
        "name": "Financial Advisor",
        "description": "Handles budgeting, cost estimation, and financial planning",
        "icon": "bi-cash-coin",
        "subscription_tier": "professional"
    },
    "stakeholder_management": {
        "name": "Stakeholder Manager",
        "description": "Manages communication and relationships with event stakeholders",
        "icon": "bi-people",
        "subscription_tier": "professional"
    },
    "marketing_communications": {
        "name": "Marketing Specialist",
        "description": "Creates marketing strategies and communication plans",
        "icon": "bi-megaphone",
        "subscription_tier": "professional"
    },
    "project_management": {
        "name": "Project Manager",
        "description": "Manages timelines, tasks, and overall project execution",
        "icon": "bi-kanban",
        "subscription_tier": "professional"
    },
    "analytics": {
        "name": "Analytics Expert",
        "description": "Analyzes event data and provides insights for improvement",
        "icon": "bi-graph-up",
        "subscription_tier": "enterprise"
    },
    "compliance_security": {
        "name": "Compliance & Security Specialist",
        "description": "Ensures event compliance with regulations and security requirements",
        "icon": "bi-shield-check",
        "subscription_tier": "enterprise"
    }
}

# Subscription tier hierarchy
SUBSCRIPTION_TIERS = {
    "free": 0,
    "professional": 1,
    "enterprise": 2
}

# Create router
router = APIRouter()


@router.get("/agents/available", response_model=AgentAvailabilityResponse)
async def get_available_agents(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get available agents for the current subscription tier.
    
    Args:
        request: FastAPI request
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        List of available agents with metadata
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None
        
        # Default to free tier
        subscription_tier = "free"
        
        try:
            # Get feature control with tenant context
            feature_control = get_feature_control(db=db, organization_id=organization_id)
            
            # Get current subscription tier
            subscription_tier = feature_control.get_subscription_tier()
        except Exception as feature_error:
            # Log the error but continue with free tier
            print(f"Error getting subscription tier: {str(feature_error)}")
            # Default to free tier
            subscription_tier = "free"
        
        tier_level = SUBSCRIPTION_TIERS.get(subscription_tier, 0)
        
        # Build list of agents with availability information
        agents = []
        for agent_type, metadata in AGENT_METADATA.items():
            agent_tier = metadata["subscription_tier"]
            agent_tier_level = SUBSCRIPTION_TIERS.get(agent_tier, 0)
            
            # Check if agent is available for current subscription
            available = tier_level >= agent_tier_level
            
            agents.append(AgentMetadata(
                agent_type=agent_type,
                name=metadata["name"],
                description=metadata["description"],
                icon=metadata["icon"],
                available=available,
                subscription_tier=agent_tier
            ))
        
        return {
            "agents": agents,
            "organization_id": organization_id,
            "subscription_tier": subscription_tier
        }
        
    except Exception as e:
        # Handle errors
        print(f"Error in get_available_agents: {str(e)}")
        
        # Return a default response with all agents
        agents = []
        for agent_type, metadata in AGENT_METADATA.items():
            agents.append(AgentMetadata(
                agent_type=agent_type,
                name=metadata["name"],
                description=metadata["description"],
                icon=metadata["icon"],
                available=True,  # Default to available
                subscription_tier=metadata["subscription_tier"]
            ))
        
        return {
            "agents": agents,
            "organization_id": None,
            "subscription_tier": "free"
        }


@router.post("/agents/message", response_model=AgentMessageResponse)
async def send_message_to_agent(
    request: Request,
    message_request: AgentMessageRequest = Body(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Send a message to an agent and get a response.
    
    Args:
        request: FastAPI request
        message_request: Agent message request
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        Agent response
    """
    return await get_agent_response(
        agent_type=message_request.agent_type,
        message=message_request.message,
        conversation_id=message_request.conversation_id,
        request=request,
        db=db,
        current_user_id=current_user_id
    )


@router.get("/agents/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_agent_conversation(
    conversation_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get conversation history for an agent.
    
    Args:
        conversation_id: Conversation ID
        request: FastAPI request
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        Conversation history
    """
    return await get_conversation_history(
        conversation_id=conversation_id,
        request=request,
        db=db,
        current_user_id=current_user_id
    )


@router.get("/agents/conversations", response_model=ConversationsListResponse)
async def list_agent_conversations(
    limit: int = 100,
    offset: int = 0,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    List conversations for the current organization.
    
    Args:
        limit: Maximum number of conversations to return
        offset: Offset for pagination
        request: FastAPI request
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        List of conversations
    """
    return await list_conversations(
        limit=limit,
        offset=offset,
        request=request,
        db=db,
        current_user_id=current_user_id
    )


@router.delete("/agents/conversations/{conversation_id}", response_model=DeleteConversationResponse)
async def delete_agent_conversation(
    conversation_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete a conversation.
    
    Args:
        conversation_id: Conversation ID
        request: FastAPI request
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        Success message
    """
    return await delete_conversation(
        conversation_id=conversation_id,
        request=request,
        db=db,
        current_user_id=current_user_id
    )


@router.get("/agents/analytics", response_model=AgentAnalyticsResponse)
async def get_agent_analytics(
    request: Request,
    start_date: str = None,
    end_date: str = None,
    agent_type: str = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get analytics data for agent usage.
    
    Args:
        request: FastAPI request
        start_date: Start date for analytics (YYYY-MM-DD)
        end_date: End date for analytics (YYYY-MM-DD)
        agent_type: Filter by agent type
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        Analytics data
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None
        
        # Get agent factory with tenant context
        agent_factory = get_agent_factory(db=db, organization_id=organization_id)
        
        # Get all conversations for this organization
        conversations = agent_factory.state_manager.list_conversations()
        
        # Parse date filters
        start_datetime = None
        end_datetime = None
        
        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        
        # Filter conversations by date and agent type
        filtered_conversations = []
        for conv in conversations:
            # Skip if no created_at timestamp
            if "created_at" not in conv:
                continue
            
            # Parse conversation timestamp
            try:
                conv_datetime = datetime.fromisoformat(conv["created_at"])
            except (ValueError, TypeError):
                continue
            
            # Apply date filters
            if start_datetime and conv_datetime < start_datetime:
                continue
            
            if end_datetime and conv_datetime >= end_datetime:
                continue
            
            # Apply agent type filter
            if agent_type and conv.get("agent_type") != agent_type:
                continue
            
            filtered_conversations.append(conv)
        
        # Calculate analytics metrics
        total_conversations = len(filtered_conversations)
        conversations_by_agent = {}
        messages_by_agent = {}
        conversations_by_date = {}
        feedback_by_agent = {}
        feedback_counts = {}
        
        for conv in filtered_conversations:
            # Count conversations by agent
            agent_type = conv.get("agent_type", "unknown")
            conversations_by_agent[agent_type] = conversations_by_agent.get(agent_type, 0) + 1
            
            # Count messages by agent and collect feedback
            messages = conv.get("messages", [])
            messages_by_agent[agent_type] = messages_by_agent.get(agent_type, 0) + len(messages)
            
            # Process feedback
            for message in messages:
                if message.get("role") == "assistant" and "feedback" in message:
                    feedback = message["feedback"]
                    rating = feedback.get("rating", 0)
                    
                    # Initialize feedback data for this agent if not exists
                    if agent_type not in feedback_by_agent:
                        feedback_by_agent[agent_type] = {
                            "total_rating": 0,
                            "count": 0,
                            "ratings": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                        }
                    
                    # Update feedback data
                    feedback_by_agent[agent_type]["total_rating"] += rating
                    feedback_by_agent[agent_type]["count"] += 1
                    feedback_by_agent[agent_type]["ratings"][rating] = feedback_by_agent[agent_type]["ratings"].get(rating, 0) + 1
                    
                    # Update overall feedback counts
                    feedback_counts[rating] = feedback_counts.get(rating, 0) + 1
            
            # Count conversations by date
            try:
                conv_date = datetime.fromisoformat(conv["created_at"]).strftime("%Y-%m-%d")
                conversations_by_date[conv_date] = conversations_by_date.get(conv_date, 0) + 1
            except (ValueError, TypeError, KeyError):
                pass
        
        # Calculate average ratings and format feedback data
        feedback_by_agent_list = []
        for agent_type, data in feedback_by_agent.items():
            avg_rating = data["total_rating"] / data["count"] if data["count"] > 0 else 0
            feedback_by_agent_list.append({
                "agent_type": agent_type,
                "average_rating": round(avg_rating, 1),
                "count": data["count"],
                "ratings_distribution": [
                    {"rating": rating, "count": count}
                    for rating, count in data["ratings"].items()
                ]
            })
        
        # Format overall feedback counts
        feedback_distribution = [
            {"rating": rating, "count": count}
            for rating, count in sorted(feedback_counts.items())
        ]
        
        # Calculate overall average rating
        total_ratings = sum(rating * count for rating, count in feedback_counts.items())
        total_feedback_count = sum(feedback_counts.values())
        overall_avg_rating = round(total_ratings / total_feedback_count, 1) if total_feedback_count > 0 else 0
        
        # Prepare response
        return {
            "total_conversations": total_conversations,
            "conversations_by_agent": [
                {"agent_type": agent, "count": count}
                for agent, count in conversations_by_agent.items()
            ],
            "messages_by_agent": [
                {"agent_type": agent, "count": count}
                for agent, count in messages_by_agent.items()
            ],
            "conversations_by_date": [
                {"date": date, "count": count}
                for date, count in sorted(conversations_by_date.items())
            ],
            "feedback": {
                "total_count": total_feedback_count,
                "average_rating": overall_avg_rating,
                "distribution": feedback_distribution,
                "by_agent": feedback_by_agent_list
            },
            "organization_id": organization_id
        }
        
    except Exception as e:
        print(f"Error in get_agent_analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analytics data: {str(e)}"
        )


@router.post("/agents/attach-event", response_model=AttachEventResponse)
async def attach_event_to_conversation(
    request: Request,
    attach_request: AttachEventRequest = Body(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Attach an event to a conversation.
    
    Args:
        request: FastAPI request
        attach_request: Attach event request
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        Success message
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None
        
        # Verify that the conversation exists and belongs to this organization
        conversation_id = attach_request.conversation_id
        event_id = attach_request.event_id
        
        # Get agent factory with tenant context
        agent_factory = get_agent_factory(db=db, organization_id=organization_id)
        
        # Get conversation state
        state = agent_factory.state_manager.get_conversation_state(conversation_id)
        
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Check if the conversation belongs to the current organization
        if organization_id and state.get("organization_id") != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this conversation"
            )
        
        # Get the event
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found"
            )
        
        # Update the conversation state with event context
        state["event_context"] = {
            "event_id": event.id,
            "title": event.title,
            "description": event.description,
            "start_date": event.start_date.isoformat() if event.start_date else None,
            "end_date": event.end_date.isoformat() if event.end_date else None,
            "location": event.location,
            "attendee_count": event.attendee_count,
            "event_type": event.event_type,
            "budget": event.budget
        }
        
        # Update the state
        agent_factory.state_manager.update_conversation_state(conversation_id, state)
        
        # Add a system message about the attached event
        if "messages" in state:
            state["messages"].append({
                "role": "system",
                "content": f"Event '{event.title}' has been attached to this conversation. The agent now has access to the event details.",
                "timestamp": datetime.utcnow().isoformat()
            })
            agent_factory.state_manager.update_conversation_state(conversation_id, state)
        
        return {
            "message": f"Event {event_id} attached to conversation {conversation_id}",
            "conversation_id": conversation_id,
            "event_id": event_id,
            "organization_id": organization_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in attach_event_to_conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error attaching event to conversation: {str(e)}"
        )


@router.post("/agents/feedback", response_model=AgentFeedbackResponse)
async def submit_agent_feedback(
    request: Request,
    feedback_request: AgentFeedbackRequest = Body(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Submit feedback for an agent response.
    
    Args:
        request: FastAPI request
        feedback_request: Feedback request
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        Success message
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None
        
        # Verify that the conversation exists and belongs to this organization
        conversation_id = feedback_request.conversation_id
        message_index = feedback_request.message_index
        rating = feedback_request.rating
        comment = feedback_request.comment
        
        # Get agent factory with tenant context
        agent_factory = get_agent_factory(db=db, organization_id=organization_id)
        
        # Get conversation state
        state = agent_factory.state_manager.get_conversation_state(conversation_id)
        
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Check if the conversation belongs to the current organization
        if organization_id and state.get("organization_id") != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this conversation"
            )
        
        # Check if the message index is valid
        if "messages" not in state or message_index >= len(state["messages"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid message index: {message_index}"
            )
        
        # Get the message
        message = state["messages"][message_index]
        
        # Check if the message is from the assistant
        if message.get("role") != "assistant":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback can only be provided for assistant messages"
            )
        
        # Add feedback to the message
        message["feedback"] = {
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": current_user_id
        }
        
        # Update the state
        agent_factory.state_manager.update_conversation_state(conversation_id, state)
        
        return {
            "message": "Feedback submitted successfully",
            "conversation_id": conversation_id,
            "message_index": message_index,
            "organization_id": organization_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in submit_agent_feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}"
        )
