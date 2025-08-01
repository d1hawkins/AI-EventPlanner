"""
Tenant-aware agent communication tools for multi-tenant AI Event Planner.

This module provides agent communication tools that ensure all agent interactions
are properly scoped to tenant, user, and conversation/event context.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
import json
from sqlalchemy.orm import Session
from fastapi import Request

from app.services.tenant_conversation_service import TenantConversationService, get_tenant_conversation_service
from app.db.models_tenant_conversations import TenantConversation, TenantMessage, TenantAgentState
from app.middleware.tenant import get_tenant_id, get_current_organization
from app.utils.conversation_memory import ConversationMemory


class TenantAgentCommunicationTools:
    """
    Tenant-aware agent communication tools.
    
    This class provides methods for agents to communicate within the proper
    tenant, user, and conversation context, ensuring data isolation and
    comprehensive context tracking.
    """
    
    def __init__(
        self,
        db: Session,
        organization_id: int,
        user_id: int,
        conversation_id: int,
        agent_type: str,
        agent_id: Optional[str] = None
    ):
        """
        Initialize tenant-aware agent communication tools.
        
        Args:
            db: Database session
            organization_id: Organization ID for tenant context
            user_id: User ID for user context
            conversation_id: Conversation ID for conversation context
            agent_type: Type of agent (coordinator, financial, marketing, etc.)
            agent_id: Unique agent instance ID (generated if not provided)
        """
        self.db = db
        self.organization_id = organization_id
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.agent_type = agent_type
        self.agent_id = agent_id or f"{agent_type}_{uuid.uuid4().hex[:8]}"
        
        # Initialize conversation service
        self.conversation_service = get_tenant_conversation_service(
            db=db,
            organization_id=organization_id,
            user_id=user_id
        )
        
        # Initialize conversation memory
        self.conversation_memory = ConversationMemory()
        
        # Load existing conversation context
        self._load_conversation_context()
    
    def send_message_to_user(
        self,
        content: str,
        content_type: str = "text",
        requires_action: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TenantMessage:
        """
        Send a message from the agent to the user.
        
        Args:
            content: Message content
            content_type: Content type (text, json, markdown, html)
            requires_action: Whether the message requires user action
            metadata: Additional message metadata
            
        Returns:
            Created TenantMessage instance
        """
        # Add agent context to metadata
        agent_metadata = {
            "agent_type": self.agent_type,
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {})
        }
        
        message = self.conversation_service.add_message(
            conversation_id=self.conversation_id,
            role="assistant",
            content=content,
            content_type=content_type,
            agent_type=self.agent_type,
            agent_id=self.agent_id,
            metadata=agent_metadata,
            requires_action=requires_action
        )
        
        # Update agent interaction statistics
        self._update_agent_statistics(successful=True)
        
        return message
    
    def send_internal_message(
        self,
        target_agent_type: str,
        content: str,
        message_type: str = "communication",
        metadata: Optional[Dict[str, Any]] = None
    ) -> TenantMessage:
        """
        Send an internal message to another agent.
        
        Args:
            target_agent_type: Target agent type
            content: Message content
            message_type: Type of internal message (communication, delegation, status)
            metadata: Additional message metadata
            
        Returns:
            Created TenantMessage instance
        """
        # Add internal message metadata
        internal_metadata = {
            "source_agent_type": self.agent_type,
            "source_agent_id": self.agent_id,
            "target_agent_type": target_agent_type,
            "message_type": message_type,
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {})
        }
        
        message = self.conversation_service.add_message(
            conversation_id=self.conversation_id,
            role="agent",
            content=content,
            content_type="json",
            agent_type=self.agent_type,
            agent_id=self.agent_id,
            metadata=internal_metadata,
            is_internal=True
        )
        
        return message
    
    def get_conversation_history(
        self,
        limit: Optional[int] = 50,
        include_internal: bool = False,
        role_filter: Optional[str] = None
    ) -> List[TenantMessage]:
        """
        Get conversation history with proper tenant/user context.
        
        Args:
            limit: Maximum number of messages to return
            include_internal: Whether to include internal agent messages
            role_filter: Filter by message role
            
        Returns:
            List of TenantMessage instances
        """
        return self.conversation_service.get_messages(
            conversation_id=self.conversation_id,
            limit=limit,
            include_internal=include_internal,
            role_filter=role_filter
        )
    
    def get_user_messages(self, limit: Optional[int] = 20) -> List[TenantMessage]:
        """
        Get recent user messages in the conversation.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of user TenantMessage instances
        """
        return self.conversation_service.get_messages(
            conversation_id=self.conversation_id,
            limit=limit,
            role_filter="user"
        )
    
    def get_agent_messages(
        self,
        agent_type: Optional[str] = None,
        limit: Optional[int] = 20
    ) -> List[TenantMessage]:
        """
        Get messages from a specific agent type or all agents.
        
        Args:
            agent_type: Specific agent type to filter by
            limit: Maximum number of messages to return
            
        Returns:
            List of agent TenantMessage instances
        """
        messages = self.conversation_service.get_messages(
            conversation_id=self.conversation_id,
            limit=limit * 2,  # Get more to filter
            role_filter="assistant"
        )
        
        if agent_type:
            messages = [m for m in messages if m.agent_type == agent_type]
        
        return messages[:limit] if limit else messages
    
    def update_agent_state(
        self,
        state_data: Dict[str, Any],
        checkpoint_data: Optional[Dict[str, Any]] = None
    ) -> TenantAgentState:
        """
        Update the agent's state with tenant context.
        
        Args:
            state_data: Complete agent state data
            checkpoint_data: Optional checkpoint data for recovery
            
        Returns:
            Updated TenantAgentState instance
        """
        # Add tenant context to state data
        enhanced_state_data = {
            **state_data,
            "tenant_context": {
                "organization_id": self.organization_id,
                "user_id": self.user_id,
                "conversation_id": self.conversation_id,
                "agent_type": self.agent_type,
                "agent_id": self.agent_id,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        return self.conversation_service.update_agent_state(
            conversation_id=self.conversation_id,
            agent_type=self.agent_type,
            agent_id=self.agent_id,
            state_data=enhanced_state_data,
            checkpoint_data=checkpoint_data
        )
    
    def get_agent_state(self) -> Optional[TenantAgentState]:
        """
        Get the current agent's state.
        
        Returns:
            TenantAgentState instance or None
        """
        return self.conversation_service.get_agent_state(
            conversation_id=self.conversation_id,
            agent_type=self.agent_type,
            agent_id=self.agent_id
        )
    
    def get_other_agent_state(
        self,
        agent_type: str,
        agent_id: Optional[str] = None
    ) -> Optional[TenantAgentState]:
        """
        Get another agent's state in the same conversation.
        
        Args:
            agent_type: Target agent type
            agent_id: Target agent ID (if None, gets the first agent of that type)
            
        Returns:
            TenantAgentState instance or None
        """
        if agent_id:
            return self.conversation_service.get_agent_state(
                conversation_id=self.conversation_id,
                agent_type=agent_type,
                agent_id=agent_id
            )
        else:
            # Find the first agent of the specified type
            from app.db.models_tenant_conversations import TenantAgentState
            from sqlalchemy import and_
            
            agent_state = self.db.query(TenantAgentState).filter(
                and_(
                    TenantAgentState.conversation_id == self.conversation_id,
                    TenantAgentState.agent_type == agent_type,
                    TenantAgentState.is_active == True
                )
            ).first()
            
            return agent_state
    
    def delegate_task(
        self,
        target_agent_type: str,
        task_description: str,
        task_data: Dict[str, Any],
        priority: str = "normal",
        deadline: Optional[datetime] = None
    ) -> TenantMessage:
        """
        Delegate a task to another agent.
        
        Args:
            target_agent_type: Target agent type
            task_description: Description of the task
            task_data: Task-specific data
            priority: Task priority (low, normal, high, urgent)
            deadline: Optional task deadline
            
        Returns:
            Created delegation TenantMessage
        """
        delegation_content = {
            "action": "delegate_task",
            "task_description": task_description,
            "task_data": task_data,
            "priority": priority,
            "deadline": deadline.isoformat() if deadline else None,
            "delegated_by": {
                "agent_type": self.agent_type,
                "agent_id": self.agent_id
            }
        }
        
        return self.send_internal_message(
            target_agent_type=target_agent_type,
            content=json.dumps(delegation_content),
            message_type="delegation",
            metadata={
                "priority": priority,
                "deadline": deadline.isoformat() if deadline else None
            }
        )
    
    def request_information(
        self,
        target_agent_type: str,
        information_type: str,
        query_parameters: Dict[str, Any],
        urgency: str = "normal"
    ) -> TenantMessage:
        """
        Request information from another agent.
        
        Args:
            target_agent_type: Target agent type
            information_type: Type of information requested
            query_parameters: Parameters for the information query
            urgency: Request urgency (low, normal, high)
            
        Returns:
            Created information request TenantMessage
        """
        request_content = {
            "action": "request_information",
            "information_type": information_type,
            "query_parameters": query_parameters,
            "urgency": urgency,
            "requested_by": {
                "agent_type": self.agent_type,
                "agent_id": self.agent_id
            }
        }
        
        return self.send_internal_message(
            target_agent_type=target_agent_type,
            content=json.dumps(request_content),
            message_type="information_request",
            metadata={
                "information_type": information_type,
                "urgency": urgency
            }
        )
    
    def provide_status_update(
        self,
        status: str,
        progress_percentage: Optional[int] = None,
        details: Optional[str] = None,
        next_steps: Optional[List[str]] = None
    ) -> TenantMessage:
        """
        Provide a status update to the user and other agents.
        
        Args:
            status: Current status (working, completed, blocked, error)
            progress_percentage: Progress percentage (0-100)
            details: Additional status details
            next_steps: List of planned next steps
            
        Returns:
            Created status update TenantMessage
        """
        status_content = {
            "action": "status_update",
            "status": status,
            "progress_percentage": progress_percentage,
            "details": details,
            "next_steps": next_steps or [],
            "agent_info": {
                "agent_type": self.agent_type,
                "agent_id": self.agent_id
            }
        }
        
        # Send as both user message and internal message
        user_message = self.send_message_to_user(
            content=self._format_status_for_user(status_content),
            content_type="text",
            metadata={"message_type": "status_update", "status": status}
        )
        
        # Also send internal status update
        self.send_internal_message(
            target_agent_type="coordinator",  # Status updates go to coordinator
            content=json.dumps(status_content),
            message_type="status_update",
            metadata={"status": status, "progress": progress_percentage}
        )
        
        return user_message
    
    def track_user_preference(
        self,
        preference_type: str,
        value: Any,
        confidence: float = 1.0,
        source: str = "conversation"
    ) -> None:
        """
        Track a discovered user preference.
        
        Args:
            preference_type: Type of preference
            value: Preference value
            confidence: Confidence level (0.0 to 1.0)
            source: Source of the preference discovery
        """
        self.conversation_memory.track_user_preference(
            preference_type=preference_type,
            value=value,
            confidence=confidence
        )
        
        # Update conversation context
        context_updates = {
            "user_preferences": {
                preference_type: {
                    "value": value,
                    "confidence": confidence,
                    "source": source,
                    "discovered_by": self.agent_type,
                    "discovered_at": datetime.utcnow().isoformat()
                }
            }
        }
        
        self.conversation_service.update_conversation_context(
            conversation_id=self.conversation_id,
            context_updates=context_updates
        )
    
    def track_decision(
        self,
        decision_type: str,
        decision: str,
        reasoning: str,
        alternatives_considered: Optional[List[str]] = None
    ) -> None:
        """
        Track a decision made during the conversation.
        
        Args:
            decision_type: Type of decision
            decision: The decision made
            reasoning: Reasoning behind the decision
            alternatives_considered: Other options considered
        """
        self.conversation_memory.track_decision(
            decision_type=decision_type,
            decision=decision,
            reasoning=reasoning,
            alternatives_considered=alternatives_considered or []
        )
        
        # Update conversation context
        decision_record = {
            "decision_type": decision_type,
            "decision": decision,
            "reasoning": reasoning,
            "alternatives_considered": alternatives_considered or [],
            "made_by": self.agent_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        context_updates = {
            "decision_history": [decision_record]  # Will be merged with existing
        }
        
        self.conversation_service.update_conversation_context(
            conversation_id=self.conversation_id,
            context_updates=context_updates
        )
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """
        Get the current conversation context.
        
        Returns:
            Conversation context dictionary
        """
        conversation = self.conversation_service.get_conversation(
            conversation_id=self.conversation_id,
            include_context=True
        )
        
        if conversation and conversation.conversation_context:
            context = conversation.conversation_context
            return {
                "user_preferences": context.user_preferences or {},
                "conversation_memory": context.conversation_memory or {},
                "decision_history": context.decision_history or [],
                "topic_transitions": context.topic_transitions or [],
                "event_requirements": context.event_requirements or {},
                "budget_constraints": context.budget_constraints or {},
                "timeline_constraints": context.timeline_constraints or {},
                "stakeholder_context": context.stakeholder_context or {},
                "communication_style": context.communication_style,
                "preferred_detail_level": context.preferred_detail_level,
                "response_preferences": context.response_preferences or {}
            }
        
        return {}
    
    def get_tenant_context(self) -> Dict[str, Any]:
        """
        Get the tenant context for this conversation.
        
        Returns:
            Tenant context dictionary
        """
        return {
            "organization_id": self.organization_id,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "agent_type": self.agent_type,
            "agent_id": self.agent_id
        }
    
    def log_error(
        self,
        error_message: str,
        error_type: str = "general",
        error_data: Optional[Dict[str, Any]] = None
    ) -> TenantMessage:
        """
        Log an error with proper tenant context.
        
        Args:
            error_message: Error message
            error_type: Type of error
            error_data: Additional error data
            
        Returns:
            Created error log TenantMessage
        """
        error_content = {
            "error_message": error_message,
            "error_type": error_type,
            "error_data": error_data or {},
            "agent_info": {
                "agent_type": self.agent_type,
                "agent_id": self.agent_id
            },
            "tenant_context": self.get_tenant_context()
        }
        
        # Update agent statistics
        self._update_agent_statistics(successful=False)
        
        return self.send_internal_message(
            target_agent_type="coordinator",
            content=json.dumps(error_content),
            message_type="error",
            metadata={"error_type": error_type}
        )
    
    def _load_conversation_context(self) -> None:
        """Load existing conversation context into memory."""
        context = self.get_conversation_context()
        
        # Load conversation memory if available
        if context.get("conversation_memory"):
            memory_data = context["conversation_memory"]
            if isinstance(memory_data, dict):
                # Reconstruct conversation memory from stored data
                for memory_type, data in memory_data.items():
                    if hasattr(self.conversation_memory, 'memory_types'):
                        self.conversation_memory.memory_types[memory_type] = data
    
    def _update_agent_statistics(self, successful: bool) -> None:
        """Update agent interaction statistics."""
        agent_state = self.get_agent_state()
        if agent_state:
            agent_state.total_interactions += 1
            if successful:
                agent_state.successful_interactions += 1
            else:
                agent_state.error_count += 1
            
            self.db.commit()
    
    def _format_status_for_user(self, status_content: Dict[str, Any]) -> str:
        """Format status update for user display."""
        status = status_content.get("status", "unknown")
        progress = status_content.get("progress_percentage")
        details = status_content.get("details", "")
        
        message = f"Status Update: {status.title()}"
        
        if progress is not None:
            message += f" ({progress}% complete)"
        
        if details:
            message += f"\n{details}"
        
        next_steps = status_content.get("next_steps", [])
        if next_steps:
            message += f"\n\nNext steps:\n" + "\n".join(f"• {step}" for step in next_steps)
        
        return message


def get_tenant_agent_communication_tools(
    db: Session,
    organization_id: int,
    user_id: int,
    conversation_id: int,
    agent_type: str,
    agent_id: Optional[str] = None
) -> TenantAgentCommunicationTools:
    """
    Factory function to create TenantAgentCommunicationTools instance.
    
    Args:
        db: Database session
        organization_id: Organization ID for tenant context
        user_id: User ID for user context
        conversation_id: Conversation ID for conversation context
        agent_type: Type of agent
        agent_id: Unique agent instance ID
        
    Returns:
        TenantAgentCommunicationTools instance
    """
    return TenantAgentCommunicationTools(
        db=db,
        organization_id=organization_id,
        user_id=user_id,
        conversation_id=conversation_id,
        agent_type=agent_type,
        agent_id=agent_id
    )


def get_tenant_agent_tools_from_request(
    request: Request,
    db: Session,
    conversation_id: int,
    agent_type: str,
    agent_id: Optional[str] = None
) -> Optional[TenantAgentCommunicationTools]:
    """
    Create TenantAgentCommunicationTools from FastAPI request context.
    
    Args:
        request: FastAPI request object
        db: Database session
        conversation_id: Conversation ID
        agent_type: Type of agent
        agent_id: Unique agent instance ID
        
    Returns:
        TenantAgentCommunicationTools instance or None if context is missing
    """
    try:
        organization_id = get_tenant_id(request)
        if not organization_id:
            return None
        
        # Get user ID from request (this would typically come from authentication)
        user_id = getattr(request.state, 'user_id', None)
        if not user_id:
            return None
        
        return get_tenant_agent_communication_tools(
            db=db,
            organization_id=organization_id,
            user_id=user_id,
            conversation_id=conversation_id,
            agent_type=agent_type,
            agent_id=agent_id
        )
    except Exception:
        return None
