"""
Enhanced tenant-aware conversation models for multi-tenant AI Event Planner.

This module provides comprehensive tenant, user, and conversation/event ID scoping
for all conversations in the system, ensuring proper data isolation and context tracking.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Boolean, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base


class TenantConversation(Base):
    """
    Enhanced conversation model with full tenant, user, and event context.
    
    This model ensures that every conversation is properly scoped to:
    1. A tenant (organization)
    2. A user within that tenant
    3. A conversation/event ID for context tracking
    """
    
    __tablename__ = "tenant_conversations"
    __table_args__ = (
        # Composite indexes for efficient querying
        Index('idx_tenant_user_conversations', 'organization_id', 'user_id'),
        Index('idx_tenant_event_conversations', 'organization_id', 'event_id'),
        Index('idx_conversation_context', 'organization_id', 'user_id', 'event_id'),
        Index('idx_conversation_status', 'organization_id', 'status', 'updated_at'),
        {'extend_existing': True}
    )
    
    # Primary identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Tenant context (required)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # User context (required)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Event/Conversation context (optional but recommended)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True, index=True)
    
    # Conversation metadata
    conversation_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String(255), default="New Conversation")
    description = Column(Text, nullable=True)
    
    # Conversation type and status
    conversation_type = Column(String(50), default="event_planning")  # event_planning, general, support
    status = Column(String(50), default="active")  # active, paused, completed, archived
    
    # Agent context
    primary_agent_type = Column(String(100), nullable=True)  # coordinator, financial, marketing, etc.
    agent_context = Column(JSON, nullable=True)  # Store agent-specific context
    
    # Conversation flow tracking
    current_phase = Column(String(100), nullable=True)  # planning, execution, review, etc.
    completion_percentage = Column(Integer, default=0)  # 0-100
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="tenant_conversations")
    user = relationship("User", back_populates="tenant_conversations")
    event = relationship("Event", back_populates="tenant_conversations")
    messages = relationship("TenantMessage", back_populates="conversation", cascade="all, delete-orphan")
    agent_states = relationship("TenantAgentState", back_populates="conversation", cascade="all, delete-orphan")
    conversation_context = relationship("ConversationContext", back_populates="conversation", uselist=False, cascade="all, delete-orphan")


class TenantMessage(Base):
    """
    Enhanced message model with full tenant context.
    
    Every message is tied to a tenant, user, and conversation for proper isolation.
    """
    
    __tablename__ = "tenant_messages"
    __table_args__ = (
        Index('idx_tenant_conversation_messages', 'organization_id', 'conversation_id', 'timestamp'),
        Index('idx_tenant_user_messages', 'organization_id', 'user_id', 'timestamp'),
        {'extend_existing': True}
    )
    
    # Primary identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Tenant context (required)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Conversation context (required)
    conversation_id = Column(Integer, ForeignKey("tenant_conversations.id"), nullable=False, index=True)
    
    # User context (required)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Message content
    role = Column(String(50), nullable=False)  # user, assistant, system, agent
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, json, markdown, html
    
    # Agent context (if message is from an agent)
    agent_type = Column(String(100), nullable=True)  # coordinator, financial, marketing, etc.
    agent_id = Column(String(255), nullable=True)  # Unique agent instance identifier
    
    # Message metadata
    message_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    parent_message_id = Column(Integer, ForeignKey("tenant_messages.id"), nullable=True)  # For threading
    
    # Processing metadata
    processing_time_ms = Column(Integer, nullable=True)  # Time taken to generate response
    token_count = Column(Integer, nullable=True)  # Token count for LLM usage tracking
    
    # Message status and flags
    is_internal = Column(Boolean, default=False)  # Internal agent communication
    is_error = Column(Boolean, default=False)  # Error message flag
    requires_action = Column(Boolean, default=False)  # Message requires user action
    
    # Additional context
    message_metadata = Column(JSON, nullable=True)  # Store additional message metadata
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    edited_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    conversation = relationship("TenantConversation", back_populates="messages")
    user = relationship("User")
    parent_message = relationship("TenantMessage", remote_side=[id])
    child_messages = relationship("TenantMessage", remote_side=[parent_message_id])


class TenantAgentState(Base):
    """
    Enhanced agent state model with full tenant context.
    
    Stores agent state information scoped to tenant, user, and conversation.
    """
    
    __tablename__ = "tenant_agent_states"
    __table_args__ = (
        Index('idx_tenant_agent_states', 'organization_id', 'conversation_id', 'agent_type'),
        Index('idx_agent_state_updates', 'organization_id', 'agent_type', 'updated_at'),
        {'extend_existing': True}
    )
    
    # Primary identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Tenant context (required)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Conversation context (required)
    conversation_id = Column(Integer, ForeignKey("tenant_conversations.id"), nullable=False, index=True)
    
    # User context (required)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Agent identification
    agent_type = Column(String(100), nullable=False, index=True)  # coordinator, financial, etc.
    agent_id = Column(String(255), nullable=False)  # Unique agent instance identifier
    agent_version = Column(String(50), nullable=True)  # Agent version for compatibility
    
    # State data
    state_data = Column(JSON, nullable=False)  # Complete agent state
    checkpoint_data = Column(JSON, nullable=True)  # Checkpoint for recovery
    
    # State metadata
    state_version = Column(Integer, default=1)  # State version for migrations
    is_active = Column(Boolean, default=True)  # Whether this state is currently active
    
    # Performance tracking
    total_interactions = Column(Integer, default=0)
    successful_interactions = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_checkpoint_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    conversation = relationship("TenantConversation", back_populates="agent_states")
    user = relationship("User")


class ConversationContext(Base):
    """
    Enhanced conversation context model for storing conversation-specific metadata.
    
    This model stores rich context information about the conversation including
    preferences, decisions, and interaction patterns.
    """
    
    __tablename__ = "conversation_contexts"
    __table_args__ = (
        Index('idx_conversation_context_tenant', 'organization_id', 'conversation_id'),
        {'extend_existing': True}
    )
    
    # Primary identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Tenant context (required)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Conversation context (required)
    conversation_id = Column(Integer, ForeignKey("tenant_conversations.id"), nullable=False, unique=True)
    
    # User context (required)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Context data
    user_preferences = Column(JSON, nullable=True)  # User preferences discovered
    conversation_memory = Column(JSON, nullable=True)  # Conversation memory data
    decision_history = Column(JSON, nullable=True)  # Decisions made in conversation
    topic_transitions = Column(JSON, nullable=True)  # Topic flow tracking
    
    # Event-specific context (if applicable)
    event_requirements = Column(JSON, nullable=True)  # Event planning requirements
    budget_constraints = Column(JSON, nullable=True)  # Budget-related context
    timeline_constraints = Column(JSON, nullable=True)  # Timeline-related context
    stakeholder_context = Column(JSON, nullable=True)  # Stakeholder information
    
    # Interaction patterns
    communication_style = Column(String(100), nullable=True)  # formal, casual, technical
    preferred_detail_level = Column(String(50), nullable=True)  # high, medium, low
    response_preferences = Column(JSON, nullable=True)  # How user prefers responses
    
    # Context metadata
    context_version = Column(Integer, default=1)
    last_summary_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization")
    conversation = relationship("TenantConversation", back_populates="conversation_context")
    user = relationship("User")


class ConversationParticipant(Base):
    """
    Model for tracking multiple participants in a conversation.
    
    Allows for multi-user conversations within a tenant context.
    """
    
    __tablename__ = "conversation_participants"
    __table_args__ = (
        Index('idx_conversation_participants', 'organization_id', 'conversation_id', 'user_id'),
        {'extend_existing': True}
    )
    
    # Primary identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Tenant context (required)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Conversation context (required)
    conversation_id = Column(Integer, ForeignKey("tenant_conversations.id"), nullable=False, index=True)
    
    # User context (required)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Participant role and permissions
    role = Column(String(50), default="participant")  # owner, admin, participant, observer
    permissions = Column(JSON, nullable=True)  # Specific permissions for this participant
    
    # Participation metadata
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Notification preferences
    notification_preferences = Column(JSON, nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    conversation = relationship("TenantConversation")
    user = relationship("User")


# Update existing models to include tenant conversation relationships
def update_existing_models():
    """
    Function to add relationships to existing models.
    This should be called after importing existing models.
    """
    try:
        from app.db.models_saas import Organization
        from app.db.models import User, Event
        
        # Add relationships to Organization
        if not hasattr(Organization, 'tenant_conversations'):
            Organization.tenant_conversations = relationship("TenantConversation", back_populates="organization")
        
        # Add relationships to User
        if not hasattr(User, 'tenant_conversations'):
            User.tenant_conversations = relationship("TenantConversation", back_populates="user")
        
        # Add relationships to Event
        if not hasattr(Event, 'tenant_conversations'):
            Event.tenant_conversations = relationship("TenantConversation", back_populates="event")
            
    except ImportError:
        # Models not available yet, relationships will be added when models are imported
        pass
