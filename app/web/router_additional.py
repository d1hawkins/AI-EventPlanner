"""
Additional API endpoints for templates, notifications, and user profile.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.db.models import User
from app.db.models_saas import EventTemplate, TemplateItem
from app.db.models_updated import Event
from app.auth.dependencies import get_current_user, get_current_user_id
from app.middleware.tenant import get_tenant_id

router = APIRouter()


# Pydantic models
class TemplateResponse(BaseModel):
    """Template response model."""
    id: int
    name: str
    description: Optional[str] = None
    event_type: Optional[str] = None
    duration_days: Optional[int] = None
    template_data: Dict[str, Any]
    is_public: bool
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    version: int
    created_at: datetime
    updated_at: datetime
    organization_id: int
    created_by: int

    class Config:
        from_attributes = True


class TemplateCreate(BaseModel):
    """Template creation model."""
    name: str
    description: Optional[str] = None
    event_type: Optional[str] = None
    duration_days: Optional[int] = None
    template_data: Dict[str, Any]
    is_public: bool = False
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class NotificationResponse(BaseModel):
    """Notification response model."""
    id: int
    title: str
    message: str
    type: str
    read: bool
    created_at: str
    link: Optional[str] = None


class UserProfileResponse(BaseModel):
    """User profile response model."""
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: bool


class EventSuggestionRequest(BaseModel):
    """Event suggestion request model."""
    prompt: str


class EventSuggestionResponse(BaseModel):
    """Event suggestion response model."""
    title: Optional[str] = None
    type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    venue: Optional[str] = None
    attendee_count: Optional[int] = None
    budget: Optional[float] = None
    description: Optional[str] = None


class EventCreateRequest(BaseModel):
    """Event creation request model."""
    title: str
    event_type: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    venue: Optional[str] = None
    attendee_count: Optional[int] = None
    budget: Optional[float] = None
    status: Optional[str] = "draft"


class EventCreateResponse(BaseModel):
    """Event creation response model."""
    id: int
    title: str
    event_type: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    attendee_count: Optional[int] = None
    budget: Optional[float] = None
    status: str
    organization_id: Optional[int] = None
    created_at: str


# Templates endpoints
@router.get("/templates", response_model=List[TemplateResponse])
async def get_templates(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get all templates for the current organization.

    Args:
        request: FastAPI request
        db: Database session
        current_user_id: Current user ID

    Returns:
        List of templates
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None

        if not organization_id:
            # Return empty list if no organization context
            return []

        # Query templates for this organization
        templates = db.query(EventTemplate).filter(
            EventTemplate.organization_id == organization_id
        ).all()

        return templates

    except Exception as e:
        print(f"Error in get_templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving templates: {str(e)}"
        )


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get a specific template by ID.

    Args:
        template_id: Template ID
        request: FastAPI request
        db: Database session
        current_user_id: Current user ID

    Returns:
        Template
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None

        # Query template
        template = db.query(EventTemplate).filter(
            EventTemplate.id == template_id
        ).first()

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        # Check access
        if organization_id and template.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return template

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving template: {str(e)}"
        )


@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Create a new template.

    Args:
        template_data: Template data
        request: FastAPI request
        db: Database session
        current_user_id: Current user ID

    Returns:
        Created template
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None

        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization context is required"
            )

        # Create template
        template = EventTemplate(
            name=template_data.name,
            description=template_data.description,
            event_type=template_data.event_type,
            duration_days=template_data.duration_days,
            template_data=template_data.template_data,
            is_public=template_data.is_public,
            category=template_data.category,
            tags=template_data.tags,
            organization_id=organization_id,
            created_by=current_user_id
        )

        db.add(template)
        db.commit()
        db.refresh(template)

        return template

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_template: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating template: {str(e)}"
        )


# Notifications endpoint
@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get notifications for the current user.

    Args:
        request: FastAPI request
        db: Database session
        current_user_id: Current user ID

    Returns:
        List of notifications
    """
    # For now, return sample notifications
    # In a real application, this would query from a notifications table
    try:
        notifications = [
            {
                "id": 1,
                "title": "Welcome to AI Event Planner",
                "message": "Get started by creating your first event",
                "type": "info",
                "read": False,
                "created_at": datetime.utcnow().isoformat(),
                "link": "/saas/events-new.html"
            }
        ]

        return notifications

    except Exception as e:
        print(f"Error in get_notifications: {str(e)}")
        # Return empty list on error to prevent frontend crashes
        return []


@router.post("/notifications/mark-read")
async def mark_notification_read(
    notification_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Mark a notification as read.

    Args:
        notification_id: Notification ID
        request: FastAPI request
        db: Database session
        current_user_id: Current user ID

    Returns:
        Success message
    """
    # For now, return success
    # In a real application, this would update the notification in the database
    return {"message": "Notification marked as read", "notification_id": notification_id}


# User profile endpoint
@router.get("/auth/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile.

    Args:
        current_user: Current authenticated user

    Returns:
        User profile
    """
    try:
        return UserProfileResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            first_name=getattr(current_user, 'first_name', None),
            last_name=getattr(current_user, 'last_name', None),
            profile_image_url=getattr(current_user, 'profile_image_url', None),
            is_active=current_user.is_active
        )

    except Exception as e:
        print(f"Error in get_user_profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user profile: {str(e)}"
        )


# AI Event Suggestion endpoint
@router.post("/agents/event-suggest", response_model=EventSuggestionResponse)
async def suggest_event(
    suggestion_request: EventSuggestionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Generate AI suggestions for event details based on a prompt.

    Args:
        suggestion_request: Event suggestion request
        request: FastAPI request
        db: Database session
        current_user_id: Current user ID

    Returns:
        Event suggestions
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None

        prompt = suggestion_request.prompt

        # For now, return mock suggestions based on keywords in the prompt
        # In a real application, this would call an AI agent to generate suggestions

        suggestions = EventSuggestionResponse()

        # Parse the prompt for keywords and generate suggestions
        prompt_lower = prompt.lower()

        # Detect event type
        if any(word in prompt_lower for word in ['conference', 'summit', 'symposium']):
            suggestions.type = 'Conference'
            suggestions.title = 'Professional Conference'
            suggestions.attendee_count = 200
            suggestions.budget = 50000.0
        elif any(word in prompt_lower for word in ['workshop', 'training', 'seminar']):
            suggestions.type = 'Workshop'
            suggestions.title = 'Professional Workshop'
            suggestions.attendee_count = 50
            suggestions.budget = 10000.0
        elif any(word in prompt_lower for word in ['party', 'celebration', 'gala']):
            suggestions.type = 'Social Event'
            suggestions.title = 'Special Celebration'
            suggestions.attendee_count = 100
            suggestions.budget = 15000.0
        elif any(word in prompt_lower for word in ['meeting', 'networking']):
            suggestions.type = 'Business Meeting'
            suggestions.title = 'Business Networking Event'
            suggestions.attendee_count = 30
            suggestions.budget = 5000.0
        else:
            suggestions.type = 'General Event'
            suggestions.title = 'Special Event'
            suggestions.attendee_count = 50
            suggestions.budget = 10000.0

        # Extract numbers for attendee count
        import re
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            suggestions.attendee_count = int(numbers[0])

        # Detect location
        if 'hotel' in prompt_lower:
            suggestions.venue = 'Hotel Conference Center'
        elif 'center' in prompt_lower or 'centre' in prompt_lower:
            suggestions.venue = 'Convention Center'
        elif 'office' in prompt_lower:
            suggestions.venue = 'Office Building'
        else:
            suggestions.venue = 'Venue TBD'

        # Generate description
        suggestions.description = f"A {suggestions.type.lower()} event with approximately {suggestions.attendee_count} attendees."

        # Set default dates (30 days from now for start, 31 days for end)
        from datetime import timedelta
        start_date = datetime.utcnow() + timedelta(days=30)
        end_date = start_date + timedelta(days=1)
        suggestions.start_date = start_date.strftime('%Y-%m-%d')
        suggestions.end_date = end_date.strftime('%Y-%m-%d')

        return suggestions

    except Exception as e:
        print(f"Error in suggest_event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating event suggestions: {str(e)}"
        )


# Event creation endpoint
@router.post("/events", response_model=EventCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Create a new event.

    Args:
        event_data: Event data
        request: FastAPI request
        db: Database session
        current_user_id: Current user ID

    Returns:
        Created event
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None

        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization context is required"
            )

        # Parse dates if provided
        start_date = None
        end_date = None

        if event_data.start_date:
            try:
                start_date = datetime.fromisoformat(event_data.start_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        if event_data.end_date:
            try:
                end_date = datetime.fromisoformat(event_data.end_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        # Create event
        event = Event(
            title=event_data.title,
            event_type=event_data.event_type,
            description=event_data.description,
            start_date=start_date,
            end_date=end_date,
            location=event_data.location or event_data.venue,
            attendee_count=event_data.attendee_count,
            budget=event_data.budget,
            status=event_data.status or "draft",
            organization_id=organization_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        # Return event
        return EventCreateResponse(
            id=event.id,
            title=event.title,
            event_type=event.event_type,
            description=event.description,
            start_date=event.start_date.isoformat() if event.start_date else None,
            end_date=event.end_date.isoformat() if event.end_date else None,
            location=event.location,
            attendee_count=event.attendee_count,
            budget=event.budget,
            status=event.status,
            organization_id=event.organization_id,
            created_at=event.created_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_event: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating event: {str(e)}"
        )
