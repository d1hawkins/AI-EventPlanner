from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MarketingChannel(BaseModel):
    """Marketing channel model."""
    
    name: str = Field(..., description="Name of the marketing channel")
    type: str = Field(..., description="Type of channel (e.g., social media, email, print)")
    target_audience: List[str] = Field(..., description="Target audience for this channel")
    cost: Optional[float] = Field(None, description="Cost associated with this channel")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics for this channel")
    content_requirements: Optional[List[str]] = Field(None, description="Content requirements for this channel")
    schedule: Optional[List[Dict[str, Any]]] = Field(None, description="Publishing schedule for this channel")


class MarketingContent(BaseModel):
    """Marketing content model."""
    
    title: str = Field(..., description="Title of the content")
    type: str = Field(..., description="Type of content (e.g., email, social post, blog, video)")
    channel: str = Field(..., description="Channel this content is for")
    content: str = Field(..., description="The actual content")
    target_audience: List[str] = Field(..., description="Target audience for this content")
    publish_date: Optional[datetime] = Field(None, description="Scheduled publish date")
    status: str = Field("draft", description="Status of the content (draft, approved, published)")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics for this content")
    attachments: Optional[List[str]] = Field(None, description="Attachments or media for this content")


class Attendee(BaseModel):
    """Attendee model."""
    
    name: str = Field(..., description="Name of the attendee")
    email: str = Field(..., description="Email of the attendee")
    registration_date: datetime = Field(..., description="Date of registration")
    ticket_type: str = Field(..., description="Type of ticket purchased")
    payment_status: str = Field("pending", description="Payment status")
    check_in_status: bool = Field(False, description="Whether the attendee has checked in")
    special_requirements: Optional[List[str]] = Field(None, description="Special requirements or accommodations")
    communication_preferences: Optional[Dict[str, bool]] = Field(None, description="Communication preferences")
    survey_responses: Optional[Dict[str, Any]] = Field(None, description="Survey responses")


class RegistrationForm(BaseModel):
    """Registration form model."""
    
    title: str = Field(..., description="Title of the registration form")
    description: Optional[str] = Field(None, description="Description of the registration form")
    fields: List[Dict[str, Any]] = Field(..., description="Fields in the registration form")
    ticket_types: List[Dict[str, Any]] = Field(..., description="Available ticket types")
    payment_methods: List[str] = Field(..., description="Available payment methods")
    terms_and_conditions: str = Field(..., description="Terms and conditions")
    privacy_policy: str = Field(..., description="Privacy policy")
    confirmation_message: str = Field(..., description="Confirmation message")
    confirmation_email_template: str = Field(..., description="Confirmation email template")


class MarketingCampaign(BaseModel):
    """Marketing campaign model."""
    
    name: str = Field(..., description="Name of the campaign")
    description: str = Field(..., description="Description of the campaign")
    objectives: List[str] = Field(..., description="Objectives of the campaign")
    target_audience: List[str] = Field(..., description="Target audience for the campaign")
    channels: List[str] = Field(..., description="Channels used in the campaign")
    start_date: datetime = Field(..., description="Start date of the campaign")
    end_date: datetime = Field(..., description="End date of the campaign")
    budget: float = Field(..., description="Budget for the campaign")
    content: List[Dict[str, Any]] = Field(default_factory=list, description="Content for the campaign")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics for the campaign")
    status: str = Field("planned", description="Status of the campaign")


class MarketingPlan(BaseModel):
    """Marketing plan model."""
    
    event_id: str = Field(..., description="ID of the event")
    objectives: List[str] = Field(..., description="Marketing objectives")
    target_audience: List[Dict[str, Any]] = Field(..., description="Target audience segments")
    unique_selling_points: List[str] = Field(..., description="Unique selling points of the event")
    key_messages: List[str] = Field(..., description="Key messages to communicate")
    branding: Dict[str, Any] = Field(..., description="Branding guidelines")
    channels: List[MarketingChannel] = Field(default_factory=list, description="Marketing channels")
    campaigns: List[MarketingCampaign] = Field(default_factory=list, description="Marketing campaigns")
    content_calendar: List[Dict[str, Any]] = Field(default_factory=list, description="Content calendar")
    budget: Dict[str, Any] = Field(..., description="Marketing budget")
    timeline: List[Dict[str, Any]] = Field(..., description="Marketing timeline")
    metrics: Dict[str, Any] = Field(..., description="Success metrics")
    approval_status: str = Field("pending", description="Approval status of the marketing plan")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class CommunicationPlan(BaseModel):
    """Communication plan model."""
    
    event_id: str = Field(..., description="ID of the event")
    stakeholder_groups: List[Dict[str, Any]] = Field(..., description="Stakeholder groups")
    communication_objectives: List[str] = Field(..., description="Communication objectives")
    key_messages: Dict[str, List[str]] = Field(..., description="Key messages by stakeholder group")
    channels: Dict[str, List[str]] = Field(..., description="Communication channels by stakeholder group")
    schedule: List[Dict[str, Any]] = Field(..., description="Communication schedule")
    templates: Dict[str, str] = Field(..., description="Communication templates")
    feedback_mechanisms: List[Dict[str, Any]] = Field(..., description="Feedback mechanisms")
    crisis_communication: Dict[str, Any] = Field(..., description="Crisis communication plan")
    approval_status: str = Field("pending", description="Approval status of the communication plan")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
