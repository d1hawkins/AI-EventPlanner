from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class EventBase(BaseModel):
    """Base schema for event data."""
    
    title: str
    event_type: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    budget: Optional[int] = None  # Budget in cents
    attendee_count: Optional[int] = None


class EventCreate(EventBase):
    """Schema for creating a new event."""
    
    conversation_id: int


class EventUpdate(BaseModel):
    """Schema for updating an event."""
    
    title: Optional[str] = None
    event_type: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    budget: Optional[int] = None
    attendee_count: Optional[int] = None


class Event(EventBase):
    """Schema for event data returned to clients."""
    
    id: int
    conversation_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    """Base schema for task data."""
    
    title: str
    description: Optional[str] = None
    status: str = "pending"
    assigned_agent: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    
    event_id: int


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assigned_agent: Optional[str] = None
    due_date: Optional[datetime] = None


class Task(TaskBase):
    """Schema for task data returned to clients."""
    
    id: int
    event_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StakeholderBase(BaseModel):
    """Base schema for stakeholder data."""
    
    name: str
    role: str
    contact_info: Optional[str] = None
    notes: Optional[str] = None


class StakeholderCreate(StakeholderBase):
    """Schema for creating a new stakeholder."""
    
    event_id: int


class StakeholderUpdate(BaseModel):
    """Schema for updating a stakeholder."""
    
    name: Optional[str] = None
    role: Optional[str] = None
    contact_info: Optional[str] = None
    notes: Optional[str] = None


class Stakeholder(StakeholderBase):
    """Schema for stakeholder data returned to clients."""
    
    id: int
    event_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EventWithDetails(Event):
    """Schema for event data with tasks and stakeholders."""
    
    tasks: List[Task] = []
    stakeholders: List[Stakeholder] = []
    
    class Config:
        from_attributes = True


# Agent state schemas
class EventDetails(BaseModel):
    """Schema for event details in agent state."""
    
    event_type: Optional[str] = None
    scale: Optional[str] = None
    budget: Optional[float] = None
    timeline_start: Optional[datetime] = None
    timeline_end: Optional[datetime] = None


class Requirements(BaseModel):
    """Schema for requirements in agent state."""
    
    stakeholders: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)


class AgentAssignment(BaseModel):
    """Schema for agent assignment in agent state."""
    
    agent_type: str
    task: str
    status: str = "pending"


class CoordinatorState(BaseModel):
    """Schema for coordinator agent state."""
    
    messages: List[Dict[str, str]] = Field(default_factory=list)
    event_details: EventDetails = Field(default_factory=EventDetails)
    requirements: Requirements = Field(default_factory=Requirements)
    agent_assignments: List[AgentAssignment] = Field(default_factory=list)
    current_phase: str = "initial_assessment"
    next_steps: List[str] = Field(default_factory=list)


class ConversationMessage(BaseModel):
    """Schema for conversation message."""
    
    role: str
    content: str
    timestamp: Optional[datetime] = None


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""
    
    title: Optional[str] = "New Conversation"


class Conversation(BaseModel):
    """Schema for conversation data returned to clients."""
    
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ConversationMessage] = []
    
    class Config:
        from_attributes = True
