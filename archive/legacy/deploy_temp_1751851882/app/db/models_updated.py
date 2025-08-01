import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Boolean, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """User model for authentication and conversation ownership."""
    
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    stripe_customer_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    organizations = relationship("OrganizationUser", back_populates="user", cascade="all, delete-orphan")


class Organization(Base):
    """
    Organization/Tenant model for multi-tenancy.
    """
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    plan_id = Column(String(50), nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    subscription_status = Column(String(50), default="inactive")
    max_users = Column(Integer, default=5)
    max_events = Column(Integer, default=10)
    features = Column(Text, default='{"basic": true, "advanced": false, "premium": false}')
    
    @property
    def features_dict(self):
        """Convert features JSON string to dictionary."""
        if isinstance(self.features, dict):
            return self.features
        try:
            return json.loads(self.features)
        except (json.JSONDecodeError, TypeError):
            return {"basic": True, "advanced": False, "premium": False}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("OrganizationUser", back_populates="organization", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="organization")
    conversations = relationship("Conversation", back_populates="organization")


class OrganizationUser(Base):
    """
    Association table for users and organizations with role information.
    """
    __tablename__ = "organization_users"
    
    organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String(50), nullable=False)  # admin, manager, user
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    user = relationship("User", back_populates="organizations")


class SubscriptionPlan(Base):
    """
    Subscription plan model.
    """
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    stripe_price_id = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Price in cents
    interval = Column(String(20), default="month")  # month, year
    max_users = Column(Integer, default=5)
    max_events = Column(Integer, default=10)
    features = Column(Text, default='{"basic": true, "advanced": false, "premium": false}')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SubscriptionInvoice(Base):
    """
    Subscription invoice model.
    """
    __tablename__ = "subscription_invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    stripe_invoice_id = Column(String(255), nullable=True)
    amount = Column(Integer, nullable=False)  # Amount in cents
    status = Column(String(50), default="pending")  # pending, paid, failed
    invoice_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    paid_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization")


class Conversation(Base):
    """Conversation model for tracking chat sessions."""
    
    __tablename__ = "conversations"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    organization = relationship("Organization", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    agent_state = relationship("AgentState", back_populates="conversation", uselist=False, cascade="all, delete-orphan")
    event = relationship("Event", back_populates="conversation", uselist=False, cascade="all, delete-orphan")


class Message(Base):
    """Message model for storing chat messages."""
    
    __tablename__ = "messages"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)  # "user", "assistant", "system"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class AgentState(Base):
    """AgentState model for storing the state of the agent."""
    
    __tablename__ = "agent_states"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), unique=True)
    state_data = Column(JSON)  # Store the agent state as JSON
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="agent_state")


class Event(Base):
    """Event model for storing event details."""
    
    __tablename__ = "events"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), unique=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    title = Column(String)
    event_type = Column(String)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    location = Column(String, nullable=True)
    budget = Column(Integer, nullable=True)  # Budget in cents
    attendee_count = Column(Integer, nullable=True)
    
    # Recurrence fields
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String, nullable=True)  # iCalendar RRULE format
    recurrence_end_date = Column(DateTime, nullable=True)
    recurrence_exceptions = Column(JSON, nullable=True)  # Dates to exclude from recurrence
    parent_event_id = Column(Integer, ForeignKey("events.id"), nullable=True)  # For recurring event instances
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="event")
    organization = relationship("Organization", back_populates="events")
    tasks = relationship("Task", back_populates="event", cascade="all, delete-orphan")
    stakeholders = relationship("Stakeholder", back_populates="event", cascade="all, delete-orphan")


class Task(Base):
    """Task model for tracking event planning tasks."""
    
    __tablename__ = "tasks"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, in_progress, completed, cancelled
    assigned_agent = Column(String, nullable=True)  # Type of agent assigned
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="tasks")


class Stakeholder(Base):
    """Stakeholder model for tracking event stakeholders."""
    
    __tablename__ = "stakeholders"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    name = Column(String)
    role = Column(String)  # sponsor, speaker, volunteer, attendee, etc.
    contact_info = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="stakeholders")
