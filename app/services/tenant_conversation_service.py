"""
Tenant-aware conversation service for multi-tenant AI Event Planner.

This service provides comprehensive conversation management with proper tenant,
user, and event ID scoping, ensuring data isolation and context tracking.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.db.models_tenant_conversations import (
    TenantConversation, 
    TenantMessage, 
    TenantAgentState, 
    ConversationContext,
    ConversationParticipant
)
from app.db.models import User
from app.db.models_saas import Organization
from app.db.models_updated import Event
from app.utils.conversation_memory import ConversationMemory
from app.middleware.tenant import get_tenant_id, get_current_organization
from app.utils.llm_factory import get_llm
import re


class TenantConversationService:
    """
    Service for managing tenant-aware conversations with full context tracking.
    
    This service ensures that all conversations are properly scoped to:
    1. Tenant (Organization)
    2. User
    3. Conversation/Event ID
    """
    
    def __init__(self, db: Session, organization_id: Optional[int] = None, user_id: Optional[int] = None):
        """
        Initialize the tenant conversation service.
        
        Args:
            db: Database session
            organization_id: Organization ID for tenant context
            user_id: User ID for user context
        """
        self.db = db
        self.organization_id = organization_id
        self.user_id = user_id
    
    def create_conversation(
        self,
        title: str = "New Conversation",
        conversation_type: str = "event_planning",
        event_id: Optional[int] = None,
        description: Optional[str] = None,
        primary_agent_type: Optional[str] = None,
        agent_context: Optional[Dict[str, Any]] = None
    ) -> TenantConversation:
        """
        Create a new tenant-aware conversation.
        
        Args:
            title: Conversation title
            conversation_type: Type of conversation
            event_id: Optional event ID to associate with conversation
            description: Optional conversation description
            primary_agent_type: Primary agent type for this conversation
            agent_context: Agent-specific context
            
        Returns:
            Created TenantConversation instance
            
        Raises:
            ValueError: If required tenant/user context is missing
        """
        if not self.organization_id:
            raise ValueError("Organization ID is required for creating conversations")
        
        if not self.user_id:
            raise ValueError("User ID is required for creating conversations")
        
        # Validate that the user belongs to the organization
        self._validate_user_organization_access()
        
        # Validate event access if event_id is provided
        if event_id:
            self._validate_event_access(event_id)
        
        # Create the conversation
        conversation = TenantConversation(
            organization_id=self.organization_id,
            user_id=self.user_id,
            event_id=event_id,
            title=title,
            description=description,
            conversation_type=conversation_type,
            primary_agent_type=primary_agent_type,
            agent_context=agent_context or {}
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        # Create initial conversation context
        self._create_initial_context(conversation.id)
        
        # Add the creating user as the primary participant
        self._add_participant(conversation.id, self.user_id, role="owner")
        
        return conversation
    
    def get_conversation(
        self,
        conversation_id: int,
        include_messages: bool = True,
        include_context: bool = True
    ) -> Optional[TenantConversation]:
        """
        Get a conversation with proper tenant/user access validation.
        
        Args:
            conversation_id: Conversation ID
            include_messages: Whether to include messages
            include_context: Whether to include conversation context
            
        Returns:
            TenantConversation instance or None if not found/accessible
        """
        query = self.db.query(TenantConversation).filter(
            and_(
                TenantConversation.id == conversation_id,
                TenantConversation.organization_id == self.organization_id
            )
        )
        
        # Check if user has access to this conversation
        if self.user_id:
            # User must be either the conversation owner or a participant
            participant_query = self.db.query(ConversationParticipant).filter(
                and_(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.user_id == self.user_id,
                    ConversationParticipant.is_active == True
                )
            )
            
            if not participant_query.first():
                # Check if user is the conversation owner
                query = query.filter(TenantConversation.user_id == self.user_id)
        
        conversation = query.first()
        
        if conversation and include_messages:
            # Load messages with proper ordering
            conversation.messages = self.db.query(TenantMessage).filter(
                TenantMessage.conversation_id == conversation_id
            ).order_by(TenantMessage.timestamp.asc()).all()
        
        if conversation and include_context:
            # Load conversation context
            conversation.conversation_context = self.db.query(ConversationContext).filter(
                ConversationContext.conversation_id == conversation_id
            ).first()
        
        return conversation
    
    def list_conversations(
        self,
        limit: int = 50,
        offset: int = 0,
        conversation_type: Optional[str] = None,
        status: Optional[str] = None,
        event_id: Optional[int] = None
    ) -> Tuple[List[TenantConversation], int]:
        """
        List conversations for the current tenant and user.
        
        Args:
            limit: Maximum number of conversations to return
            offset: Offset for pagination
            conversation_type: Filter by conversation type
            status: Filter by conversation status
            event_id: Filter by event ID
            
        Returns:
            Tuple of (conversations list, total count)
        """
        if not self.organization_id:
            return [], 0
        
        # Base query with tenant filtering
        query = self.db.query(TenantConversation).filter(
            TenantConversation.organization_id == self.organization_id
        )
        
        # User access filtering
        if self.user_id:
            # Include conversations where user is owner or participant
            participant_subquery = self.db.query(ConversationParticipant.conversation_id).filter(
                and_(
                    ConversationParticipant.user_id == self.user_id,
                    ConversationParticipant.is_active == True
                )
            ).subquery()
            
            query = query.filter(
                or_(
                    TenantConversation.user_id == self.user_id,
                    TenantConversation.id.in_(participant_subquery)
                )
            )
        
        # Apply filters
        if conversation_type:
            query = query.filter(TenantConversation.conversation_type == conversation_type)
        
        if status:
            query = query.filter(TenantConversation.status == status)
        
        if event_id:
            query = query.filter(TenantConversation.event_id == event_id)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        conversations = query.order_by(
            desc(TenantConversation.last_activity_at)
        ).offset(offset).limit(limit).all()
        
        return conversations, total_count
    
    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        content_type: str = "text",
        agent_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        parent_message_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_internal: bool = False,
        requires_action: bool = False
    ) -> TenantMessage:
        """
        Add a message to a conversation with proper tenant/user context.
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user, assistant, system, agent)
            content: Message content
            content_type: Content type (text, json, markdown, html)
            agent_type: Agent type if message is from an agent
            agent_id: Agent instance ID
            parent_message_id: Parent message ID for threading
            metadata: Additional message metadata
            is_internal: Whether this is an internal message
            requires_action: Whether message requires user action
            
        Returns:
            Created TenantMessage instance
            
        Raises:
            ValueError: If conversation is not accessible
        """
        # Validate conversation access
        conversation = self.get_conversation(conversation_id, include_messages=False)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found or not accessible")
        
        # Create the message
        message = TenantMessage(
            organization_id=self.organization_id,
            conversation_id=conversation_id,
            user_id=self.user_id,
            role=role,
            content=content,
            content_type=content_type,
            agent_type=agent_type,
            agent_id=agent_id,
            parent_message_id=parent_message_id,
            metadata=metadata or {},
            is_internal=is_internal,
            requires_action=requires_action
        )
        
        self.db.add(message)
        
        # Update conversation last activity
        conversation.last_activity_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        # Update conversation context if this is a user message
        if role == "user" and not is_internal:
            self._update_conversation_context(conversation_id, message)
        
        return message
    
    def get_messages(
        self,
        conversation_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
        include_internal: bool = False,
        role_filter: Optional[str] = None
    ) -> List[TenantMessage]:
        """
        Get messages for a conversation with proper access validation.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to return
            offset: Offset for pagination
            include_internal: Whether to include internal messages
            role_filter: Filter by message role
            
        Returns:
            List of TenantMessage instances
        """
        # Validate conversation access
        conversation = self.get_conversation(conversation_id, include_messages=False)
        if not conversation:
            return []
        
        query = self.db.query(TenantMessage).filter(
            TenantMessage.conversation_id == conversation_id
        )
        
        if not include_internal:
            query = query.filter(TenantMessage.is_internal == False)
        
        if role_filter:
            query = query.filter(TenantMessage.role == role_filter)
        
        query = query.order_by(TenantMessage.timestamp.asc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def update_agent_state(
        self,
        conversation_id: int,
        agent_type: str,
        agent_id: str,
        state_data: Dict[str, Any],
        checkpoint_data: Optional[Dict[str, Any]] = None
    ) -> TenantAgentState:
        """
        Update agent state for a conversation.
        
        Args:
            conversation_id: Conversation ID
            agent_type: Agent type
            agent_id: Agent instance ID
            state_data: Complete agent state data
            checkpoint_data: Optional checkpoint data
            
        Returns:
            Updated TenantAgentState instance
        """
        # Validate conversation access
        conversation = self.get_conversation(conversation_id, include_messages=False)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found or not accessible")
        
        # Find existing agent state or create new one
        agent_state = self.db.query(TenantAgentState).filter(
            and_(
                TenantAgentState.conversation_id == conversation_id,
                TenantAgentState.agent_type == agent_type,
                TenantAgentState.agent_id == agent_id
            )
        ).first()
        
        if agent_state:
            # Update existing state
            agent_state.state_data = state_data
            agent_state.checkpoint_data = checkpoint_data
            agent_state.updated_at = datetime.utcnow()
            agent_state.state_version += 1
            
            if checkpoint_data:
                agent_state.last_checkpoint_at = datetime.utcnow()
        else:
            # Create new agent state
            agent_state = TenantAgentState(
                organization_id=self.organization_id,
                conversation_id=conversation_id,
                user_id=self.user_id,
                agent_type=agent_type,
                agent_id=agent_id,
                state_data=state_data,
                checkpoint_data=checkpoint_data
            )
            self.db.add(agent_state)
        
        self.db.commit()
        self.db.refresh(agent_state)
        
        return agent_state
    
    def get_agent_state(
        self,
        conversation_id: int,
        agent_type: str,
        agent_id: str
    ) -> Optional[TenantAgentState]:
        """
        Get agent state for a conversation.
        
        Args:
            conversation_id: Conversation ID
            agent_type: Agent type
            agent_id: Agent instance ID
            
        Returns:
            TenantAgentState instance or None
        """
        # Validate conversation access
        conversation = self.get_conversation(conversation_id, include_messages=False)
        if not conversation:
            return None
        
        return self.db.query(TenantAgentState).filter(
            and_(
                TenantAgentState.conversation_id == conversation_id,
                TenantAgentState.agent_type == agent_type,
                TenantAgentState.agent_id == agent_id
            )
        ).first()
    
    def update_conversation_context(
        self,
        conversation_id: int,
        context_updates: Dict[str, Any]
    ) -> ConversationContext:
        """
        Update conversation context with new information.
        
        Args:
            conversation_id: Conversation ID
            context_updates: Context updates to apply
            
        Returns:
            Updated ConversationContext instance
        """
        # Validate conversation access
        conversation = self.get_conversation(conversation_id, include_messages=False)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found or not accessible")
        
        # Get or create conversation context
        context = self.db.query(ConversationContext).filter(
            ConversationContext.conversation_id == conversation_id
        ).first()
        
        if not context:
            context = ConversationContext(
                organization_id=self.organization_id,
                conversation_id=conversation_id,
                user_id=self.user_id
            )
            self.db.add(context)
        
        # Apply updates
        for key, value in context_updates.items():
            if hasattr(context, key):
                if key in ['user_preferences', 'conversation_memory', 'decision_history', 
                          'topic_transitions', 'event_requirements', 'budget_constraints',
                          'timeline_constraints', 'stakeholder_context', 'response_preferences']:
                    # JSON fields - merge with existing data
                    existing_data = getattr(context, key) or {}
                    if isinstance(existing_data, dict) and isinstance(value, dict):
                        existing_data.update(value)
                        setattr(context, key, existing_data)
                    else:
                        setattr(context, key, value)
                else:
                    # Regular fields - direct update
                    setattr(context, key, value)
        
        context.updated_at = datetime.utcnow()
        context.context_version += 1
        
        self.db.commit()
        self.db.refresh(context)
        
        return context
    
    def add_participant(
        self,
        conversation_id: int,
        user_id: int,
        role: str = "participant",
        permissions: Optional[Dict[str, Any]] = None
    ) -> ConversationParticipant:
        """
        Add a participant to a conversation.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID to add as participant
            role: Participant role
            permissions: Specific permissions for this participant
            
        Returns:
            Created ConversationParticipant instance
        """
        # Validate conversation access
        conversation = self.get_conversation(conversation_id, include_messages=False)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found or not accessible")
        
        # Validate that the user belongs to the same organization
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Check if user is already a participant
        existing_participant = self.db.query(ConversationParticipant).filter(
            and_(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id
            )
        ).first()
        
        if existing_participant:
            # Update existing participant
            existing_participant.role = role
            existing_participant.permissions = permissions
            existing_participant.is_active = True
            existing_participant.last_seen_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(existing_participant)
            return existing_participant
        
        # Create new participant
        participant = ConversationParticipant(
            organization_id=self.organization_id,
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            permissions=permissions or {}
        )
        
        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)
        
        return participant
    
    def get_conversation_summary(self, conversation_id: int) -> Dict[str, Any]:
        """
        Get a comprehensive summary of a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation summary dictionary
        """
        conversation = self.get_conversation(conversation_id, include_messages=True, include_context=True)
        if not conversation:
            return {}
        
        # Get message statistics
        total_messages = len(conversation.messages)
        user_messages = len([m for m in conversation.messages if m.role == "user"])
        agent_messages = len([m for m in conversation.messages if m.role in ["assistant", "agent"]])
        
        # Get participant count
        participants = self.db.query(ConversationParticipant).filter(
            and_(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.is_active == True
            )
        ).count()
        
        # Get agent states
        agent_states = self.db.query(TenantAgentState).filter(
            TenantAgentState.conversation_id == conversation_id
        ).all()
        
        summary = {
            "conversation": {
                "id": conversation.id,
                "uuid": str(conversation.conversation_uuid),
                "title": conversation.title,
                "type": conversation.conversation_type,
                "status": conversation.status,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "last_activity_at": conversation.last_activity_at.isoformat(),
                "completion_percentage": conversation.completion_percentage,
                "current_phase": conversation.current_phase
            },
            "context": {
                "organization_id": conversation.organization_id,
                "user_id": conversation.user_id,
                "event_id": conversation.event_id,
                "primary_agent_type": conversation.primary_agent_type
            },
            "statistics": {
                "total_messages": total_messages,
                "user_messages": user_messages,
                "agent_messages": agent_messages,
                "participants": participants,
                "active_agents": len(agent_states)
            },
            "agents": [
                {
                    "type": state.agent_type,
                    "id": state.agent_id,
                    "version": state.agent_version,
                    "interactions": state.total_interactions,
                    "success_rate": (state.successful_interactions / state.total_interactions 
                                   if state.total_interactions > 0 else 0),
                    "last_updated": state.updated_at.isoformat()
                }
                for state in agent_states
            ]
        }
        
        # Add conversation context if available
        if conversation.conversation_context:
            context = conversation.conversation_context
            summary["context_data"] = {
                "communication_style": context.communication_style,
                "preferred_detail_level": context.preferred_detail_level,
                "has_preferences": bool(context.user_preferences),
                "has_decisions": bool(context.decision_history),
                "has_event_requirements": bool(context.event_requirements),
                "context_version": context.context_version,
                "last_summary_at": context.last_summary_at.isoformat() if context.last_summary_at else None
            }
        
        return summary
    
    def _validate_user_organization_access(self) -> None:
        """Validate that the user has access to the organization."""
        if not self.organization_id or not self.user_id:
            return
        
        # Check if user belongs to the organization
        from app.db.models_saas import OrganizationUser
        
        org_user = self.db.query(OrganizationUser).filter(
            and_(
                OrganizationUser.organization_id == self.organization_id,
                OrganizationUser.user_id == self.user_id
            )
        ).first()
        
        if not org_user:
            raise ValueError(f"User {self.user_id} does not have access to organization {self.organization_id}")
    
    def _validate_event_access(self, event_id: int) -> None:
        """Validate that the user has access to the event."""
        event = self.db.query(Event).filter(
            and_(
                Event.id == event_id,
                Event.organization_id == self.organization_id
            )
        ).first()
        
        if not event:
            raise ValueError(f"Event {event_id} not found or not accessible")
    
    def _create_initial_context(self, conversation_id: int) -> ConversationContext:
        """Create initial conversation context."""
        context = ConversationContext(
            organization_id=self.organization_id,
            conversation_id=conversation_id,
            user_id=self.user_id,
            user_preferences={},
            conversation_memory={},
            decision_history=[],
            topic_transitions=[]
        )
        
        self.db.add(context)
        self.db.commit()
        self.db.refresh(context)
        
        return context
    
    def _add_participant(self, conversation_id: int, user_id: int, role: str = "participant") -> ConversationParticipant:
        """Add a participant to the conversation."""
        participant = ConversationParticipant(
            organization_id=self.organization_id,
            conversation_id=conversation_id,
            user_id=user_id,
            role=role
        )
        
        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)
        
        return participant
    
    def _update_conversation_context(self, conversation_id: int, message: TenantMessage) -> None:
        """Update conversation context based on a new message using NLP analysis."""

        # Extract contextual information from the message
        extracted_context = self._extract_context_from_message(message.content)

        # Build context updates with extracted information
        context_updates = {
            "conversation_memory": {
                "last_user_message": {
                    "content": message.content[:200],  # First 200 chars for quick reference
                    "timestamp": message.timestamp.isoformat(),
                    "message_id": message.id
                }
            }
        }

        # Add extracted preferences if found
        if extracted_context.get("preferences"):
            context_updates["user_preferences"] = extracted_context["preferences"]

        # Add extracted decisions if found
        if extracted_context.get("decisions"):
            if "decisions" not in context_updates:
                context_updates["decisions"] = []
            context_updates["decisions"].extend(extracted_context["decisions"])

        # Add extracted entities (dates, locations, people, etc.)
        if extracted_context.get("entities"):
            context_updates["entities"] = extracted_context["entities"]

        # Add extracted requirements
        if extracted_context.get("requirements"):
            context_updates["requirements"] = extracted_context["requirements"]

        # Add sentiment/tone analysis
        if extracted_context.get("sentiment"):
            context_updates["sentiment"] = extracted_context["sentiment"]

        self.update_conversation_context(conversation_id, context_updates)

    def _extract_context_from_message(self, message_content: str) -> Dict[str, Any]:
        """
        Extract contextual information from a message using NLP.

        This method uses LLM-based analysis to extract:
        - User preferences (budget, venue type, food preferences, etc.)
        - Decisions made
        - Key entities (dates, locations, people)
        - Requirements and constraints
        - Sentiment/tone

        Args:
            message_content: The message text to analyze

        Returns:
            Dictionary containing extracted context information
        """
        if not message_content or len(message_content.strip()) < 10:
            return {}

        try:
            # Use LLM to extract structured information from the message
            llm = get_llm(temperature=0.1)  # Low temperature for consistent extraction

            extraction_prompt = f"""Analyze the following message from a user planning an event and extract structured information.

Message: "{message_content}"

Extract and return a JSON object with the following structure:
{{
  "preferences": {{
    "venue_type": "string or null (e.g., 'outdoor', 'ballroom', 'conference center')",
    "location": "string or null",
    "budget": "string or null (e.g., '$5000', '10000-15000')",
    "date_preference": "string or null",
    "food_preferences": "string or null",
    "atmosphere": "string or null (e.g., 'formal', 'casual', 'professional')",
    "other": {{}}
  }},
  "decisions": [
    "list of concrete decisions made (e.g., 'decided on October 15th', 'chose Italian catering')"
  ],
  "entities": {{
    "dates": ["list of mentioned dates"],
    "locations": ["list of mentioned locations"],
    "people": ["list of mentioned people/contacts"],
    "vendors": ["list of mentioned vendors"]
  }},
  "requirements": [
    "list of specific requirements or constraints (e.g., 'needs parking for 100 cars', 'must have AV equipment')"
  ],
  "sentiment": "positive|neutral|negative|mixed"
}}

Only include fields where you find relevant information. If a field has no information, use null or an empty list/object.
Return ONLY the JSON object, no other text."""

            # Get response from LLM
            response = llm.invoke(extraction_prompt)
            response_text = response.content.strip()

            # Extract JSON from response (handle cases where LLM adds markdown formatting)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())

                # Clean up null/empty values
                cleaned_data = self._clean_extracted_data(extracted_data)
                return cleaned_data
            else:
                # Fallback to basic extraction if LLM doesn't return valid JSON
                return self._basic_context_extraction(message_content)

        except Exception as e:
            # If LLM extraction fails, fall back to basic pattern matching
            print(f"Context extraction error: {e}")
            return self._basic_context_extraction(message_content)

    def _basic_context_extraction(self, message_content: str) -> Dict[str, Any]:
        """
        Fallback method for basic context extraction using pattern matching.

        Args:
            message_content: The message text to analyze

        Returns:
            Dictionary containing basic extracted context
        """
        context = {
            "entities": {},
            "requirements": []
        }

        # Extract dates using common patterns
        date_patterns = [
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?\s*,?\s*\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            r'\b(?:next|this)\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b'
        ]

        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, message_content, re.IGNORECASE))

        if dates:
            context["entities"]["dates"] = dates

        # Extract budget mentions
        budget_pattern = r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?|\d+(?:,\d{3})*\s*dollars?'
        budget_matches = re.findall(budget_pattern, message_content, re.IGNORECASE)

        if budget_matches:
            context["preferences"] = {"budget": ", ".join(budget_matches)}

        # Extract attendee count
        attendee_pattern = r'\b(\d+)\s+(?:people|attendees|guests|participants)\b'
        attendee_matches = re.findall(attendee_pattern, message_content, re.IGNORECASE)

        if attendee_matches:
            if "requirements" not in context:
                context["requirements"] = []
            context["requirements"].append(f"Attendee count: {attendee_matches[0]}")

        # Detect sentiment through keyword analysis
        positive_keywords = ['excited', 'great', 'perfect', 'love', 'excellent', 'wonderful']
        negative_keywords = ['concerned', 'worried', 'problem', 'issue', 'difficult', 'expensive']

        message_lower = message_content.lower()
        positive_count = sum(1 for word in positive_keywords if word in message_lower)
        negative_count = sum(1 for word in negative_keywords if word in message_lower)

        if positive_count > negative_count:
            context["sentiment"] = "positive"
        elif negative_count > positive_count:
            context["sentiment"] = "negative"
        else:
            context["sentiment"] = "neutral"

        return context

    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove null, empty, and meaningless values from extracted data.

        Args:
            data: Raw extracted data dictionary

        Returns:
            Cleaned data dictionary
        """
        cleaned = {}

        for key, value in data.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                cleaned_dict = self._clean_extracted_data(value)
                if cleaned_dict:
                    cleaned[key] = cleaned_dict
            elif isinstance(value, list):
                cleaned_list = [item for item in value if item]
                if cleaned_list:
                    cleaned[key] = cleaned_list
            elif isinstance(value, str) and value.strip():
                cleaned[key] = value.strip()
            elif not isinstance(value, str):
                cleaned[key] = value

        return cleaned


def get_tenant_conversation_service(
    db: Session,
    organization_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> TenantConversationService:
    """
    Factory function to create a TenantConversationService instance.
    
    Args:
        db: Database session
        organization_id: Organization ID for tenant context
        user_id: User ID for user context
        
    Returns:
        TenantConversationService instance
    """
    return TenantConversationService(db=db, organization_id=organization_id, user_id=user_id)
