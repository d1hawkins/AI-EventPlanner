from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Boolean, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """User model for authentication and conversation ownership."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    stripe_customer_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    """Conversation model for tracking chat sessions."""
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    agent_state = relationship("AgentState", back_populates="conversation", uselist=False, cascade="all, delete-orphan")
    event = relationship("Event", back_populates="conversation", uselist=False, cascade="all, delete-orphan")


class Message(Base):
    """Message model for storing chat messages."""
    
    __tablename__ = "messages"
    
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
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), unique=True)
    state_data = Column(JSON)  # Store the agent state as JSON
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="agent_state")


class Event(Base):
    """Event model for storing event details."""
    
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), unique=True)
    title = Column(String)
    event_type = Column(String)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    location = Column(String, nullable=True)
    budget = Column(Integer, nullable=True)  # Budget in cents
    attendee_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="event")
    tasks = relationship("Task", back_populates="event", cascade="all, delete-orphan")
    stakeholders = relationship("Stakeholder", back_populates="event", cascade="all, delete-orphan")


class Task(Base):
    """Task model for tracking event planning tasks."""
    
    __tablename__ = "tasks"
    
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
