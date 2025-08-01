from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Speaker(BaseModel):
    """Speaker model."""
    
    name: str = Field(..., description="Name of the speaker")
    role: str = Field(..., description="Role or title of the speaker")
    topic: str = Field(..., description="Topic or presentation title")
    bio: Optional[str] = Field(None, description="Speaker biography")
    contact_info: Optional[str] = Field(None, description="Contact information")
    requirements: Optional[List[str]] = Field(None, description="Speaker requirements")
    confirmed: bool = Field(False, description="Whether the speaker is confirmed")
    presentation_time: Optional[datetime] = Field(None, description="Scheduled presentation time")


class Sponsor(BaseModel):
    """Sponsor model."""
    
    name: str = Field(..., description="Name of the sponsor")
    level: str = Field(..., description="Sponsorship level (e.g., Gold, Silver, Bronze)")
    contribution: float = Field(..., description="Sponsorship contribution amount")
    benefits: List[str] = Field(..., description="Benefits provided to the sponsor")
    contact_person: str = Field(..., description="Primary contact person")
    contact_info: str = Field(..., description="Contact information")
    logo_url: Optional[str] = Field(None, description="URL to sponsor logo")
    confirmed: bool = Field(False, description="Whether the sponsor is confirmed")


class Volunteer(BaseModel):
    """Volunteer model."""
    
    name: str = Field(..., description="Name of the volunteer")
    role: str = Field(..., description="Assigned role")
    skills: List[str] = Field(..., description="Relevant skills")
    availability: List[str] = Field(..., description="Availability times")
    contact_info: str = Field(..., description="Contact information")
    assigned_tasks: Optional[List[str]] = Field(None, description="Assigned tasks")
    confirmed: bool = Field(False, description="Whether the volunteer is confirmed")


class VIP(BaseModel):
    """VIP attendee model."""
    
    name: str = Field(..., description="Name of the VIP")
    organization: str = Field(..., description="Organization or company")
    role: str = Field(..., description="Role or title")
    special_requirements: Optional[List[str]] = Field(None, description="Special requirements or accommodations")
    contact_info: str = Field(..., description="Contact information")
    confirmed: bool = Field(False, description="Whether the VIP is confirmed")


class StakeholderPlan(BaseModel):
    """Stakeholder management plan model."""
    
    event_id: str = Field(..., description="ID of the event")
    speakers: List[Speaker] = Field(default_factory=list, description="Event speakers")
    sponsors: List[Sponsor] = Field(default_factory=list, description="Event sponsors")
    volunteers: List[Volunteer] = Field(default_factory=list, description="Event volunteers")
    vips: List[VIP] = Field(default_factory=list, description="VIP attendees")
    communication_schedule: List[Dict[str, Any]] = Field(default_factory=list, description="Communication schedule")
    engagement_strategies: Dict[str, List[str]] = Field(default_factory=dict, description="Engagement strategies by stakeholder type")
    approval_status: str = Field("pending", description="Approval status of the stakeholder plan")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
