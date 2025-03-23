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


class TenantAwareStateManager(StateManager):
    """
    Tenant-aware state manager for multi-tenant agent operations.
    
    This class extends the base StateManager to include organization/tenant context,
    ensuring proper data isolation between different organizations.
    """
    
    def __init__(self, organization_id: int = None):
        """
        Initialize the tenant-aware state manager.
        
        Args:
            organization_id: The organization ID for tenant context
        """
        super().__init__()
        self.organization_id = organization_id
    
    def get_conversation_state(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get the state for a specific conversation, filtered by organization.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            The conversation state
        """
        # Get the base state
        state = super().get_conversation_state(conversation_id)
        
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
        
        # Update the state
        super().update_conversation_state(conversation_id, state)
    
    def list_conversations(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List conversations for the current organization.
        
        Args:
            limit: Maximum number of conversations to return
            offset: Offset for pagination
            
        Returns:
            List of conversations
        """
        # Get all conversations
        all_conversations = super().list_conversations(limit=None, offset=0)
        
        # Filter by organization if organization_id is set
        if self.organization_id:
            filtered_conversations = [
                conv for conv in all_conversations 
                if conv.get("organization_id") == self.organization_id
            ]
            
            # Apply pagination
            paginated = filtered_conversations[offset:offset+limit] if limit else filtered_conversations
            return paginated
        
        return all_conversations[offset:offset+limit] if limit else all_conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation, ensuring tenant isolation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            True if deleted, False otherwise
        """
        # Check if the conversation belongs to this organization
        state = self.get_conversation_state(conversation_id)
        if self.organization_id and state.get("organization_id") != self.organization_id:
            # Cannot delete conversations from other organizations
            return False
        
        return super().delete_conversation(conversation_id)
    
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
        
        # Create the initial state
        super().create_initial_state(conversation_id, initial_state)


def get_tenant_aware_state_manager(organization_id: Optional[int] = None) -> TenantAwareStateManager:
    """
    Get a tenant-aware state manager instance.
    
    Args:
        organization_id: The organization ID for tenant context
        
    Returns:
        TenantAwareStateManager instance
    """
    return TenantAwareStateManager(organization_id=organization_id)
