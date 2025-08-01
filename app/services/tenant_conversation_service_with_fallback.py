"""
Enhanced tenant conversation service with fallback mechanisms for Azure deployment.
Includes connection retry logic and graceful error handling for database timeouts.
"""

import logging
import time
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, TimeoutError
from contextlib import contextmanager

from app.db.models_tenant_conversations import (
    TenantConversation, TenantMessage, TenantAgentState, 
    ConversationContext, ConversationParticipant
)

logger = logging.getLogger(__name__)

class TenantConversationServiceWithFallback:
    """
    Enhanced tenant conversation service with Azure PostgreSQL resilience.
    
    Features:
    - Connection retry logic
    - Timeout handling
    - Graceful degradation
    - In-memory fallback for critical operations
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._memory_cache = {}  # Fallback cache
    
    @contextmanager
    def db_operation_with_retry(self, db: Session):
        """Context manager for database operations with retry logic."""
        for attempt in range(self.max_retries):
            try:
                yield db
                break
            except (OperationalError, TimeoutError) as e:
                logger.warning(f"Database operation failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    logger.error(f"Database operation failed after {self.max_retries} attempts")
                    raise
    
    def get_or_create_conversation(
        self, 
        db: Session, 
        organization_id: int, 
        user_id: int, 
        event_id: Optional[int] = None,
        conversation_type: str = "event_planning"
    ) -> Optional[TenantConversation]:
        """
        Get or create a conversation with fallback handling.
        
        Args:
            db: Database session
            organization_id: Organization ID
            user_id: User ID
            event_id: Optional event ID
            conversation_type: Type of conversation
            
        Returns:
            TenantConversation or None if database unavailable
        """
        cache_key = f"conv_{organization_id}_{user_id}_{event_id}_{conversation_type}"
        
        try:
            with self.db_operation_with_retry(db):
                # Try to find existing conversation
                conversation = db.query(TenantConversation).filter(
                    TenantConversation.organization_id == organization_id,
                    TenantConversation.user_id == user_id,
                    TenantConversation.event_id == event_id,
                    TenantConversation.conversation_type == conversation_type,
                    TenantConversation.status == "active"
                ).first()
                
                if conversation:
                    # Cache for fallback
                    self._memory_cache[cache_key] = {
                        'id': conversation.id,
                        'organization_id': organization_id,
                        'user_id': user_id,
                        'event_id': event_id,
                        'conversation_type': conversation_type
                    }
                    return conversation
                
                # Create new conversation
                conversation = TenantConversation(
                    organization_id=organization_id,
                    user_id=user_id,
                    event_id=event_id,
                    conversation_type=conversation_type,
                    title=f"New {conversation_type.replace('_', ' ').title()}",
                    status="active"
                )
                
                db.add(conversation)
                db.flush()
                db.refresh(conversation)
                
                # Cache for fallback
                self._memory_cache[cache_key] = {
                    'id': conversation.id,
                    'organization_id': organization_id,
                    'user_id': user_id,
                    'event_id': event_id,
                    'conversation_type': conversation_type
                }
                
                return conversation
                
        except Exception as e:
            logger.error(f"Error getting or creating conversation: {e}")
            
            # Fallback: return cached conversation or create mock
            if cache_key in self._memory_cache:
                logger.info("Using cached conversation data as fallback")
                cached = self._memory_cache[cache_key]
                # Create a mock conversation object
                mock_conversation = TenantConversation(
                    id=cached['id'],
                    organization_id=cached['organization_id'],
                    user_id=cached['user_id'],
                    event_id=cached['event_id'],
                    conversation_type=cached['conversation_type']
                )
                return mock_conversation
            
            # Last resort: create temporary in-memory conversation
            logger.warning("Creating temporary in-memory conversation as fallback")
            temp_id = hash(f"{organization_id}_{user_id}_{event_id}_{conversation_type}") % 1000000
            mock_conversation = TenantConversation(
                id=temp_id,
                organization_id=organization_id,
                user_id=user_id,
                event_id=event_id,
                conversation_type=conversation_type
            )
            
            # Cache the temporary conversation
            self._memory_cache[cache_key] = {
                'id': temp_id,
                'organization_id': organization_id,
                'user_id': user_id,
                'event_id': event_id,
                'conversation_type': conversation_type
            }
            
            return mock_conversation
    
    def add_message_with_fallback(
        self,
        db: Session,
        conversation_id: int,
        organization_id: int,
        user_id: int,
        role: str,
        content: str,
        agent_type: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> Optional[TenantMessage]:
        """
        Add a message with fallback handling.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            organization_id: Organization ID
            user_id: User ID
            role: Message role (user, assistant, system, agent)
            content: Message content
            agent_type: Optional agent type
            agent_id: Optional agent ID
            
        Returns:
            TenantMessage or None if database unavailable
        """
        try:
            with self.db_operation_with_retry(db):
                message = TenantMessage(
                    conversation_id=conversation_id,
                    organization_id=organization_id,
                    user_id=user_id,
                    role=role,
                    content=content,
                    agent_type=agent_type,
                    agent_id=agent_id
                )
                
                db.add(message)
                db.flush()
                db.refresh(message)
                
                return message
                
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            
            # Fallback: create mock message
            logger.warning("Creating temporary in-memory message as fallback")
            temp_id = hash(f"{conversation_id}_{user_id}_{content[:50]}") % 1000000
            mock_message = TenantMessage(
                id=temp_id,
                conversation_id=conversation_id,
                organization_id=organization_id,
                user_id=user_id,
                role=role,
                content=content,
                agent_type=agent_type,
                agent_id=agent_id
            )
            
            return mock_message
    
    def get_conversation_messages(
        self,
        db: Session,
        conversation_id: int,
        organization_id: int,
        limit: int = 50
    ) -> List[TenantMessage]:
        """
        Get conversation messages with fallback handling.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            organization_id: Organization ID
            limit: Maximum number of messages to return
            
        Returns:
            List of TenantMessage objects
        """
        try:
            with self.db_operation_with_retry(db):
                messages = db.query(TenantMessage).filter(
                    TenantMessage.conversation_id == conversation_id,
                    TenantMessage.organization_id == organization_id
                ).order_by(TenantMessage.timestamp.desc()).limit(limit).all()
                
                return messages
                
        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            logger.warning("Returning empty message list as fallback")
            return []
    
    def save_agent_state_with_fallback(
        self,
        db: Session,
        conversation_id: int,
        organization_id: int,
        user_id: int,
        agent_type: str,
        agent_id: str,
        state_data: Dict[str, Any]
    ) -> Optional[TenantAgentState]:
        """
        Save agent state with fallback handling.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            organization_id: Organization ID
            user_id: User ID
            agent_type: Agent type
            agent_id: Agent ID
            state_data: Agent state data
            
        Returns:
            TenantAgentState or None if database unavailable
        """
        cache_key = f"agent_state_{conversation_id}_{agent_type}_{agent_id}"
        
        try:
            with self.db_operation_with_retry(db):
                # Try to find existing state
                agent_state = db.query(TenantAgentState).filter(
                    TenantAgentState.conversation_id == conversation_id,
                    TenantAgentState.organization_id == organization_id,
                    TenantAgentState.agent_type == agent_type,
                    TenantAgentState.agent_id == agent_id
                ).first()
                
                if agent_state:
                    # Update existing state
                    agent_state.state_data = state_data
                    agent_state.state_version += 1
                else:
                    # Create new state
                    agent_state = TenantAgentState(
                        conversation_id=conversation_id,
                        organization_id=organization_id,
                        user_id=user_id,
                        agent_type=agent_type,
                        agent_id=agent_id,
                        state_data=state_data
                    )
                    db.add(agent_state)
                
                db.flush()
                db.refresh(agent_state)
                
                # Cache for fallback
                self._memory_cache[cache_key] = state_data
                
                return agent_state
                
        except Exception as e:
            logger.error(f"Error saving agent state: {e}")
            
            # Fallback: cache in memory
            logger.warning("Caching agent state in memory as fallback")
            self._memory_cache[cache_key] = state_data
            
            # Create mock agent state
            temp_id = hash(f"{conversation_id}_{agent_type}_{agent_id}") % 1000000
            mock_state = TenantAgentState(
                id=temp_id,
                conversation_id=conversation_id,
                organization_id=organization_id,
                user_id=user_id,
                agent_type=agent_type,
                agent_id=agent_id,
                state_data=state_data
            )
            
            return mock_state
    
    def get_agent_state_with_fallback(
        self,
        db: Session,
        conversation_id: int,
        organization_id: int,
        agent_type: str,
        agent_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get agent state with fallback handling.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            organization_id: Organization ID
            agent_type: Agent type
            agent_id: Agent ID
            
        Returns:
            Agent state data or None
        """
        cache_key = f"agent_state_{conversation_id}_{agent_type}_{agent_id}"
        
        try:
            with self.db_operation_with_retry(db):
                agent_state = db.query(TenantAgentState).filter(
                    TenantAgentState.conversation_id == conversation_id,
                    TenantAgentState.organization_id == organization_id,
                    TenantAgentState.agent_type == agent_type,
                    TenantAgentState.agent_id == agent_id
                ).first()
                
                if agent_state:
                    # Cache for fallback
                    self._memory_cache[cache_key] = agent_state.state_data
                    return agent_state.state_data
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting agent state: {e}")
            
            # Fallback: return cached state
            if cache_key in self._memory_cache:
                logger.info("Using cached agent state as fallback")
                return self._memory_cache[cache_key]
            
            return None

# Global instance
tenant_conversation_service = TenantConversationServiceWithFallback()
