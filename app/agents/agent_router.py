"""
Agent router for handling agent requests with tenant context.

This module provides functionality to route agent requests to the appropriate
agent with tenant context and subscription-based access controls.
"""

from typing import Dict, Any, Optional, List
import uuid
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.middleware.tenant import get_tenant_id, require_tenant
from app.agents.agent_factory import get_agent_factory
from app.subscription.feature_control import FeatureNotAvailableError


async def get_agent_response(
    agent_type: str,
    message: str,
    conversation_id: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get a response from an agent with tenant context.
    
    Args:
        agent_type: The type of agent to use
        message: The user message
        conversation_id: The conversation ID (optional, will be generated if not provided)
        request: The FastAPI request
        db: Database session
        current_user_id: The current user ID
        
    Returns:
        The agent response
        
    Raises:
        HTTPException: If the agent is not available or an error occurs
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None
        
        # Create a new conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Get agent factory with tenant context
        agent_factory = get_agent_factory(db=db, organization_id=organization_id)
        
        try:
            # Create the agent with tenant context and subscription checks
            agent = agent_factory.create_agent(
                agent_type=agent_type,
                conversation_id=conversation_id
            )
            
            # Add the message to the agent state
            state = agent["state"]
            if "messages" not in state:
                state["messages"] = []
            
            # Add the user message
            state["messages"].append({
                "role": "user",
                "content": message
            })
            
            # Run the agent graph with the updated state
            result = agent["graph"].invoke(state)
            
            # Update the state in the state manager
            agent_factory.state_manager.update_conversation_state(conversation_id, result)
            
            # Extract the assistant's response
            assistant_messages = [
                msg for msg in result.get("messages", [])
                if msg.get("role") == "assistant" and not msg.get("ephemeral", False)
            ]
            
            # Get the last assistant message
            last_message = assistant_messages[-1]["content"] if assistant_messages else "No response from agent."
            
            # Return the response
            return {
                "response": last_message,
                "conversation_id": conversation_id,
                "agent_type": agent_type,
                "organization_id": organization_id
            }
            
        except FeatureNotAvailableError as e:
            # Handle subscription-based access control errors
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
            
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing agent request: {str(e)}"
        )


async def get_conversation_history(
    conversation_id: str,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get conversation history with tenant context.
    
    Args:
        conversation_id: The conversation ID
        request: The FastAPI request
        db: Database session
        current_user_id: The current user ID
        
    Returns:
        The conversation history
        
    Raises:
        HTTPException: If the conversation is not found or an error occurs
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None
        
        # Get agent factory with tenant context
        agent_factory = get_agent_factory(db=db, organization_id=organization_id)
        
        # Get the conversation state
        state = agent_factory.state_manager.get_conversation_state(conversation_id)
        
        # Check if the conversation exists
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
        
        # Extract messages from the state
        messages = [
            {
                "role": msg.get("role"),
                "content": msg.get("content"),
                "timestamp": msg.get("timestamp")
            }
            for msg in state.get("messages", [])
            if not msg.get("ephemeral", False)  # Skip ephemeral messages
        ]
        
        # Return the conversation history
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "agent_type": state.get("agent_type", "unknown"),
            "organization_id": state.get("organization_id")
        }
        
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation history: {str(e)}"
        )


async def list_conversations(
    limit: int = 100,
    offset: int = 0,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    List conversations with tenant context.
    
    Args:
        limit: Maximum number of conversations to return
        offset: Offset for pagination
        request: The FastAPI request
        db: Database session
        current_user_id: The current user ID
        
    Returns:
        List of conversations
        
    Raises:
        HTTPException: If an error occurs
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None
        
        # Get agent factory with tenant context
        agent_factory = get_agent_factory(db=db, organization_id=organization_id)
        
        # List conversations for the current organization
        conversations = agent_factory.state_manager.list_conversations(limit=limit, offset=offset)
        
        # Return the conversations
        return {
            "conversations": conversations,
            "total": len(conversations),
            "limit": limit,
            "offset": offset,
            "organization_id": organization_id
        }
        
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing conversations: {str(e)}"
        )


async def delete_conversation(
    conversation_id: str,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete a conversation with tenant context.
    
    Args:
        conversation_id: The conversation ID
        request: The FastAPI request
        db: Database session
        current_user_id: The current user ID
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If the conversation is not found or an error occurs
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None
        
        # Get agent factory with tenant context
        agent_factory = get_agent_factory(db=db, organization_id=organization_id)
        
        # Delete the conversation
        success = agent_factory.state_manager.delete_conversation(conversation_id)
        
        # Check if the conversation was deleted
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found or you do not have access to it"
            )
        
        # Return success message
        return {
            "message": f"Conversation {conversation_id} deleted successfully",
            "conversation_id": conversation_id,
            "organization_id": organization_id
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )
