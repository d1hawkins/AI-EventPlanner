"""
FastAPI router for agent endpoints with tenant context.

This module provides FastAPI endpoints for interacting with agents
with tenant context and subscription-based access controls.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.middleware.tenant import get_tenant_id, require_tenant
from app.agents.agent_router import (
    get_agent_response,
    get_conversation_history,
    list_conversations,
    delete_conversation
)


# Define request and response models
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


# Create router
router = APIRouter()


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
