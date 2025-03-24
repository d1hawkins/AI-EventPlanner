"""
Tenant-aware state manager for multi-tenant agent operations.

This module extends the base state manager to include tenant context,
ensuring proper data isolation between different organizations.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from app.state.manager import StateManager
from app.db.models_saas import Organization


class TenantAwareStateManager:
    """
    Tenant-aware state manager for multi-tenant agent operations.
    
    This class provides organization/tenant context for state management,
    ensuring proper data isolation between different organizations.
    """
    
    def __init__(self, organization_id: int = None):
        """
        Initialize the tenant-aware state manager.
        
        Args:
            organization_id: The organization ID for tenant context
        """
        self.organization_id = organization_id
        self._conversations = {}
    
    def get_conversation_state(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get the state for a specific conversation, filtered by organization.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            The conversation state
        """
        # Get the state from in-memory storage
        state = self._conversations.get(conversation_id, {})
        
        # Add organization context if not present
        if self.organization_id and "organization_id" not in state:
            state["organization_id"] = self.organization_id
        
        return state
    
    def update_conversation_state(self, conversation_id: str, state: Dict[str, Any]) -> None:
        """
        Update the state for a specific conversation, ensuring tenant context.
        
        Args:
            conversation_id: The conversation ID
            state: The new state
        """
        # Ensure organization context is preserved
        if self.organization_id:
            state["organization_id"] = self.organization_id
        
        # Update the state in in-memory storage
        self._conversations[conversation_id] = state
    
    def list_conversations(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List conversations for the current organization.
        
        Args:
            limit: Maximum number of conversations to return
            offset: Offset for pagination
            
        Returns:
            List of conversations
        """
        # Convert conversations to list of dicts with metadata
        all_conversations = []
        for conv_id, state in self._conversations.items():
            # Skip if organization_id doesn't match
            if self.organization_id and state.get("organization_id") != self.organization_id:
                continue
                
            # Extract basic metadata
            conversation = {
                "id": conv_id,
                "organization_id": state.get("organization_id"),
                "agent_type": state.get("agent_type", "unknown"),
                "created_at": state.get("created_at", datetime.utcnow().isoformat()),
                "last_message": None
            }
            
            # Extract last message if available
            messages = state.get("messages", [])
            if messages:
                last_message = messages[-1]
                conversation["last_message"] = {
                    "content": last_message.get("content", ""),
                    "role": last_message.get("role", "user"),
                    "timestamp": last_message.get("timestamp", datetime.utcnow().isoformat())
                }
            
            all_conversations.append(conversation)
        
        # Sort by created_at (newest first)
        all_conversations.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply pagination
        return all_conversations[offset:offset+limit] if limit else all_conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation, ensuring tenant isolation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            True if deleted, False otherwise
        """
        # Check if the conversation exists
        if conversation_id not in self._conversations:
            return False
            
        # Check if the conversation belongs to this organization
        state = self._conversations.get(conversation_id, {})
        if self.organization_id and state.get("organization_id") != self.organization_id:
            # Cannot delete conversations from other organizations
            return False
        
        # Delete the conversation
        del self._conversations[conversation_id]
        return True
    
    def create_initial_state(self, conversation_id: str, initial_state: Dict[str, Any]) -> None:
        """
        Create initial state for a conversation with tenant context.
        
        Args:
            conversation_id: The conversation ID
            initial_state: The initial state
        """
        # Add organization context
        if self.organization_id:
            initial_state["organization_id"] = self.organization_id
        
        # Add creation timestamp
        initial_state["created_at"] = datetime.utcnow().isoformat()
        
        # Store the initial state
        self._conversations[conversation_id] = initial_state


def get_tenant_aware_state_manager(organization_id: Optional[int] = None) -> TenantAwareStateManager:
    """
    Get a tenant-aware state manager instance.
    
    Args:
        organization_id: The organization ID for tenant context
        
    Returns:
        TenantAwareStateManager instance
    """
    return TenantAwareStateManager(organization_id=organization_id)
