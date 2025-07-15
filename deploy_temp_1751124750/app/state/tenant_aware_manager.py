"""
Tenant-aware state manager for multi-tenant agent operations.

This module extends the base state manager to include tenant context,
ensuring proper data isolation between different organizations.
It implements a hybrid approach with in-memory storage for performance
and database persistence for durability.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import json
import uuid
import time
import threading
from sqlalchemy.orm import Session

from app.state.manager import StateManager
from app.db.models_updated import Organization, Conversation, AgentState
from app.db.session import get_db


class TenantAwareStateManager:
    """
    Tenant-aware state manager for multi-tenant agent operations.
    
    This class provides organization/tenant context for state management,
    ensuring proper data isolation between different organizations.
    It uses a hybrid approach with in-memory storage for performance
    and database persistence for durability.
    """
    
    def __init__(self, organization_id: int = None, db: Optional[Session] = None):
        """
        Initialize the tenant-aware state manager.
        
        Args:
            organization_id: The organization ID for tenant context
            db: Database session (optional, will be created if needed)
        """
        self.organization_id = organization_id
        self._conversations = {}  # In-memory storage
        self._db = db
        self._sync_lock = threading.RLock()  # Lock for thread safety
        self._last_sync_time = time.time()
        self._sync_interval = 60  # Sync to database every 60 seconds
        
        # Load conversations from database on startup
        self._load_from_database()
    
    @property
    def db(self) -> Session:
        """
        Get the database session, creating one if needed.
        
        Returns:
            Database session
        """
        if self._db is None:
            self._db = next(get_db())
        return self._db
    
    def _load_from_database(self) -> None:
        """
        Load conversations from the database into in-memory storage.
        """
        try:
            # Query for agent states with the current organization
            query = self.db.query(AgentState).join(Conversation)
            
            if self.organization_id:
                query = query.filter(Conversation.organization_id == self.organization_id)
            
            agent_states = query.all()
            
            # Load each state into memory
            for agent_state in agent_states:
                try:
                    # Get the conversation ID as string (UUID)
                    conversation_id = str(agent_state.conversation.id)
                    
                    # Parse the state data
                    state_data = json.loads(agent_state.state_data)
                    
                    # Store in memory
                    self._conversations[conversation_id] = state_data
                    
                    print(f"Loaded conversation {conversation_id} from database")
                except Exception as e:
                    print(f"Error loading conversation state: {str(e)}")
        except Exception as e:
            print(f"Error loading conversations from database: {str(e)}")
    
    def _sync_to_database(self, conversation_id: str = None) -> None:
        """
        Sync in-memory state to the database.
        
        Args:
            conversation_id: Specific conversation ID to sync (optional)
                            If not provided, all conversations will be synced
        """
        try:
            with self._sync_lock:
                if conversation_id:
                    # Sync specific conversation
                    self._sync_conversation(conversation_id)
                else:
                    # Sync all conversations
                    for conv_id in self._conversations:
                        self._sync_conversation(conv_id)
                
                # Update last sync time
                self._last_sync_time = time.time()
        except Exception as e:
            print(f"Error syncing to database: {str(e)}")
    
    def _sync_conversation(self, conversation_id: str) -> None:
        """
        Sync a specific conversation to the database.
        
        Args:
            conversation_id: The conversation ID to sync
        """
        try:
            # Get the state from memory
            state = self._conversations.get(conversation_id)
            if not state:
                return
            
            # Find or create the conversation in the database
            db_conversation = self._get_or_create_conversation(conversation_id)
            if not db_conversation:
                return
            
            # Find or create the agent state
            agent_state = self.db.query(AgentState).filter(
                AgentState.conversation_id == db_conversation.id
            ).first()
            
            if agent_state:
                # Update existing state
                agent_state.state_data = json.dumps(state)
                agent_state.updated_at = datetime.utcnow()
            else:
                # Create new state
                agent_state = AgentState(
                    conversation_id=db_conversation.id,
                    state_data=json.dumps(state)
                )
                self.db.add(agent_state)
            
            # Commit changes
            self.db.commit()
        except Exception as e:
            print(f"Error syncing conversation {conversation_id}: {str(e)}")
            # Rollback on error
            self.db.rollback()
    
    def _get_or_create_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get or create a conversation in the database.
        
        Args:
            conversation_id: The conversation ID (can be UUID string or integer)
            
        Returns:
            The conversation object or None if error
        """
        try:
            # First, check if we already have a mapping for this conversation_id
            # in our in-memory state
            state = self._conversations.get(conversation_id, {})
            db_conversation_id = state.get("db_conversation_id")
            
            # If we have a database ID in the state, use it to find the conversation
            if db_conversation_id:
                conversation = self.db.query(Conversation).filter(
                    Conversation.id == db_conversation_id
                ).first()
                
                if conversation:
                    return conversation
            
            # Try to parse the conversation_id as an integer
            try:
                conv_id = int(conversation_id)
                # If it's an integer, look for it directly
                conversation = self.db.query(Conversation).filter(
                    Conversation.id == conv_id
                ).first()
                
                if conversation:
                    # Store the mapping in the state for future reference
                    if conversation_id in self._conversations:
                        self._conversations[conversation_id]["db_conversation_id"] = conversation.id
                    return conversation
            except ValueError:
                # If it's not an integer, it's a UUID string
                # Look for a conversation with this UUID in the title or metadata
                pass
            
            # If we get here, we need to create a new conversation
            state = self._conversations.get(conversation_id, {})
            title = state.get("agent_type", "Unknown Agent")
            
            # Create a new conversation with the UUID in the title for reference
            conversation = Conversation(
                title=f"Conversation with {title} ({conversation_id})",
                organization_id=self.organization_id
            )
            
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            
            # Store the mapping in the state for future reference
            if conversation_id in self._conversations:
                self._conversations[conversation_id]["db_conversation_id"] = conversation.id
            
            return conversation
        except Exception as e:
            print(f"Error getting or creating conversation: {str(e)}")
            self.db.rollback()
            return None
    
    def _check_periodic_sync(self) -> None:
        """
        Check if it's time for a periodic sync and perform it if needed.
        """
        current_time = time.time()
        if current_time - self._last_sync_time > self._sync_interval:
            # Time for a periodic sync
            self._sync_to_database()
    
    def get_conversation_state(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get the state for a specific conversation, filtered by organization.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            The conversation state
        """
        # Check for periodic sync
        self._check_periodic_sync()
        
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
        
        # Sync to database for critical operations
        # This is a critical operation, so we sync immediately
        self._sync_to_database(conversation_id)
    
    def list_conversations(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List conversations for the current organization.
        
        Args:
            limit: Maximum number of conversations to return
            offset: Offset for pagination
            
        Returns:
            List of conversations
        """
        # Check for periodic sync
        self._check_periodic_sync()
        
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
        
        # Delete from in-memory storage
        del self._conversations[conversation_id]
        
        # Delete from database
        try:
            # Try to parse the conversation_id as an integer
            try:
                conv_id = int(conversation_id)
            except ValueError:
                # If it's not an integer, we can't find it in the database
                return True
            
            # Find the conversation in the database
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conv_id
            ).first()
            
            if conversation:
                # Delete the agent state first (due to foreign key constraint)
                agent_state = self.db.query(AgentState).filter(
                    AgentState.conversation_id == conversation.id
                ).first()
                
                if agent_state:
                    self.db.delete(agent_state)
                
                # Delete the conversation
                self.db.delete(conversation)
                self.db.commit()
        except Exception as e:
            print(f"Error deleting conversation from database: {str(e)}")
            self.db.rollback()
        
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
        
        # Store the initial state in memory
        self._conversations[conversation_id] = initial_state
        
        # Sync to database immediately
        self._sync_to_database(conversation_id)
    
    def force_sync(self) -> None:
        """
        Force a sync of all conversations to the database.
        """
        self._sync_to_database()


def get_tenant_aware_state_manager(organization_id: Optional[int] = None, db: Optional[Session] = None) -> TenantAwareStateManager:
    """
    Get a tenant-aware state manager instance.
    
    Args:
        organization_id: The organization ID for tenant context
        db: Database session (optional)
        
    Returns:
        TenantAwareStateManager instance
    """
    return TenantAwareStateManager(organization_id=organization_id, db=db)
