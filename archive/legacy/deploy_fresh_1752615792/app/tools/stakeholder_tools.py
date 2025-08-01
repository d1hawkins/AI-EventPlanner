from typing import Dict, Any, List, Optional, Type
from datetime import datetime, timedelta
import uuid

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.schemas.stakeholder import Speaker, Sponsor, Volunteer, VIP, StakeholderPlan


class SpeakerManagementInput(BaseModel):
    """Input schema for the speaker management tool."""
    
    name: str = Field(..., description="Name of the speaker")
    role: str = Field(..., description="Role or title of the speaker")
    topic: str = Field(..., description="Topic or presentation title")
    bio: Optional[str] = Field(None, description="Speaker biography")
    contact_info: Optional[str] = Field(None, description="Contact information")
    requirements: Optional[List[str]] = Field(None, description="Speaker requirements")
    confirmed: bool = Field(False, description="Whether the speaker is confirmed")
    presentation_time: Optional[str] = Field(None, description="Scheduled presentation time (YYYY-MM-DD HH:MM)")


class SpeakerManagementTool(BaseTool):
    """Tool for managing speakers."""
    
    name: str = "speaker_management_tool"
    description: str = "Manage speakers for the event"
    args_schema: Type[SpeakerManagementInput] = SpeakerManagementInput
    
    def _run(self, name: str, role: str, topic: str, 
             bio: Optional[str] = None, contact_info: Optional[str] = None,
             requirements: Optional[List[str]] = None, confirmed: bool = False,
             presentation_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the speaker management tool.
        
        Args:
            name: Name of the speaker
            role: Role or title of the speaker
            topic: Topic or presentation title
            bio: Speaker biography
            contact_info: Contact information
            requirements: Speaker requirements
            confirmed: Whether the speaker is confirmed
            presentation_time: Scheduled presentation time
            
        Returns:
            Dictionary with speaker details
        """
        # Parse presentation time if provided
        presentation_time_obj = None
        if presentation_time:
            try:
                presentation_time_obj = datetime.strptime(presentation_time, "%Y-%m-%d %H:%M")
            except ValueError:
                # If date parsing fails, use None
                pass
        
        # Create a Speaker object
        speaker = Speaker(
            name=name,
            role=role,
            topic=topic,
            bio=bio,
            contact_info=contact_info,
            requirements=requirements or [],
            confirmed=confirmed,
            presentation_time=presentation_time_obj
        )
        
        # Generate a unique ID for the speaker
        speaker_id = str(uuid.uuid4())
        
        return {
            "speaker_id": speaker_id,
            "speaker": speaker.dict(),
            "management_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "added" if confirmed else "pending"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class SponsorManagementInput(BaseModel):
    """Input schema for the sponsor management tool."""
    
    name: str = Field(..., description="Name of the sponsor")
    level: str = Field(..., description="Sponsorship level (e.g., Gold, Silver, Bronze)")
    contribution: float = Field(..., description="Sponsorship contribution amount")
    benefits: List[str] = Field(..., description="Benefits provided to the sponsor")
    contact_person: str = Field(..., description="Primary contact person")
    contact_info: str = Field(..., description="Contact information")
    logo_url: Optional[str] = Field(None, description="URL to sponsor logo")
    confirmed: bool = Field(False, description="Whether the sponsor is confirmed")


class SponsorManagementTool(BaseTool):
    """Tool for managing sponsors."""
    
    name: str = "sponsor_management_tool"
    description: str = "Manage sponsors for the event"
    args_schema: Type[SponsorManagementInput] = SponsorManagementInput
    
    def _run(self, name: str, level: str, contribution: float,
             benefits: List[str], contact_person: str, contact_info: str,
             logo_url: Optional[str] = None, confirmed: bool = False) -> Dict[str, Any]:
        """
        Run the sponsor management tool.
        
        Args:
            name: Name of the sponsor
            level: Sponsorship level
            contribution: Sponsorship contribution amount
            benefits: Benefits provided to the sponsor
            contact_person: Primary contact person
            contact_info: Contact information
            logo_url: URL to sponsor logo
            confirmed: Whether the sponsor is confirmed
            
        Returns:
            Dictionary with sponsor details
        """
        # Create a Sponsor object
        sponsor = Sponsor(
            name=name,
            level=level,
            contribution=contribution,
            benefits=benefits,
            contact_person=contact_person,
            contact_info=contact_info,
            logo_url=logo_url,
            confirmed=confirmed
        )
        
        # Generate a unique ID for the sponsor
        sponsor_id = str(uuid.uuid4())
        
        # Generate standard benefits based on level if not provided
        if not benefits:
            if level.lower() == "gold":
                benefits = [
                    "Logo on main stage",
                    "Logo on website",
                    "Logo on all marketing materials",
                    "Booth at event",
                    "5 free tickets",
                    "Speaking opportunity"
                ]
            elif level.lower() == "silver":
                benefits = [
                    "Logo on website",
                    "Logo on marketing materials",
                    "Booth at event",
                    "3 free tickets"
                ]
            elif level.lower() == "bronze":
                benefits = [
                    "Logo on website",
                    "1 free ticket"
                ]
            else:
                benefits = ["Logo on website"]
        
        return {
            "sponsor_id": sponsor_id,
            "sponsor": sponsor.dict(),
            "management_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "confirmed" if confirmed else "pending"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class VolunteerManagementInput(BaseModel):
    """Input schema for the volunteer management tool."""
    
    name: str = Field(..., description="Name of the volunteer")
    role: str = Field(..., description="Assigned role")
    skills: List[str] = Field(..., description="Relevant skills")
    availability: List[str] = Field(..., description="Availability times")
    contact_info: str = Field(..., description="Contact information")
    assigned_tasks: Optional[List[str]] = Field(None, description="Assigned tasks")
    confirmed: bool = Field(False, description="Whether the volunteer is confirmed")


class VolunteerManagementTool(BaseTool):
    """Tool for managing volunteers."""
    
    name: str = "volunteer_management_tool"
    description: str = "Manage volunteers for the event"
    args_schema: Type[VolunteerManagementInput] = VolunteerManagementInput
    
    def _run(self, name: str, role: str, skills: List[str],
             availability: List[str], contact_info: str,
             assigned_tasks: Optional[List[str]] = None,
             confirmed: bool = False) -> Dict[str, Any]:
        """
        Run the volunteer management tool.
        
        Args:
            name: Name of the volunteer
            role: Assigned role
            skills: Relevant skills
            availability: Availability times
            contact_info: Contact information
            assigned_tasks: Assigned tasks
            confirmed: Whether the volunteer is confirmed
            
        Returns:
            Dictionary with volunteer details
        """
        # Create a Volunteer object
        volunteer = Volunteer(
            name=name,
            role=role,
            skills=skills,
            availability=availability,
            contact_info=contact_info,
            assigned_tasks=assigned_tasks or [],
            confirmed=confirmed
        )
        
        # Generate a unique ID for the volunteer
        volunteer_id = str(uuid.uuid4())
        
        # Suggest tasks based on role and skills if not provided
        if not assigned_tasks:
            if role.lower() == "registration":
                assigned_tasks = [
                    "Check in attendees",
                    "Distribute badges and materials",
                    "Answer attendee questions"
                ]
            elif role.lower() == "technical support":
                assigned_tasks = [
                    "Set up AV equipment",
                    "Assist speakers with presentations",
                    "Troubleshoot technical issues"
                ]
            elif role.lower() == "hospitality":
                assigned_tasks = [
                    "Greet attendees",
                    "Direct attendees to sessions",
                    "Assist with refreshments"
                ]
            else:
                assigned_tasks = ["General assistance"]
        
        return {
            "volunteer_id": volunteer_id,
            "volunteer": volunteer.dict(),
            "management_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "confirmed" if confirmed else "pending"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class VIPManagementInput(BaseModel):
    """Input schema for the VIP management tool."""
    
    name: str = Field(..., description="Name of the VIP")
    organization: str = Field(..., description="Organization or company")
    role: str = Field(..., description="Role or title")
    special_requirements: Optional[List[str]] = Field(None, description="Special requirements or accommodations")
    contact_info: str = Field(..., description="Contact information")
    confirmed: bool = Field(False, description="Whether the VIP is confirmed")


class VIPManagementTool(BaseTool):
    """Tool for managing VIP attendees."""
    
    name: str = "vip_management_tool"
    description: str = "Manage VIP attendees for the event"
    args_schema: Type[VIPManagementInput] = VIPManagementInput
    
    def _run(self, name: str, organization: str, role: str,
             contact_info: str, special_requirements: Optional[List[str]] = None,
             confirmed: bool = False) -> Dict[str, Any]:
        """
        Run the VIP management tool.
        
        Args:
            name: Name of the VIP
            organization: Organization or company
            role: Role or title
            contact_info: Contact information
            special_requirements: Special requirements or accommodations
            confirmed: Whether the VIP is confirmed
            
        Returns:
            Dictionary with VIP details
        """
        # Create a VIP object
        vip = VIP(
            name=name,
            organization=organization,
            role=role,
            contact_info=contact_info,
            special_requirements=special_requirements or [],
            confirmed=confirmed
        )
        
        # Generate a unique ID for the VIP
        vip_id = str(uuid.uuid4())
        
        # Generate standard VIP accommodations if not provided
        if not special_requirements:
            special_requirements = [
                "Reserved seating",
                "VIP lounge access",
                "Dedicated concierge",
                "Priority registration"
            ]
        
        return {
            "vip_id": vip_id,
            "vip": vip.dict(),
            "management_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "confirmed" if confirmed else "pending"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class StakeholderPlanGenerationInput(BaseModel):
    """Input schema for the stakeholder plan generation tool."""
    
    event_id: str = Field(..., description="ID of the event")
    event_details: Dict[str, Any] = Field(..., description="Event details")
    speakers: List[Dict[str, Any]] = Field(default_factory=list, description="Event speakers")
    sponsors: List[Dict[str, Any]] = Field(default_factory=list, description="Event sponsors")
    volunteers: List[Dict[str, Any]] = Field(default_factory=list, description="Event volunteers")
    vips: List[Dict[str, Any]] = Field(default_factory=list, description="VIP attendees")


class StakeholderPlanGenerationTool(BaseTool):
    """Tool for generating a comprehensive stakeholder management plan."""
    
    name: str = "stakeholder_plan_generation_tool"
    description: str = "Generate a comprehensive stakeholder management plan for an event"
    args_schema: Type[StakeholderPlanGenerationInput] = StakeholderPlanGenerationInput
    
    def _run(self, event_id: str, event_details: Dict[str, Any],
             speakers: List[Dict[str, Any]] = None,
             sponsors: List[Dict[str, Any]] = None,
             volunteers: List[Dict[str, Any]] = None,
             vips: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the stakeholder plan generation tool.
        
        Args:
            event_id: ID of the event
            event_details: Event details
            speakers: Event speakers
            sponsors: Event sponsors
            volunteers: Event volunteers
            vips: VIP attendees
            
        Returns:
            Dictionary with stakeholder management plan
        """
        # Initialize empty lists if not provided
        speakers = speakers or []
        sponsors = sponsors or []
        volunteers = volunteers or []
        vips = vips or []
        
        # Create speaker objects
        speaker_objects = []
        for speaker_data in speakers:
            # Parse presentation time if provided
            presentation_time_obj = None
            if "presentation_time" in speaker_data and speaker_data["presentation_time"]:
                try:
                    if isinstance(speaker_data["presentation_time"], str):
                        presentation_time_obj = datetime.strptime(speaker_data["presentation_time"], "%Y-%m-%d %H:%M")
                    else:
                        presentation_time_obj = speaker_data["presentation_time"]
                except (ValueError, TypeError):
                    pass
            
            speaker = Speaker(
                name=speaker_data.get("name", "Unknown"),
                role=speaker_data.get("role", "Speaker"),
                topic=speaker_data.get("topic", "TBD"),
                bio=speaker_data.get("bio"),
                contact_info=speaker_data.get("contact_info"),
                requirements=speaker_data.get("requirements", []),
                confirmed=speaker_data.get("confirmed", False),
                presentation_time=presentation_time_obj
            )
            speaker_objects.append(speaker)
        
        # Create sponsor objects
        sponsor_objects = []
        for sponsor_data in sponsors:
            sponsor = Sponsor(
                name=sponsor_data.get("name", "Unknown"),
                level=sponsor_data.get("level", "Standard"),
                contribution=sponsor_data.get("contribution", 0.0),
                benefits=sponsor_data.get("benefits", []),
                contact_person=sponsor_data.get("contact_person", "Unknown"),
                contact_info=sponsor_data.get("contact_info", "Unknown"),
                logo_url=sponsor_data.get("logo_url"),
                confirmed=sponsor_data.get("confirmed", False)
            )
            sponsor_objects.append(sponsor)
        
        # Create volunteer objects
        volunteer_objects = []
        for volunteer_data in volunteers:
            volunteer = Volunteer(
                name=volunteer_data.get("name", "Unknown"),
                role=volunteer_data.get("role", "General"),
                skills=volunteer_data.get("skills", []),
                availability=volunteer_data.get("availability", []),
                contact_info=volunteer_data.get("contact_info", "Unknown"),
                assigned_tasks=volunteer_data.get("assigned_tasks", []),
                confirmed=volunteer_data.get("confirmed", False)
            )
            volunteer_objects.append(volunteer)
        
        # Create VIP objects
        vip_objects = []
        for vip_data in vips:
            vip = VIP(
                name=vip_data.get("name", "Unknown"),
                organization=vip_data.get("organization", "Unknown"),
                role=vip_data.get("role", "VIP"),
                special_requirements=vip_data.get("special_requirements", []),
                contact_info=vip_data.get("contact_info", "Unknown"),
                confirmed=vip_data.get("confirmed", False)
            )
            vip_objects.append(vip)
        
        # Create communication schedule
        # Get event start date
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
        
        # Create communication milestones
        communication_schedule = [
            {
                "stakeholder_type": "speakers",
                "communication_type": "Initial Outreach",
                "date": (event_start - timedelta(days=120)).strftime("%Y-%m-%d"),
                "content": "Initial invitation to speak at the event",
                "status": "pending"
            },
            {
                "stakeholder_type": "speakers",
                "communication_type": "Confirmation",
                "date": (event_start - timedelta(days=90)).strftime("%Y-%m-%d"),
                "content": "Confirmation of participation and topic",
                "status": "pending"
            },
            {
                "stakeholder_type": "speakers",
                "communication_type": "Requirements Collection",
                "date": (event_start - timedelta(days=60)).strftime("%Y-%m-%d"),
                "content": "Collection of technical requirements and preferences",
                "status": "pending"
            },
            {
                "stakeholder_type": "speakers",
                "communication_type": "Final Details",
                "date": (event_start - timedelta(days=14)).strftime("%Y-%m-%d"),
                "content": "Final schedule and logistics information",
                "status": "pending"
            },
            {
                "stakeholder_type": "sponsors",
                "communication_type": "Initial Outreach",
                "date": (event_start - timedelta(days=180)).strftime("%Y-%m-%d"),
                "content": "Initial sponsorship proposal",
                "status": "pending"
            },
            {
                "stakeholder_type": "sponsors",
                "communication_type": "Agreement",
                "date": (event_start - timedelta(days=120)).strftime("%Y-%m-%d"),
                "content": "Sponsorship agreement and payment details",
                "status": "pending"
            },
            {
                "stakeholder_type": "sponsors",
                "communication_type": "Materials Collection",
                "date": (event_start - timedelta(days=60)).strftime("%Y-%m-%d"),
                "content": "Collection of logos and marketing materials",
                "status": "pending"
            },
            {
                "stakeholder_type": "sponsors",
                "communication_type": "Final Details",
                "date": (event_start - timedelta(days=14)).strftime("%Y-%m-%d"),
                "content": "Final logistics and setup information",
                "status": "pending"
            },
            {
                "stakeholder_type": "volunteers",
                "communication_type": "Recruitment",
                "date": (event_start - timedelta(days=60)).strftime("%Y-%m-%d"),
                "content": "Volunteer recruitment and role descriptions",
                "status": "pending"
            },
            {
                "stakeholder_type": "volunteers",
                "communication_type": "Assignment",
                "date": (event_start - timedelta(days=30)).strftime("%Y-%m-%d"),
                "content": "Role assignments and schedule",
                "status": "pending"
            },
            {
                "stakeholder_type": "volunteers",
                "communication_type": "Training",
                "date": (event_start - timedelta(days=7)).strftime("%Y-%m-%d"),
                "content": "Volunteer training and final instructions",
                "status": "pending"
            },
            {
                "stakeholder_type": "vips",
                "communication_type": "Initial Invitation",
                "date": (event_start - timedelta(days=90)).strftime("%Y-%m-%d"),
                "content": "VIP invitation with event details",
                "status": "pending"
            },
            {
                "stakeholder_type": "vips",
                "communication_type": "Confirmation",
                "date": (event_start - timedelta(days=60)).strftime("%Y-%m-%d"),
                "content": "Confirmation of attendance and special requirements",
                "status": "pending"
            },
            {
                "stakeholder_type": "vips",
                "communication_type": "Final Details",
                "date": (event_start - timedelta(days=7)).strftime("%Y-%m-%d"),
                "content": "Final logistics and VIP experience details",
                "status": "pending"
            }
        ]
        
        # Create engagement strategies
        engagement_strategies = {
            "speakers": [
                "Personalized outreach highlighting event relevance to their expertise",
                "Offer professional recording of their presentation",
                "Provide speaker networking opportunities",
                "Share audience demographics and interests",
                "Offer travel and accommodation assistance"
            ],
            "sponsors": [
                "Tiered sponsorship packages with clear ROI metrics",
                "Exclusive networking opportunities with key attendees",
                "Custom sponsorship options for specific needs",
                "Post-event analytics and lead generation reports",
                "Early bird discounts for returning sponsors"
            ],
            "volunteers": [
                "Clear role descriptions with specific time commitments",
                "Training and skill development opportunities",
                "Recognition program for outstanding volunteers",
                "Event attendance perks during off-duty hours",
                "Post-event appreciation and networking event"
            ],
            "vips": [
                "Personalized invitations from event leadership",
                "Exclusive VIP lounge and networking opportunities",
                "Dedicated concierge service during the event",
                "Special access to speakers and key stakeholders",
                "Customized event experience based on interests"
            ]
        }
        
        # Create a StakeholderPlan object
        stakeholder_plan = StakeholderPlan(
            event_id=event_id,
            speakers=speaker_objects,
            sponsors=sponsor_objects,
            volunteers=volunteer_objects,
            vips=vip_objects,
            communication_schedule=communication_schedule,
            engagement_strategies=engagement_strategies,
            approval_status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Generate a stakeholder plan summary
        summary = f"""
Stakeholder Management Plan for {event_details.get('title', 'Event')}

Stakeholder Summary:
- Speakers: {len(speaker_objects)} ({len([s for s in speaker_objects if s.confirmed])} confirmed)
- Sponsors: {len(sponsor_objects)} ({len([s for s in sponsor_objects if s.confirmed])} confirmed)
- Volunteers: {len(volunteer_objects)} ({len([v for v in volunteer_objects if v.confirmed])} confirmed)
- VIPs: {len(vip_objects)} ({len([v for v in vip_objects if v.confirmed])} confirmed)

Communication Schedule:
{chr(10).join([f"- {comm['date']}: {comm['stakeholder_type']} - {comm['communication_type']}" for comm in communication_schedule[:5]])}
... and {len(communication_schedule) - 5} more communications scheduled

Key Engagement Strategies:
- Speakers: Personalized outreach, professional recording, networking opportunities
- Sponsors: Tiered packages with ROI metrics, exclusive networking, custom options
- Volunteers: Clear roles, training opportunities, recognition program
- VIPs: Personalized invitations, exclusive access, dedicated concierge service

This stakeholder management plan was generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        return {
            "stakeholder_plan": stakeholder_plan.dict(),
            "summary": summary,
            "communication_schedule": communication_schedule,
            "engagement_strategies": engagement_strategies,
            "generation_details": {
                "created_at": datetime.now().isoformat(),
                "status": "draft",
                "next_steps": "Review stakeholder plan and submit for approval"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)
