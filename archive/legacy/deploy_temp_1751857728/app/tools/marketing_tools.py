from typing import Dict, Any, List, Optional, Type
from datetime import datetime, timedelta
import uuid

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.schemas.marketing import (
    MarketingChannel, 
    MarketingContent, 
    Attendee, 
    RegistrationForm, 
    MarketingCampaign, 
    MarketingPlan, 
    CommunicationPlan
)


class ChannelManagementInput(BaseModel):
    """Input schema for the channel management tool."""
    
    name: str = Field(..., description="Name of the marketing channel")
    type: str = Field(..., description="Type of channel (e.g., social media, email, print)")
    target_audience: List[str] = Field(..., description="Target audience for this channel")
    cost: Optional[float] = Field(None, description="Cost associated with this channel")
    content_requirements: Optional[List[str]] = Field(None, description="Content requirements for this channel")
    schedule: Optional[List[Dict[str, Any]]] = Field(None, description="Publishing schedule for this channel")


class ChannelManagementTool(BaseTool):
    """Tool for managing marketing channels."""
    
    name: str = "channel_management_tool"
    description: str = "Manage marketing channels for the event"
    args_schema: Type[ChannelManagementInput] = ChannelManagementInput
    
    def _run(self, name: str, type: str, target_audience: List[str],
             cost: Optional[float] = None, content_requirements: Optional[List[str]] = None,
             schedule: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Run the channel management tool.
        
        Args:
            name: Name of the marketing channel
            type: Type of channel
            target_audience: Target audience for this channel
            cost: Cost associated with this channel
            content_requirements: Content requirements for this channel
            schedule: Publishing schedule for this channel
            
        Returns:
            Dictionary with channel details
        """
        # Create a MarketingChannel object
        channel = MarketingChannel(
            name=name,
            type=type,
            target_audience=target_audience,
            cost=cost,
            content_requirements=content_requirements or [],
            schedule=schedule or [],
            metrics={}
        )
        
        # Generate a unique ID for the channel
        channel_id = str(uuid.uuid4())
        
        # Generate standard content requirements based on channel type if not provided
        if not content_requirements:
            if type.lower() == "social media":
                content_requirements = [
                    "Short, engaging posts (max 280 characters)",
                    "High-quality images (1200x628px)",
                    "Relevant hashtags",
                    "Call to action"
                ]
            elif type.lower() == "email":
                content_requirements = [
                    "Compelling subject line",
                    "Personalized greeting",
                    "Clear value proposition",
                    "Mobile-friendly design",
                    "Unsubscribe option"
                ]
            elif type.lower() == "website":
                content_requirements = [
                    "SEO-optimized content",
                    "Clear navigation",
                    "Mobile responsiveness",
                    "Fast loading time",
                    "Clear call to action"
                ]
            elif type.lower() == "print":
                content_requirements = [
                    "High-resolution images (300 DPI)",
                    "Bleed area (3mm)",
                    "CMYK color mode",
                    "Vector logos",
                    "Contact information"
                ]
            else:
                content_requirements = ["Content appropriate for channel type"]
            
            channel.content_requirements = content_requirements
        
        # Generate a standard schedule if not provided
        if not schedule:
            # Create a schedule starting from 2 months before the event
            now = datetime.now()
            start_date = now - timedelta(days=60)
            
            if type.lower() == "social media":
                schedule = [
                    {"date": (start_date + timedelta(days=i*7)).strftime("%Y-%m-%d"), "content_type": "announcement", "frequency": "weekly"}
                    for i in range(8)
                ]
            elif type.lower() == "email":
                schedule = [
                    {"date": (start_date + timedelta(days=i*14)).strftime("%Y-%m-%d"), "content_type": "newsletter", "frequency": "bi-weekly"}
                    for i in range(4)
                ]
            elif type.lower() == "website":
                schedule = [
                    {"date": start_date.strftime("%Y-%m-%d"), "content_type": "event page", "frequency": "one-time"},
                    {"date": (start_date + timedelta(days=30)).strftime("%Y-%m-%d"), "content_type": "update", "frequency": "one-time"}
                ]
            else:
                schedule = [
                    {"date": (start_date + timedelta(days=30)).strftime("%Y-%m-%d"), "content_type": "general", "frequency": "one-time"}
                ]
            
            channel.schedule = schedule
        
        return {
            "channel_id": channel_id,
            "channel": channel.dict(),
            "management_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "active"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class ContentCreationInput(BaseModel):
    """Input schema for the content creation tool."""
    
    title: str = Field(..., description="Title of the content")
    type: str = Field(..., description="Type of content (e.g., email, social post, blog, video)")
    channel: str = Field(..., description="Channel this content is for")
    content: str = Field(..., description="The actual content")
    target_audience: List[str] = Field(..., description="Target audience for this content")
    publish_date: Optional[str] = Field(None, description="Scheduled publish date (YYYY-MM-DD)")
    attachments: Optional[List[str]] = Field(None, description="Attachments or media for this content")


class ContentCreationTool(BaseTool):
    """Tool for creating marketing content."""
    
    name: str = "content_creation_tool"
    description: str = "Create marketing content for the event"
    args_schema: Type[ContentCreationInput] = ContentCreationInput
    
    def _run(self, title: str, type: str, channel: str, content: str,
             target_audience: List[str], publish_date: Optional[str] = None,
             attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the content creation tool.
        
        Args:
            title: Title of the content
            type: Type of content
            channel: Channel this content is for
            content: The actual content
            target_audience: Target audience for this content
            publish_date: Scheduled publish date
            attachments: Attachments or media for this content
            
        Returns:
            Dictionary with content details
        """
        # Parse publish date if provided
        publish_date_obj = None
        if publish_date:
            try:
                publish_date_obj = datetime.strptime(publish_date, "%Y-%m-%d")
            except ValueError:
                # If date parsing fails, use None
                pass
        
        # Create a MarketingContent object
        marketing_content = MarketingContent(
            title=title,
            type=type,
            channel=channel,
            content=content,
            target_audience=target_audience,
            publish_date=publish_date_obj,
            status="draft",
            attachments=attachments or [],
            metrics={}
        )
        
        # Generate a unique ID for the content
        content_id = str(uuid.uuid4())
        
        # Provide content improvement suggestions based on type
        improvement_suggestions = []
        if type.lower() == "email":
            improvement_suggestions = [
                "Personalize the subject line to increase open rates",
                "Keep the email concise and focused on a single call to action",
                "Use a mobile-friendly design",
                "Include social sharing buttons",
                "Test the email on different devices and email clients"
            ]
        elif type.lower() == "social post":
            improvement_suggestions = [
                "Include relevant hashtags to increase visibility",
                "Use eye-catching visuals",
                "Keep the post concise and engaging",
                "Include a clear call to action",
                "Consider the optimal posting time for your audience"
            ]
        elif type.lower() == "blog":
            improvement_suggestions = [
                "Use SEO-friendly keywords in the title and throughout the content",
                "Break up text with subheadings, bullet points, and images",
                "Include internal and external links",
                "Add a compelling meta description",
                "End with a clear call to action"
            ]
        elif type.lower() == "video":
            improvement_suggestions = [
                "Keep the video concise and focused on a single message",
                "Include captions for accessibility",
                "Optimize the thumbnail image",
                "Include a call to action in the video and description",
                "Consider the optimal video length for the platform"
            ]
        
        return {
            "content_id": content_id,
            "content": marketing_content.dict(),
            "improvement_suggestions": improvement_suggestions,
            "management_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "draft"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class AttendeeManagementInput(BaseModel):
    """Input schema for the attendee management tool."""
    
    name: str = Field(..., description="Name of the attendee")
    email: str = Field(..., description="Email of the attendee")
    registration_date: str = Field(..., description="Date of registration (YYYY-MM-DD)")
    ticket_type: str = Field(..., description="Type of ticket purchased")
    payment_status: Optional[str] = Field("pending", description="Payment status")
    special_requirements: Optional[List[str]] = Field(None, description="Special requirements or accommodations")
    communication_preferences: Optional[Dict[str, bool]] = Field(None, description="Communication preferences")


class AttendeeManagementTool(BaseTool):
    """Tool for managing attendees."""
    
    name: str = "attendee_management_tool"
    description: str = "Manage attendees for the event"
    args_schema: Type[AttendeeManagementInput] = AttendeeManagementInput
    
    def _run(self, name: str, email: str, registration_date: str, ticket_type: str,
             payment_status: str = "pending", special_requirements: Optional[List[str]] = None,
             communication_preferences: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        """
        Run the attendee management tool.
        
        Args:
            name: Name of the attendee
            email: Email of the attendee
            registration_date: Date of registration
            ticket_type: Type of ticket purchased
            payment_status: Payment status
            special_requirements: Special requirements or accommodations
            communication_preferences: Communication preferences
            
        Returns:
            Dictionary with attendee details
        """
        # Parse registration date
        registration_date_obj = None
        try:
            registration_date_obj = datetime.strptime(registration_date, "%Y-%m-%d")
        except ValueError:
            # If date parsing fails, use current date
            registration_date_obj = datetime.now()
        
        # Create an Attendee object
        attendee = Attendee(
            name=name,
            email=email,
            registration_date=registration_date_obj,
            ticket_type=ticket_type,
            payment_status=payment_status,
            check_in_status=False,
            special_requirements=special_requirements or [],
            communication_preferences=communication_preferences or {"marketing": True, "updates": True, "surveys": True},
            survey_responses={}
        )
        
        # Generate a unique ID for the attendee
        attendee_id = str(uuid.uuid4())
        
        # Generate standard communication preferences if not provided
        if not communication_preferences:
            communication_preferences = {
                "marketing": True,
                "updates": True,
                "surveys": True,
                "reminders": True,
                "post_event": True
            }
            attendee.communication_preferences = communication_preferences
        
        return {
            "attendee_id": attendee_id,
            "attendee": attendee.dict(),
            "management_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "registered"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class RegistrationFormCreationInput(BaseModel):
    """Input schema for the registration form creation tool."""
    
    title: str = Field(..., description="Title of the registration form")
    description: Optional[str] = Field(None, description="Description of the registration form")
    fields: List[Dict[str, Any]] = Field(..., description="Fields in the registration form")
    ticket_types: List[Dict[str, Any]] = Field(..., description="Available ticket types")
    payment_methods: List[str] = Field(..., description="Available payment methods")
    terms_and_conditions: str = Field(..., description="Terms and conditions")
    privacy_policy: str = Field(..., description="Privacy policy")


class RegistrationFormCreationTool(BaseTool):
    """Tool for creating registration forms."""
    
    name: str = "registration_form_creation_tool"
    description: str = "Create registration forms for the event"
    args_schema: Type[RegistrationFormCreationInput] = RegistrationFormCreationInput
    
    def _run(self, title: str, fields: List[Dict[str, Any]], ticket_types: List[Dict[str, Any]],
             payment_methods: List[str], terms_and_conditions: str, privacy_policy: str,
             description: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the registration form creation tool.
        
        Args:
            title: Title of the registration form
            description: Description of the registration form
            fields: Fields in the registration form
            ticket_types: Available ticket types
            payment_methods: Available payment methods
            terms_and_conditions: Terms and conditions
            privacy_policy: Privacy policy
            
        Returns:
            Dictionary with registration form details
        """
        # Create a RegistrationForm object
        registration_form = RegistrationForm(
            title=title,
            description=description,
            fields=fields,
            ticket_types=ticket_types,
            payment_methods=payment_methods,
            terms_and_conditions=terms_and_conditions,
            privacy_policy=privacy_policy,
            confirmation_message="Thank you for registering for our event! We look forward to seeing you there.",
            confirmation_email_template="Dear {name},\n\nThank you for registering for {event_title}. Your registration has been confirmed.\n\nEvent Details:\nDate: {event_date}\nLocation: {event_location}\nTicket Type: {ticket_type}\n\nIf you have any questions, please contact us at {contact_email}.\n\nBest regards,\nThe Event Team"
        )
        
        # Generate a unique ID for the registration form
        form_id = str(uuid.uuid4())
        
        # Provide form improvement suggestions
        improvement_suggestions = [
            "Keep the form as short as possible to increase completion rates",
            "Make sure required fields are clearly marked",
            "Include a progress indicator for multi-page forms",
            "Ensure the form is mobile-friendly",
            "Test the form on different devices and browsers",
            "Consider adding social login options",
            "Include clear error messages for validation failures"
        ]
        
        return {
            "form_id": form_id,
            "registration_form": registration_form.dict(),
            "improvement_suggestions": improvement_suggestions,
            "management_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "active"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class CampaignCreationInput(BaseModel):
    """Input schema for the campaign creation tool."""
    
    name: str = Field(..., description="Name of the campaign")
    description: str = Field(..., description="Description of the campaign")
    objectives: List[str] = Field(..., description="Objectives of the campaign")
    target_audience: List[str] = Field(..., description="Target audience for the campaign")
    channels: List[str] = Field(..., description="Channels used in the campaign")
    start_date: str = Field(..., description="Start date of the campaign (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date of the campaign (YYYY-MM-DD)")
    budget: float = Field(..., description="Budget for the campaign")
    content: Optional[List[Dict[str, Any]]] = Field(None, description="Content for the campaign")


class CampaignCreationTool(BaseTool):
    """Tool for creating marketing campaigns."""
    
    name: str = "campaign_creation_tool"
    description: str = "Create marketing campaigns for the event"
    args_schema: Type[CampaignCreationInput] = CampaignCreationInput
    
    def _run(self, name: str, description: str, objectives: List[str],
             target_audience: List[str], channels: List[str], start_date: str,
             end_date: str, budget: float, content: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Run the campaign creation tool.
        
        Args:
            name: Name of the campaign
            description: Description of the campaign
            objectives: Objectives of the campaign
            target_audience: Target audience for the campaign
            channels: Channels used in the campaign
            start_date: Start date of the campaign
            end_date: End date of the campaign
            budget: Budget for the campaign
            content: Content for the campaign
            
        Returns:
            Dictionary with campaign details
        """
        # Parse dates
        start_date_obj = None
        end_date_obj = None
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            # If date parsing fails, use default dates
            start_date_obj = datetime.now()
            end_date_obj = datetime.now() + timedelta(days=30)
        
        # Create a MarketingCampaign object
        campaign = MarketingCampaign(
            name=name,
            description=description,
            objectives=objectives,
            target_audience=target_audience,
            channels=channels,
            start_date=start_date_obj,
            end_date=end_date_obj,
            budget=budget,
            content=content or [],
            status="planned"
        )
        
        # Generate a unique ID for the campaign
        campaign_id = str(uuid.uuid4())
        
        # Generate standard content if not provided
        if not content:
            content = []
            for channel in channels:
                if channel.lower() == "email":
                    content.append({
                        "title": f"{name} - Email Announcement",
                        "type": "email",
                        "channel": "email",
                        "description": "Initial campaign announcement email",
                        "publish_date": start_date_obj.strftime("%Y-%m-%d")
                    })
                    content.append({
                        "title": f"{name} - Email Reminder",
                        "type": "email",
                        "channel": "email",
                        "description": "Campaign reminder email",
                        "publish_date": (start_date_obj + timedelta(days=7)).strftime("%Y-%m-%d")
                    })
                elif channel.lower() == "social media":
                    content.append({
                        "title": f"{name} - Social Media Announcement",
                        "type": "social post",
                        "channel": "social media",
                        "description": "Initial campaign announcement post",
                        "publish_date": start_date_obj.strftime("%Y-%m-%d")
                    })
                    content.append({
                        "title": f"{name} - Social Media Update",
                        "type": "social post",
                        "channel": "social media",
                        "description": "Campaign update post",
                        "publish_date": (start_date_obj + timedelta(days=7)).strftime("%Y-%m-%d")
                    })
                elif channel.lower() == "website":
                    content.append({
                        "title": f"{name} - Website Banner",
                        "type": "website",
                        "channel": "website",
                        "description": "Campaign banner for website",
                        "publish_date": start_date_obj.strftime("%Y-%m-%d")
                    })
            
            campaign.content = content
        
        # Calculate budget allocation by channel
        budget_allocation = {}
        total_channels = len(channels)
        if total_channels > 0:
            base_allocation = budget / total_channels
            for channel in channels:
                # Adjust allocation based on channel type
                if channel.lower() == "social media":
                    budget_allocation[channel] = base_allocation * 1.2  # 20% more for social media
                elif channel.lower() == "email":
                    budget_allocation[channel] = base_allocation * 0.8  # 20% less for email
                else:
                    budget_allocation[channel] = base_allocation
            
            # Normalize to ensure total equals budget
            total_allocated = sum(budget_allocation.values())
            for channel in budget_allocation:
                budget_allocation[channel] = (budget_allocation[channel] / total_allocated) * budget
        
        return {
            "campaign_id": campaign_id,
            "campaign": campaign.dict(),
            "budget_allocation": budget_allocation,
            "management_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "planned"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class MarketingPlanGenerationInput(BaseModel):
    """Input schema for the marketing plan generation tool."""
    
    event_id: str = Field(..., description="ID of the event")
    event_details: Dict[str, Any] = Field(..., description="Event details")
    objectives: List[str] = Field(..., description="Marketing objectives")
    target_audience: List[Dict[str, Any]] = Field(..., description="Target audience segments")
    unique_selling_points: List[str] = Field(..., description="Unique selling points of the event")
    key_messages: List[str] = Field(..., description="Key messages to communicate")
    budget: float = Field(..., description="Total marketing budget")
    channels: Optional[List[Dict[str, Any]]] = Field(None, description="Marketing channels")
    campaigns: Optional[List[Dict[str, Any]]] = Field(None, description="Marketing campaigns")


class MarketingPlanGenerationTool(BaseTool):
    """Tool for generating marketing plans."""
    
    name: str = "marketing_plan_generation_tool"
    description: str = "Generate comprehensive marketing plans for the event"
    args_schema: Type[MarketingPlanGenerationInput] = MarketingPlanGenerationInput
    
    def _run(self, event_id: str, event_details: Dict[str, Any], objectives: List[str],
             target_audience: List[Dict[str, Any]], unique_selling_points: List[str],
             key_messages: List[str], budget: float, channels: Optional[List[Dict[str, Any]]] = None,
             campaigns: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Run the marketing plan generation tool.
        
        Args:
            event_id: ID of the event
            event_details: Event details
            objectives: Marketing objectives
            target_audience: Target audience segments
            unique_selling_points: Unique selling points of the event
            key_messages: Key messages to communicate
            budget: Total marketing budget
            channels: Marketing channels
            campaigns: Marketing campaigns
            
        Returns:
            Dictionary with marketing plan details
        """
        # Create channel objects
        channel_objects = []
        if channels:
            for channel_data in channels:
                channel = MarketingChannel(
                    name=channel_data.get("name", "Unknown"),
                    type=channel_data.get("type", "Unknown"),
                    target_audience=channel_data.get("target_audience", []),
                    cost=channel_data.get("cost"),
                    content_requirements=channel_data.get("content_requirements", []),
                    schedule=channel_data.get("schedule", [])
                )
                channel_objects.append(channel)
        else:
            # Create default channels if none provided
            default_channels = [
                {
                    "name": "Email Marketing",
                    "type": "email",
                    "target_audience": ["All registered attendees", "Past attendees"],
                    "cost": budget * 0.2,
                    "content_requirements": [
                        "Compelling subject line",
                        "Personalized greeting",
                        "Clear value proposition",
                        "Mobile-friendly design",
                        "Unsubscribe option"
                    ]
                },
                {
                    "name": "Social Media",
                    "type": "social media",
                    "target_audience": ["Industry professionals", "Target demographic"],
                    "cost": budget * 0.3,
                    "content_requirements": [
                        "Short, engaging posts",
                        "High-quality images",
                        "Relevant hashtags",
                        "Call to action"
                    ]
                },
                {
                    "name": "Event Website",
                    "type": "website",
                    "target_audience": ["All potential attendees", "Sponsors", "Speakers"],
                    "cost": budget * 0.25,
                    "content_requirements": [
                        "SEO-optimized content",
                        "Clear navigation",
                        "Mobile responsiveness",
                        "Fast loading time",
                        "Clear call to action"
                    ]
                },
                {
                    "name": "Print Materials",
                    "type": "print",
                    "target_audience": ["Local attendees", "Event day participants"],
                    "cost": budget * 0.15,
                    "content_requirements": [
                        "High-resolution images",
                        "Bleed area",
                        "CMYK color mode",
                        "Vector logos",
                        "Contact information"
                    ]
                }
            ]
            
            for channel_data in default_channels:
                channel = MarketingChannel(
                    name=channel_data["name"],
                    type=channel_data["type"],
                    target_audience=channel_data["target_audience"],
                    cost=channel_data["cost"],
                    content_requirements=channel_data["content_requirements"],
                    schedule=[]
                )
                channel_objects.append(channel)
        
        # Create campaign objects
        campaign_objects = []
        if campaigns:
            for campaign_data in campaigns:
                try:
                    start_date = datetime.strptime(campaign_data.get("start_date", "2023-01-01"), "%Y-%m-%d")
                    end_date = datetime.strptime(campaign_data.get("end_date", "2023-12-31"), "%Y-%m-%d")
                except ValueError:
                    start_date = datetime.now()
                    end_date = datetime.now() + timedelta(days=30)
                
                campaign = MarketingCampaign(
                    name=campaign_data.get("name", "Unknown"),
                    description=campaign_data.get("description", ""),
                    objectives=campaign_data.get("objectives", []),
                    target_audience=campaign_data.get("target_audience", []),
                    channels=campaign_data.get("channels", []),
                    start_date=start_date,
                    end_date=end_date,
                    budget=campaign_data.get("budget", 0.0),
                    content=campaign_data.get("content", [])
                )
                campaign_objects.append(campaign)
        else:
            # Create default campaigns if none provided
            event_start = None
            if "timeline_start" in event_details and event_details["timeline_start"]:
                try:
                    if isinstance(event_details["timeline_start"], str):
                        event_start = datetime.strptime(event_details["timeline_start"], "%Y-%m-%d")
                    else:
                        event_start = event_details["timeline_start"]
                except (ValueError, TypeError):
                    event_start = datetime.now() + timedelta(days=90)
            else:
                event_start = datetime.now() + timedelta(days=90)
            
            default_campaigns = [
                {
                    "name": "Early Bird Registration",
                    "description": "Campaign to drive early registrations with special pricing",
                    "objectives": ["Drive early registrations", "Generate buzz"],
                    "target_audience": ["Past attendees", "Industry professionals"],
                    "channels": ["Email", "Social Media", "Website"],
                    "start_date": (event_start - timedelta(days=90)).strftime("%Y-%m-%d"),
                    "end_date": (event_start - timedelta(days=60)).strftime("%Y-%m-%d"),
                    "budget": budget * 0.3
                },
                {
                    "name": "Speaker Announcement",
                    "description": "Campaign to announce and promote event speakers",
                    "objectives": ["Highlight speakers", "Establish event credibility"],
                    "target_audience": ["Industry professionals", "Potential attendees"],
                    "channels": ["Social Media", "Website", "Email"],
                    "start_date": (event_start - timedelta(days=60)).strftime("%Y-%m-%d"),
                    "end_date": (event_start - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "budget": budget * 0.2
                },
                {
                    "name": "Final Push",
                    "description": "Last chance to register campaign",
                    "objectives": ["Fill remaining spots", "Create urgency"],
                    "target_audience": ["Warm leads", "Industry professionals"],
                    "channels": ["Email", "Social Media", "Paid Advertising"],
                    "start_date": (event_start - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "end_date": (event_start - timedelta(days=7)).strftime("%Y-%m-%d"),
                    "budget": budget * 0.3
                },
                {
                    "name": "Event Countdown",
                    "description": "Build excitement in the days leading up to the event",
                    "objectives": ["Build excitement", "Reduce no-shows"],
                    "target_audience": ["Registered attendees"],
                    "channels": ["Email", "Social Media"],
                    "start_date": (event_start - timedelta(days=7)).strftime("%Y-%m-%d"),
                    "end_date": event_start.strftime("%Y-%m-%d"),
                    "budget": budget * 0.2
                }
            ]
            
            for campaign_data in default_campaigns:
                try:
                    start_date = datetime.strptime(campaign_data["start_date"], "%Y-%m-%d")
                    end_date = datetime.strptime(campaign_data["end_date"], "%Y-%m-%d")
                except ValueError:
                    start_date = datetime.now()
                    end_date = datetime.now() + timedelta(days=30)
                
                campaign = MarketingCampaign(
                    name=campaign_data["name"],
                    description=campaign_data["description"],
                    objectives=campaign_data["objectives"],
                    target_audience=campaign_data["target_audience"],
                    channels=campaign_data["channels"],
                    start_date=start_date,
                    end_date=end_date,
                    budget=campaign_data["budget"],
                    content=[]
                )
                campaign_objects.append(campaign)
        
        # Create content calendar
        content_calendar = []
        for campaign in campaign_objects:
            # Add campaign milestones to content calendar
            start_date = campaign.start_date
            end_date = campaign.end_date
            duration = (end_date - start_date).days
            
            # Add campaign start
            content_calendar.append({
                "date": start_date.strftime("%Y-%m-%d"),
                "type": "campaign_start",
                "campaign": campaign.name,
                "description": f"Launch of {campaign.name} campaign",
                "channels": campaign.channels
            })
            
            # Add mid-campaign update if duration is more than 7 days
            if duration > 7:
                mid_date = start_date + timedelta(days=duration // 2)
                content_calendar.append({
                    "date": mid_date.strftime("%Y-%m-%d"),
                    "type": "campaign_update",
                    "campaign": campaign.name,
                    "description": f"Mid-campaign update for {campaign.name}",
                    "channels": campaign.channels
                })
            
            # Add campaign end
            content_calendar.append({
                "date": end_date.strftime("%Y-%m-%d"),
                "type": "campaign_end",
                "campaign": campaign.name,
                "description": f"Conclusion of {campaign.name} campaign",
                "channels": campaign.channels
            })
        
        # Sort content calendar by date
        content_calendar.sort(key=lambda x: x["date"])
        
        # Create marketing timeline
        timeline = []
        
        # Add pre-event marketing phases
        event_start = None
        if "timeline_start" in event_details and event_details["timeline_start"]:
            try:
                if isinstance(event_details["timeline_start"], str):
                    event_start = datetime.strptime(event_details["timeline_start"], "%Y-%m-%d")
                else:
                    event_start = event_details["timeline_start"]
            except (ValueError, TypeError):
                event_start = datetime.now() + timedelta(days=90)
        else:
            event_start = datetime.now() + timedelta(days=90)
        
        # 3-6 months before
        timeline.append({
            "phase": "Early Planning",
            "timeframe": "3-6 months before event",
            "start_date": (event_start - timedelta(days=180)).strftime("%Y-%m-%d"),
            "end_date": (event_start - timedelta(days=90)).strftime("%Y-%m-%d"),
            "activities": [
                "Define marketing objectives and KPIs",
                "Identify target audience segments",
                "Develop branding and messaging",
                "Create marketing plan and budget",
                "Set up event website and registration"
            ]
        })
        
        # 1-3 months before
        timeline.append({
            "phase": "Promotion",
            "timeframe": "1-3 months before event",
            "start_date": (event_start - timedelta(days=90)).strftime("%Y-%m-%d"),
            "end_date": (event_start - timedelta(days=30)).strftime("%Y-%m-%d"),
            "activities": [
                "Launch early bird registration campaign",
                "Announce speakers and agenda",
                "Begin social media promotion",
                "Send initial email announcements",
                "Engage with industry partners and sponsors"
            ]
        })
        
        # 2-4 weeks before
        timeline.append({
            "phase": "Engagement",
            "timeframe": "2-4 weeks before event",
            "start_date": (event_start - timedelta(days=30)).strftime("%Y-%m-%d"),
            "end_date": (event_start - timedelta(days=14)).strftime("%Y-%m-%d"),
            "activities": [
                "Increase social media frequency",
                "Send targeted email reminders",
                "Share speaker highlights and teasers",
                "Launch final registration push",
                "Prepare on-site marketing materials"
            ]
        })
        
        # 1-2 weeks before
        timeline.append({
            "phase": "Final Push",
            "timeframe": "1-2 weeks before event",
            "start_date": (event_start - timedelta(days=14)).strftime("%Y-%m-%d"),
            "end_date": (event_start - timedelta(days=1)).strftime("%Y-%m-%d"),
            "activities": [
                "Send final reminders and logistics information",
                "Create excitement with countdown posts",
                "Prepare attendee communications",
                "Brief team on on-site marketing activities",
                "Finalize media partnerships and coverage"
            ]
        })
        
        # During event
        timeline.append({
            "phase": "During Event",
            "timeframe": "Event days",
            "start_date": event_start.strftime("%Y-%m-%d"),
            "end_date": event_start.strftime("%Y-%m-%d"),  # Assuming 1-day event; adjust as needed
            "activities": [
                "Live social media coverage",
                "Attendee engagement activities",
                "Media interviews and press releases",
                "Photo and video documentation",
                "Collect testimonials and feedback"
            ]
        })
        
        # Post-event
        timeline.append({
            "phase": "Post-Event",
            "timeframe": "1-4 weeks after event",
            "start_date": (event_start + timedelta(days=1)).strftime("%Y-%m-%d"),
            "end_date": (event_start + timedelta(days=28)).strftime("%Y-%m-%d"),
            "activities": [
                "Send thank you communications",
                "Share event highlights and success stories",
                "Distribute recordings and materials",
                "Collect and analyze feedback",
                "Begin planning for next event"
            ]
        })
        
        # Create success metrics
        metrics = {
            "registration": {
                "total_registrations": {
                    "target": event_details.get("attendee_count", 100),
                    "actual": 0
                },
                "conversion_rate": {
                    "target": 0.05,  # 5% of website visitors
                    "actual": 0
                },
                "early_bird_registrations": {
                    "target": event_details.get("attendee_count", 100) * 0.4,  # 40% of total
                    "actual": 0
                }
            },
            "engagement": {
                "email_open_rate": {
                    "target": 0.25,  # 25%
                    "actual": 0
                },
                "email_click_rate": {
                    "target": 0.05,  # 5%
                    "actual": 0
                },
                "social_media_engagement": {
                    "target": 0.03,  # 3% engagement rate
                    "actual": 0
                },
                "website_visits": {
                    "target": event_details.get("attendee_count", 100) * 10,  # 10x attendees
                    "actual": 0
                }
            },
            "roi": {
                "cost_per_acquisition": {
                    "target": budget / event_details.get("attendee_count", 100),
                    "actual": 0
                },
                "marketing_roi": {
                    "target": 3.0,  # 3x return
                    "actual": 0
                }
            },
            "satisfaction": {
                "net_promoter_score": {
                    "target": 8.0,  # Out of 10
                    "actual": 0
                },
                "attendee_satisfaction": {
                    "target": 0.9,  # 90%
                    "actual": 0
                }
            }
        }
        
        # Create the marketing plan
        marketing_plan = MarketingPlan(
            event_id=event_id,
            objectives=objectives,
            target_audience=target_audience,
            unique_selling_points=unique_selling_points,
            key_messages=key_messages,
            branding={
                "name": event_details.get("title", "Event"),
                "tagline": f"The premier {event_details.get('event_type', 'event')} for industry professionals",
                "color_scheme": ["#007BFF", "#6C757D", "#28A745", "#FFC107"],
                "typography": {
                    "headings": "Montserrat, sans-serif",
                    "body": "Open Sans, sans-serif"
                },
                "logo": "event_logo.png",
                "voice_and_tone": "Professional, engaging, and authoritative"
            },
            channels=channel_objects,
            campaigns=campaign_objects,
            content_calendar=content_calendar,
            budget={
                "total_amount": budget,
                "allocation": {
                    "digital_marketing": budget * 0.4,
                    "print_materials": budget * 0.15,
                    "event_promotion": budget * 0.25,
                    "public_relations": budget * 0.1,
                    "contingency": budget * 0.1
                }
            },
            timeline=timeline,
            metrics=metrics,
            approval_status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return {
            "marketing_plan": marketing_plan.dict(),
            "management_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "draft"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class CommunicationPlanGenerationInput(BaseModel):
    """Input schema for the communication plan generation tool."""
    
    event_id: str = Field(..., description="ID of the event")
    event_details: Dict[str, Any] = Field(..., description="Event details")
    stakeholder_groups: List[Dict[str, Any]] = Field(..., description="Stakeholder groups")
    communication_objectives: List[str] = Field(..., description="Communication objectives")
    key_messages: Dict[str, List[str]] = Field(..., description="Key messages by stakeholder group")


class CommunicationPlanGenerationTool(BaseTool):
    """Tool for generating communication plans."""
    
    name: str = "communication_plan_generation_tool"
    description: str = "Generate comprehensive communication plans for the event"
    args_schema: Type[CommunicationPlanGenerationInput] = CommunicationPlanGenerationInput
    
    def _run(self, event_id: str, event_details: Dict[str, Any], stakeholder_groups: List[Dict[str, Any]],
             communication_objectives: List[str], key_messages: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Run the communication plan generation tool.
        
        Args:
            event_id: ID of the event
            event_details: Event details
            stakeholder_groups: Stakeholder groups
            communication_objectives: Communication objectives
            key_messages: Key messages by stakeholder group
            
        Returns:
            Dictionary with communication plan details
        """
        # Define communication channels for each stakeholder group
        channels = {}
        for group in stakeholder_groups:
            group_name = group.get("name", "Unknown")
            group_type = group.get("type", "general").lower()
            
            if group_type == "attendees":
                channels[group_name] = ["Email", "Mobile App", "Social Media", "Website"]
            elif group_type == "speakers":
                channels[group_name] = ["Email", "Phone", "Private Portal", "Briefing Sessions"]
            elif group_type == "sponsors":
                channels[group_name] = ["Email", "Phone", "In-person Meetings", "Sponsor Portal"]
            elif group_type == "media":
                channels[group_name] = ["Email", "Press Releases", "Media Kit", "Press Conferences"]
            elif group_type == "staff":
                channels[group_name] = ["Email", "Team Meetings", "Collaboration Tools", "Training Sessions"]
            elif group_type == "vendors":
                channels[group_name] = ["Email", "Phone", "Contracts", "Briefing Documents"]
            else:
                channels[group_name] = ["Email", "Website", "Social Media"]
        
        # Create communication schedule
        schedule = []
        
        # Determine event dates
        event_start = None
        event_end = None
        if "timeline_start" in event_details and event_details["timeline_start"]:
            try:
                if isinstance(event_details["timeline_start"], str):
                    event_start = datetime.strptime(event_details["timeline_start"], "%Y-%m-%d")
                else:
                    event_start = event_details["timeline_start"]
            except (ValueError, TypeError):
                event_start = datetime.now() + timedelta(days=90)
        else:
            event_start = datetime.now() + timedelta(days=90)
        
        if "timeline_end" in event_details and event_details["timeline_end"]:
            try:
                if isinstance(event_details["timeline_end"], str):
                    event_end = datetime.strptime(event_details["timeline_end"], "%Y-%m-%d")
                else:
                    event_end = event_details["timeline_end"]
            except (ValueError, TypeError):
                event_end = event_start + timedelta(days=1)
        else:
            event_end = event_start + timedelta(days=1)
        
        # Pre-event communications (3 months before)
        for group in stakeholder_groups:
            group_name = group.get("name", "Unknown")
            
            # Initial announcement
            schedule.append({
                "date": (event_start - timedelta(days=90)).strftime("%Y-%m-%d"),
                "stakeholder_group": group_name,
                "communication_type": "Initial Announcement",
                "channels": channels[group_name][:2],  # Use first two channels
                "key_messages": key_messages.get(group_name, ["Event announcement"])[:2],
                "purpose": "Announce event and key details"
            })
            
            # Regular updates
            for i in range(1, 3):  # 2 updates
                schedule.append({
                    "date": (event_start - timedelta(days=90-i*30)).strftime("%Y-%m-%d"),
                    "stakeholder_group": group_name,
                    "communication_type": f"Update {i}",
                    "channels": channels[group_name][:2],  # Use first two channels
                    "key_messages": key_messages.get(group_name, ["Event update"])[:2],
                    "purpose": "Provide updates on event planning"
                })
        
        # Pre-event communications (1 month before)
        for group in stakeholder_groups:
            group_name = group.get("name", "Unknown")
            
            # Detailed information
            schedule.append({
                "date": (event_start - timedelta(days=30)).strftime("%Y-%m-%d"),
                "stakeholder_group": group_name,
                "communication_type": "Detailed Information",
                "channels": channels[group_name],  # Use all channels
                "key_messages": key_messages.get(group_name, ["Event details"]),
                "purpose": "Provide detailed information about the event"
            })
            
            # Final reminder
            schedule.append({
                "date": (event_start - timedelta(days=7)).strftime("%Y-%m-%d"),
                "stakeholder_group": group_name,
                "communication_type": "Final Reminder",
                "channels": channels[group_name],  # Use all channels
                "key_messages": key_messages.get(group_name, ["Event reminder"]),
                "purpose": "Remind stakeholders about the upcoming event"
            })
        
        # During event communications
        for group in stakeholder_groups:
            group_name = group.get("name", "Unknown")
            
            # Day-of communications
            schedule.append({
                "date": event_start.strftime("%Y-%m-%d"),
                "stakeholder_group": group_name,
                "communication_type": "Day-of Communication",
                "channels": channels[group_name],  # Use all channels
                "key_messages": key_messages.get(group_name, ["Event day information"]),
                "purpose": "Provide day-of information and support"
            })
        
        # Post-event communications
        for group in stakeholder_groups:
            group_name = group.get("name", "Unknown")
            
            # Thank you and feedback
            schedule.append({
                "date": (event_end + timedelta(days=1)).strftime("%Y-%m-%d"),
                "stakeholder_group": group_name,
                "communication_type": "Thank You",
                "channels": channels[group_name][:2],  # Use first two channels
                "key_messages": key_messages.get(group_name, ["Thank you"]),
                "purpose": "Thank stakeholders and request feedback"
            })
            
            # Follow-up
            schedule.append({
                "date": (event_end + timedelta(days=7)).strftime("%Y-%m-%d"),
                "stakeholder_group": group_name,
                "communication_type": "Follow-up",
                "channels": channels[group_name][:2],  # Use first two channels
                "key_messages": key_messages.get(group_name, ["Event follow-up"]),
                "purpose": "Provide event highlights and next steps"
            })
        
        # Sort schedule by date
        schedule.sort(key=lambda x: x["date"])
        
        # Create communication templates
        templates = {
            "initial_announcement": "Dear {stakeholder},\n\nWe are excited to announce {event_title}, taking place on {event_date} at {event_location}. {event_description}\n\nMark your calendar and stay tuned for more information.\n\nBest regards,\nThe Event Team",
            "update": "Dear {stakeholder},\n\nHere's an update on {event_title}:\n\n{update_details}\n\nFor more information, visit our website at {website_url}.\n\nBest regards,\nThe Event Team",
            "detailed_information": "Dear {stakeholder},\n\nAs we approach {event_title}, we want to provide you with detailed information:\n\n{detailed_information}\n\nIf you have any questions, please contact us at {contact_email}.\n\nBest regards,\nThe Event Team",
            "final_reminder": "Dear {stakeholder},\n\n{event_title} is just around the corner! Here's everything you need to know:\n\n{reminder_details}\n\nWe look forward to seeing you there!\n\nBest regards,\nThe Event Team",
            "day_of": "Dear {stakeholder},\n\nToday is the day! {event_title} begins at {start_time}.\n\n{day_of_details}\n\nSee you soon!\n\nBest regards,\nThe Event Team",
            "thank_you": "Dear {stakeholder},\n\nThank you for being part of {event_title}. We hope you had a great experience.\n\n{thank_you_message}\n\nPlease take a moment to provide feedback: {feedback_link}\n\nBest regards,\nThe Event Team",
            "follow_up": "Dear {stakeholder},\n\nThank you again for being part of {event_title}. Here are some highlights from the event:\n\n{highlights}\n\nStay tuned for information about our next event!\n\nBest regards,\nThe Event Team"
        }
        
        # Create feedback mechanisms
        feedback_mechanisms = [
            {
                "type": "Post-event survey",
                "target_groups": [group.get("name", "Unknown") for group in stakeholder_groups],
                "timing": "1 day after event",
                "method": "Email with survey link",
                "questions": [
                    "How would you rate your overall experience?",
                    "What did you like most about the event?",
                    "What could we improve for future events?",
                    "Would you recommend this event to others?",
                    "Any additional comments or suggestions?"
                ]
            },
            {
                "type": "Social media monitoring",
                "target_groups": ["Attendees", "General public"],
                "timing": "Before, during, and after event",
                "method": "Social listening tools",
                "metrics": [
                    "Sentiment analysis",
                    "Engagement rates",
                    "Reach and impressions",
                    "Common themes and topics"
                ]
            },
            {
                "type": "Stakeholder interviews",
                "target_groups": ["Speakers", "Sponsors", "VIPs"],
                "timing": "1-2 weeks after event",
                "method": "Phone or video calls",
                "questions": [
                    "How was your experience as a {stakeholder_type}?",
                    "What worked well from your perspective?",
                    "What could we improve for future events?",
                    "Would you participate in future events?",
                    "Any additional feedback or suggestions?"
                ]
            }
        ]
        
        # Create crisis communication plan
        crisis_communication = {
            "crisis_team": [
                {"role": "Crisis Lead", "responsibilities": "Overall coordination and decision-making"},
                {"role": "Communications Manager", "responsibilities": "Message development and distribution"},
                {"role": "Stakeholder Liaison", "responsibilities": "Direct communication with affected stakeholders"},
                {"role": "Legal Advisor", "responsibilities": "Legal guidance and review of communications"},
                {"role": "Operations Manager", "responsibilities": "Logistical support and venue coordination"}
            ],
            "crisis_scenarios": [
                {
                    "type": "Event cancellation",
                    "response_steps": [
                        "Confirm cancellation details with leadership",
                        "Prepare official statement with reason for cancellation",
                        "Notify all stakeholders through multiple channels",
                        "Update website and social media",
                        "Provide information about refunds or alternatives",
                        "Set up dedicated support channels for questions"
                    ],
                    "communication_templates": {
                        "email": "Dear {stakeholder},\n\nWe regret to inform you that {event_title} has been cancelled due to {reason}. {additional_details}\n\nInformation regarding {refunds/alternatives} will be provided shortly.\n\nWe sincerely apologize for any inconvenience this may cause.\n\nIf you have any questions, please contact us at {contact_email}.\n\nBest regards,\nThe Event Team",
                        "social_media": "ANNOUNCEMENT: {event_title} has been cancelled due to {reason}. Details regarding {refunds/alternatives} will be provided shortly. We apologize for any inconvenience. For questions, please contact {contact_email}."
                    }
                },
                {
                    "type": "Venue change",
                    "response_steps": [
                        "Confirm new venue details",
                        "Prepare announcement with reason for change",
                        "Notify all stakeholders with new location information",
                        "Update website, registration system, and maps",
                        "Provide transportation options and directions",
                        "Set up signage at original venue directing to new location"
                    ],
                    "communication_templates": {
                        "email": "Dear {stakeholder},\n\nPlease note that {event_title} has been moved to a new venue: {new_venue_name}, located at {new_venue_address}. This change is due to {reason}.\n\n{additional_details_and_directions}\n\nIf you have any questions, please contact us at {contact_email}.\n\nBest regards,\nThe Event Team",
                        "social_media": "VENUE CHANGE: {event_title} will now take place at {new_venue_name}. See our website for details and directions. For questions, please contact {contact_email}."
                    }
                },
                {
                    "type": "Security incident",
                    "response_steps": [
                        "Ensure immediate safety of all attendees",
                        "Coordinate with security and emergency services",
                        "Prepare factual statement with verified information only",
                        "Designate single spokesperson for consistency",
                        "Provide regular updates as situation evolves",
                        "Offer support resources for affected individuals"
                    ],
                    "communication_templates": {
                        "email": "Dear {stakeholder},\n\nWe want to inform you about a security incident that occurred at {event_title}. {factual_description}\n\nThe safety of our attendees is our top priority, and we are working closely with {authorities} to address the situation.\n\n{status_update_and_next_steps}\n\nIf you have any concerns, please contact us at {contact_email}.\n\nBest regards,\nThe Event Team",
                        "social_media": "SECURITY UPDATE: We are addressing a security incident at {event_title}. All attendees are {status}. We are working with authorities and will provide updates as available."
                    }
                }
            ],
            "communication_channels_priority": [
                {"channel": "Email", "purpose": "Detailed information to all stakeholders"},
                {"channel": "SMS/Text", "purpose": "Urgent notifications and updates"},
                {"channel": "Website", "purpose": "Central information hub with all details"},
                {"channel": "Social Media", "purpose": "Real-time updates and public information"},
                {"channel": "Phone", "purpose": "Direct communication with key stakeholders"}
            ],
            "post_crisis_steps": [
                "Conduct thorough assessment of crisis response",
                "Provide comprehensive update to all stakeholders",
                "Implement recovery plan and communicate next steps",
                "Gather feedback on crisis communication effectiveness",
                "Update crisis communication plan based on lessons learned"
            ]
        }
        
        # Create the communication plan
        communication_plan = CommunicationPlan(
            event_id=event_id,
            stakeholder_groups=stakeholder_groups,
            communication_objectives=communication_objectives,
            key_messages=key_messages,
            channels=channels,
            schedule=schedule,
            templates=templates,
            feedback_mechanisms=feedback_mechanisms,
            crisis_communication=crisis_communication,
            approval_status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return {
            "communication_plan": communication_plan.dict(),
            "management_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "draft"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)
