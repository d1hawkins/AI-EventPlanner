from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class Task(BaseModel):
    """Model for a project task."""
    id: str = Field(..., description="Unique identifier for the task")
    name: str = Field(..., description="Name of the task")
    description: str = Field(..., description="Description of the task")
    status: str = Field(..., description="Status of the task (not_started, in_progress, completed, blocked)")
    priority: str = Field(..., description="Priority of the task (low, medium, high, critical)")
    assigned_to: Optional[str] = Field(None, description="Person or agent assigned to the task")
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks that must be completed before this task")
    start_date: Optional[datetime] = Field(None, description="Planned start date")
    end_date: Optional[datetime] = Field(None, description="Planned end date")
    actual_start_date: Optional[datetime] = Field(None, description="Actual start date")
    actual_end_date: Optional[datetime] = Field(None, description="Actual end date")
    completion_percentage: int = Field(0, description="Percentage of task completed", ge=0, le=100)
    notes: Optional[str] = Field(None, description="Additional notes about the task")

class Milestone(BaseModel):
    """Model for a project milestone."""
    id: str = Field(..., description="Unique identifier for the milestone")
    name: str = Field(..., description="Name of the milestone")
    description: str = Field(..., description="Description of the milestone")
    date: datetime = Field(..., description="Date of the milestone")
    status: str = Field(..., description="Status of the milestone (not_reached, reached, delayed)")
    associated_tasks: List[str] = Field(default_factory=list, description="IDs of tasks associated with this milestone")

class Risk(BaseModel):
    """Model for a project risk."""
    id: str = Field(..., description="Unique identifier for the risk")
    name: str = Field(..., description="Name of the risk")
    description: str = Field(..., description="Description of the risk")
    probability: str = Field(..., description="Probability of the risk occurring (low, medium, high)")
    impact: str = Field(..., description="Impact if the risk occurs (low, medium, high)")
    status: str = Field(..., description="Status of the risk (identified, mitigated, occurred, resolved)")
    mitigation_plan: Optional[str] = Field(None, description="Plan to mitigate the risk")
    contingency_plan: Optional[str] = Field(None, description="Plan to execute if the risk occurs")
    owner: Optional[str] = Field(None, description="Person or agent responsible for monitoring this risk")

class Timeline(BaseModel):
    """Model for a project timeline."""
    tasks: List[Task] = Field(default_factory=list, description="List of tasks in the timeline")
    milestones: List[Milestone] = Field(default_factory=list, description="List of milestones in the timeline")
    critical_path: List[str] = Field(default_factory=list, description="IDs of tasks on the critical path")
    start_date: datetime = Field(..., description="Start date of the project")
    end_date: datetime = Field(..., description="End date of the project")

class ProjectPlan(BaseModel):
    """Model for a comprehensive project plan."""
    id: str = Field(..., description="Unique identifier for the project plan")
    event_id: str = Field(..., description="ID of the associated event")
    timeline: Timeline = Field(..., description="Project timeline")
    tasks: List[Task] = Field(default_factory=list, description="List of all tasks")
    milestones: List[Milestone] = Field(default_factory=list, description="List of all milestones")
    risks: List[Risk] = Field(default_factory=list, description="List of identified risks")
    status_summary: str = Field(..., description="Overall status summary of the project")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TaskUpdateSchema(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assigned_agent: Optional[str] = None
    due_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
