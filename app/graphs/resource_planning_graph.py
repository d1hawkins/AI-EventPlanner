from typing import Dict, List, Any, TypedDict, Literal, Optional
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from app.utils.llm_factory import get_llm
from app.tools.event_tools import RequirementsTool, MonitoringTool, ReportingTool
from app.tools.resource_planning_search_tool import ResourcePlanningSearchTool


# Define the state schema for the Resource Planning Agent
class ResourcePlanningStateDict(TypedDict):
    """State for the resource planning agent."""
    
    messages: List[Dict[str, str]]
    event_details: Dict[str, Any]
    venue_options: List[Dict[str, Any]]
    selected_venue: Optional[Dict[str, Any]]
    service_providers: List[Dict[str, Any]]
    equipment_needs: List[Dict[str, Any]]
    current_phase: str
    next_steps: List[str]
    resource_plan: Optional[Dict[str, Any]]


# Define the system prompt for the Resource Planning Agent
RESOURCE_PLANNING_SYSTEM_PROMPT = """You are the Resource Planning Agent for an event planning system. Your role is to:

1. Analyze event requirements to determine resource needs
2. Research and recommend venue options
3. Coordinate with service providers
4. Manage equipment and resource allocation
5. Optimize resource utilization

Your primary responsibilities include:

Venue Management:
- Venue search and selection
- Capacity planning
- Layout optimization
- Technical requirements assessment

Service Provider Coordination:
- Provider search and vetting
- Proposal management
- Contract negotiation
- Performance monitoring

Resource Allocation:
- Equipment tracking
- Staff assignment
- Schedule optimization
- Contingency planning

Your current state:
Current phase: {current_phase}
Event details: {event_details}
Venue options: {venue_options}
Selected venue: {selected_venue}
Service providers: {service_providers}
Equipment needs: {equipment_needs}
Next steps: {next_steps}

Follow these guidelines:
1. Analyze the event requirements to understand the resource needs
2. Research and recommend appropriate venues based on the event type, size, and budget
3. Identify necessary service providers and equipment
4. Create a comprehensive resource plan
5. Optimize resource allocation to maximize efficiency and minimize costs
6. Provide clear recommendations with justifications

Respond to the coordinator agent or user in a helpful, professional manner. Ask clarifying questions when needed to gather complete requirements.
"""


# Define input schemas for the Resource Planning Agent's tools
class VenueSearchInput(BaseModel):
    """Input schema for the venue search tool."""
    
    event_type: str = Field(..., description="Type of event (e.g., conference, wedding, corporate)")
    location: str = Field(..., description="Geographic location for the venue")
    attendee_count: int = Field(..., description="Expected number of attendees")
    budget_range: Optional[str] = Field(None, description="Budget range for the venue (e.g., $5000-$10000)")
    date_range: Optional[str] = Field(None, description="Date range for the event (e.g., 2025-05-10 to 2025-05-12)")
    special_requirements: Optional[List[str]] = Field(None, description="Special requirements for the venue")


class VenueSearchTool(BaseTool):
    """Tool for searching venues based on event requirements."""
    
    name: str = "venue_search_tool"
    description: str = "Search for venues based on event requirements"
    args_schema: type = VenueSearchInput
    
    def _run(self, event_type: str, location: str, attendee_count: int, 
             budget_range: Optional[str] = None, date_range: Optional[str] = None,
             special_requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the venue search tool.
        
        Args:
            event_type: Type of event
            location: Geographic location
            attendee_count: Expected number of attendees
            budget_range: Budget range for the venue
            date_range: Date range for the event
            special_requirements: Special requirements for the venue
            
        Returns:
            Dictionary with venue options
        """
        # In a real implementation, this would query a venue database or API
        # For now, we'll return mock data based on the input parameters
        
        # Parse budget range if provided
        min_budget = 0
        max_budget = float('inf')
        if budget_range:
            try:
                parts = budget_range.replace('$', '').split('-')
                if len(parts) == 2:
                    min_budget = int(parts[0].strip())
                    max_budget = int(parts[1].strip())
            except ValueError:
                pass
        
        # Generate mock venue options based on the event type and location
        venue_options = []
        
        if event_type and event_type.lower() in ["conference", "corporate", "meeting"]:
            # Conference venues
            if attendee_count <= 100:
                venue_options.append({
                    "id": "venue1",
                    "name": f"Business Center {location}",
                    "type": "conference center",
                    "capacity": 100,
                    "price_per_day": 2500,
                    "location": location,
                    "amenities": ["projector", "sound system", "wifi", "catering"],
                    "availability": True
                })
            
            if 100 <= attendee_count <= 500:
                venue_options.append({
                    "id": "venue2",
                    "name": f"{location} Convention Center - Medium Hall",
                    "type": "convention center",
                    "capacity": 500,
                    "price_per_day": 7500,
                    "location": location,
                    "amenities": ["stage", "projector", "sound system", "wifi", "catering", "breakout rooms"],
                    "availability": True
                })
            
            if attendee_count >= 300:
                venue_options.append({
                    "id": "venue3",
                    "name": f"{location} Convention Center - Grand Hall",
                    "type": "convention center",
                    "capacity": 1500,
                    "price_per_day": 15000,
                    "location": location,
                    "amenities": ["stage", "projector", "sound system", "wifi", "catering", "breakout rooms", "exhibition space"],
                    "availability": True
                })
        
        elif event_type and event_type.lower() in ["wedding", "gala", "social"]:
            # Social event venues
            if attendee_count <= 150:
                venue_options.append({
                    "id": "venue4",
                    "name": f"{location} Botanical Gardens",
                    "type": "garden",
                    "capacity": 150,
                    "price_per_day": 5000,
                    "location": location,
                    "amenities": ["outdoor space", "indoor backup", "catering"],
                    "availability": True
                })
            
            if 50 <= attendee_count <= 300:
                venue_options.append({
                    "id": "venue5",
                    "name": f"Grand Hotel {location}",
                    "type": "hotel",
                    "capacity": 300,
                    "price_per_day": 8000,
                    "location": location,
                    "amenities": ["ballroom", "sound system", "catering", "accommodation"],
                    "availability": True
                })
            
            if attendee_count >= 200:
                venue_options.append({
                    "id": "venue6",
                    "name": f"{location} Historic Mansion",
                    "type": "historic venue",
                    "capacity": 500,
                    "price_per_day": 12000,
                    "location": location,
                    "amenities": ["ballroom", "garden", "sound system", "catering"],
                    "availability": True
                })
        
        else:
            # Generic venues for other event types
            venue_options.append({
                "id": "venue7",
                "name": f"{location} Community Center",
                "type": "community center",
                "capacity": 200,
                "price_per_day": 1500,
                "location": location,
                "amenities": ["basic AV", "tables and chairs", "kitchen"],
                "availability": True
            })
            
            venue_options.append({
                "id": "venue8",
                "name": f"{location} Event Space",
                "type": "event space",
                "capacity": 350,
                "price_per_day": 4500,
                "location": location,
                "amenities": ["sound system", "lighting", "catering options"],
                "availability": True
            })
        
        # Filter by budget if provided
        if budget_range:
            venue_options = [v for v in venue_options if min_budget <= v["price_per_day"] <= max_budget]
        
        # Filter by special requirements if provided
        if special_requirements:
            for req in special_requirements:
                req_lower = req.lower()
                # Simple keyword matching for requirements
                venue_options = [
                    v for v in venue_options 
                    if any(req_lower in amenity.lower() for amenity in v["amenities"])
                ]
        
        return {
            "venue_options": venue_options,
            "search_criteria": {
                "event_type": event_type,
                "location": location,
                "attendee_count": attendee_count,
                "budget_range": budget_range,
                "date_range": date_range,
                "special_requirements": special_requirements
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class ServiceProviderSearchInput(BaseModel):
    """Input schema for the service provider search tool."""
    
    service_type: str = Field(..., description="Type of service (e.g., catering, AV, photography)")
    location: str = Field(..., description="Geographic location for the service")
    event_date: Optional[str] = Field(None, description="Date of the event (YYYY-MM-DD)")
    budget: Optional[float] = Field(None, description="Budget for the service")
    requirements: Optional[List[str]] = Field(None, description="Specific requirements for the service")


class ServiceProviderSearchTool(BaseTool):
    """Tool for searching service providers based on event requirements."""
    
    name: str = "service_provider_search_tool"
    description: str = "Search for service providers based on event requirements"
    args_schema: type = ServiceProviderSearchInput
    
    def _run(self, service_type: str, location: str, event_date: Optional[str] = None,
             budget: Optional[float] = None, requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the service provider search tool.
        
        Args:
            service_type: Type of service
            location: Geographic location
            event_date: Date of the event
            budget: Budget for the service
            requirements: Specific requirements for the service
            
        Returns:
            Dictionary with service provider options
        """
        # In a real implementation, this would query a service provider database or API
        # For now, we'll return mock data based on the input parameters
        
        service_providers = []
        
        if service_type.lower() == "catering":
            service_providers.extend([
                {
                    "id": "sp1",
                    "name": f"{location} Gourmet Catering",
                    "type": "catering",
                    "price_range": "$$",
                    "rating": 4.7,
                    "location": location,
                    "services": ["buffet", "plated", "cocktail hour", "dessert"],
                    "availability": True
                },
                {
                    "id": "sp2",
                    "name": "Elite Catering Services",
                    "type": "catering",
                    "price_range": "$$$",
                    "rating": 4.9,
                    "location": location,
                    "services": ["buffet", "plated", "cocktail hour", "dessert", "specialty menus"],
                    "availability": True
                },
                {
                    "id": "sp3",
                    "name": "Budget Friendly Catering",
                    "type": "catering",
                    "price_range": "$",
                    "rating": 4.2,
                    "location": location,
                    "services": ["buffet", "boxed lunches", "coffee service"],
                    "availability": True
                }
            ])
        
        elif service_type.lower() in ["av", "audio visual", "audio-visual"]:
            service_providers.extend([
                {
                    "id": "sp4",
                    "name": f"{location} AV Solutions",
                    "type": "audio-visual",
                    "price_range": "$$",
                    "rating": 4.6,
                    "location": location,
                    "services": ["sound systems", "projectors", "lighting", "technicians"],
                    "availability": True
                },
                {
                    "id": "sp5",
                    "name": "Premium Event Technology",
                    "type": "audio-visual",
                    "price_range": "$$$",
                    "rating": 4.8,
                    "location": location,
                    "services": ["sound systems", "projectors", "lighting", "video walls", "streaming", "technicians"],
                    "availability": True
                }
            ])
        
        elif service_type.lower() in ["photography", "photo", "video"]:
            service_providers.extend([
                {
                    "id": "sp6",
                    "name": f"{location} Event Photography",
                    "type": "photography",
                    "price_range": "$$",
                    "rating": 4.5,
                    "location": location,
                    "services": ["event photography", "portraits", "digital delivery"],
                    "availability": True
                },
                {
                    "id": "sp7",
                    "name": "Capture Moments Photography & Video",
                    "type": "photography and video",
                    "price_range": "$$$",
                    "rating": 4.9,
                    "location": location,
                    "services": ["event photography", "videography", "drone footage", "same-day edits"],
                    "availability": True
                }
            ])
        
        else:
            # Generic service providers for other types
            service_providers.append({
                "id": "sp8",
                "name": f"{location} Event Services",
                "type": service_type,
                "price_range": "$$",
                "rating": 4.3,
                "location": location,
                "services": [f"{service_type} services"],
                "availability": True
            })
        
        # Filter by budget if provided
        if budget:
            # Simple filtering based on price range
            if budget < 1000:
                service_providers = [sp for sp in service_providers if sp["price_range"] == "$"]
            elif budget < 5000:
                service_providers = [sp for sp in service_providers if sp["price_range"] in ["$", "$$"]]
            else:
                # Keep all options for high budgets
                pass
        
        # Filter by requirements if provided
        if requirements:
            for req in requirements:
                req_lower = req.lower()
                # Simple keyword matching for requirements
                service_providers = [
                    sp for sp in service_providers 
                    if any(req_lower in service.lower() for service in sp["services"])
                ]
        
        return {
            "service_providers": service_providers,
            "search_criteria": {
                "service_type": service_type,
                "location": location,
                "event_date": event_date,
                "budget": budget,
                "requirements": requirements
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class EquipmentPlanningInput(BaseModel):
    """Input schema for the equipment planning tool."""
    
    event_type: str = Field(..., description="Type of event (e.g., conference, wedding, corporate)")
    attendee_count: int = Field(..., description="Expected number of attendees")
    venue_type: str = Field(..., description="Type of venue (e.g., hotel, convention center)")
    special_requirements: Optional[List[str]] = Field(None, description="Special equipment requirements")


class EquipmentPlanningTool(BaseTool):
    """Tool for planning equipment needs based on event requirements."""
    
    name: str = "equipment_planning_tool"
    description: str = "Plan equipment needs based on event requirements"
    args_schema: type = EquipmentPlanningInput
    
    def _run(self, event_type: str, attendee_count: int, venue_type: str,
             special_requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the equipment planning tool.
        
        Args:
            event_type: Type of event
            attendee_count: Expected number of attendees
            venue_type: Type of venue
            special_requirements: Special equipment requirements
            
        Returns:
            Dictionary with equipment recommendations
        """
        # In a real implementation, this would use algorithms to determine equipment needs
        # For now, we'll return mock data based on the input parameters
        
        equipment_needs = []
        
        # Basic equipment for all events
        equipment_needs.append({
            "category": "Audio",
            "items": [
                {"name": "Microphones", "quantity": 2, "notes": "Wireless handheld"}
            ]
        })
        
        equipment_needs.append({
            "category": "Furniture",
            "items": [
                {"name": "Tables", "quantity": max(5, attendee_count // 10), "notes": "Round tables, 10 seats each"},
                {"name": "Chairs", "quantity": attendee_count, "notes": "Padded folding chairs"}
            ]
        })
        
        # Event-specific equipment
        if event_type.lower() in ["conference", "corporate", "meeting"]:
            equipment_needs.append({
                "category": "Visual",
                "items": [
                    {"name": "Projector", "quantity": 1, "notes": "High-lumen projector"},
                    {"name": "Projection Screen", "quantity": 1, "notes": "16:9 aspect ratio"},
                    {"name": "Laptop", "quantity": 1, "notes": "For presentations"}
                ]
            })
            
            equipment_needs.append({
                "category": "Audio",
                "items": [
                    {"name": "Sound System", "quantity": 1, "notes": "Appropriate for venue size"},
                    {"name": "Lavalier Microphones", "quantity": 2, "notes": "For presenters"}
                ]
            })
            
            if attendee_count > 100:
                equipment_needs.append({
                    "category": "Networking",
                    "items": [
                        {"name": "Wi-Fi Boosters", "quantity": attendee_count // 100, "notes": "To ensure good connectivity"}
                    ]
                })
        
        elif event_type.lower() in ["wedding", "gala", "social"]:
            equipment_needs.append({
                "category": "Lighting",
                "items": [
                    {"name": "Decorative Lighting", "quantity": 1, "notes": "Ambient lighting package"},
                    {"name": "Uplighting", "quantity": 8, "notes": "For perimeter of venue"}
                ]
            })
            
            equipment_needs.append({
                "category": "Entertainment",
                "items": [
                    {"name": "Sound System", "quantity": 1, "notes": "For music and speeches"},
                    {"name": "Dance Floor", "quantity": 1, "notes": f"{attendee_count // 3} square feet"}
                ]
            })
        
        # Add special requirements if provided
        if special_requirements:
            special_items = []
            for req in special_requirements:
                if "video" in req.lower():
                    special_items.append({"name": "Video Recording Equipment", "quantity": 1, "notes": "Professional-grade camera and tripod"})
                if "stream" in req.lower():
                    special_items.append({"name": "Streaming Equipment", "quantity": 1, "notes": "For live streaming the event"})
                if "translation" in req.lower():
                    special_items.append({"name": "Translation Equipment", "quantity": attendee_count // 5, "notes": "Headsets and receivers"})
            
            if special_items:
                equipment_needs.append({
                    "category": "Special Requirements",
                    "items": special_items
                })
        
        return {
            "equipment_needs": equipment_needs,
            "estimated_cost": calculate_equipment_cost(equipment_needs),
            "planning_criteria": {
                "event_type": event_type,
                "attendee_count": attendee_count,
                "venue_type": venue_type,
                "special_requirements": special_requirements
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


def calculate_equipment_cost(equipment_needs: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate the estimated cost of equipment.
    
    Args:
        equipment_needs: List of equipment categories and items
        
    Returns:
        Dictionary with cost breakdown
    """
    # Mock cost calculation
    total_cost = 0
    cost_breakdown = {}
    
    for category in equipment_needs:
        category_cost = 0
        for item in category["items"]:
            # Mock cost calculation based on item name and quantity
            item_cost = 0
            
            if "projector" in item["name"].lower():
                item_cost = 250 * item["quantity"]
            elif "screen" in item["name"].lower():
                item_cost = 100 * item["quantity"]
            elif "microphone" in item["name"].lower():
                item_cost = 50 * item["quantity"]
            elif "sound system" in item["name"].lower():
                item_cost = 500 * item["quantity"]
            elif "lighting" in item["name"].lower():
                item_cost = 300 * item["quantity"]
            elif "table" in item["name"].lower():
                item_cost = 20 * item["quantity"]
            elif "chair" in item["name"].lower():
                item_cost = 5 * item["quantity"]
            elif "dance floor" in item["name"].lower():
                item_cost = 500 * item["quantity"]
            elif "wi-fi" in item["name"].lower():
                item_cost = 150 * item["quantity"]
            elif "streaming" in item["name"].lower():
                item_cost = 750 * item["quantity"]
            elif "recording" in item["name"].lower():
                item_cost = 500 * item["quantity"]
            elif "translation" in item["name"].lower():
                item_cost = 25 * item["quantity"]
            else:
                item_cost = 50 * item["quantity"]  # Default cost
            
            category_cost += item_cost
        
        cost_breakdown[category["category"]] = category_cost
        total_cost += category_cost
    
    return {
        "total": total_cost,
        "breakdown": cost_breakdown
    }


class ResourcePlanGenerationInput(BaseModel):
    """Input schema for the resource plan generation tool."""
    
    event_details: Dict[str, Any] = Field(..., description="Details about the event")
    venue: Dict[str, Any] = Field(..., description="Selected venue information")
    service_providers: List[Dict[str, Any]] = Field(..., description="Selected service providers")
    equipment_needs: List[Dict[str, Any]] = Field(..., description="Equipment needs for the event")


class ResourcePlanGenerationTool(BaseTool):
    """Tool for generating a comprehensive resource plan."""
    
    name: str = "resource_plan_generation_tool"
    description: str = "Generate a comprehensive resource plan for an event"
    args_schema: type = ResourcePlanGenerationInput
    
    def _run(self, event_details: Dict[str, Any], venue: Dict[str, Any],
             service_providers: List[Dict[str, Any]], equipment_needs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run the resource plan generation tool.
        
        Args:
            event_details: Details about the event
            venue: Selected venue information
            service_providers: Selected service providers
            equipment_needs: Equipment needs for the event
            
        Returns:
            Dictionary with the comprehensive resource plan
        """
        # In a real implementation, this would generate an optimized resource plan
        # For now, we'll create a structured plan based on the input parameters
        
        # Calculate total costs
        venue_cost = venue.get("price_per_day", 0) * 1  # Assuming 1 day event
        
        service_provider_cost = 0
        for provider in service_providers:
            # Mock cost calculation based on price range
            if provider.get("price_range") == "$":
                service_provider_cost += 1000
            elif provider.get("price_range") == "$$":
                service_provider_cost += 3000
            elif provider.get("price_range") == "$$$":
                service_provider_cost += 7000
            else:
                service_provider_cost += 2000
        
        equipment_cost = 0
        for category in equipment_needs:
            for item in category.get("items", []):
                # Use the same logic as in calculate_equipment_cost
                item_cost = 0
                
                if "projector" in item["name"].lower():
                    item_cost = 250 * item["quantity"]
                elif "screen" in item["name"].lower():
                    item_cost = 100 * item["quantity"]
                elif "microphone" in item["name"].lower():
                    item_cost = 50 * item["quantity"]
                elif "sound system" in item["name"].lower():
                    item_cost = 500 * item["quantity"]
                elif "lighting" in item["name"].lower():
                    item_cost = 300 * item["quantity"]
                elif "table" in item["name"].lower():
                    item_cost = 20 * item["quantity"]
                elif "chair" in item["name"].lower():
                    item_cost = 5 * item["quantity"]
                elif "dance floor" in item["name"].lower():
                    item_cost = 500 * item["quantity"]
                elif "wi-fi" in item["name"].lower():
                    item_cost = 150 * item["quantity"]
                elif "streaming" in item["name"].lower():
                    item_cost = 750 * item["quantity"]
                elif "recording" in item["name"].lower():
                    item_cost = 500 * item["quantity"]
                elif "translation" in item["name"].lower():
                    item_cost = 25 * item["quantity"]
                else:
                    item_cost = 50 * item["quantity"]  # Default cost
                
                equipment_cost += item_cost
        
        total_cost = venue_cost + service_provider_cost + equipment_cost
        
        # Create the resource plan
        resource_plan = {
            "summary": {
                "event_type": event_details.get("event_type", "Unknown"),
                "date": event_details.get("timeline_start", "TBD"),
                "location": venue.get("location", "Unknown"),
                "attendee_count": event_details.get("attendee_count", 0),
                "total_cost": total_cost
            },
            "venue": {
                "name": venue.get("name", "Unknown"),
                "address": f"{venue.get('location', 'Unknown')} (detailed address to be confirmed)",
                "cost": venue_cost,
                "capacity": venue.get("capacity", 0),
                "amenities": venue.get("amenities", []),
                "notes": "Venue booking to be confirmed"
            },
            "service_providers": [
                {
                    "name": provider.get("name", "Unknown"),
                    "type": provider.get("type", "Unknown"),
                    "services": provider.get("services", []),
                    "cost_estimate": 3000 if provider.get("price_range") == "$$" else 
                                    7000 if provider.get("price_range") == "$$$" else 
                                    1000 if provider.get("price_range") == "$" else 2000,
                    "notes": "Service provider to be confirmed"
                }
                for provider in service_providers
            ],
            "equipment": {
                "categories": [
                    {
                        "name": category.get("category", "Unknown"),
                        "items": category.get("items", []),
                        "cost_estimate": sum([
                            250 * item["quantity"] if "projector" in item["name"].lower() else
                            100 * item["quantity"] if "screen" in item["name"].lower() else
                            50 * item["quantity"] if "microphone" in item["name"].lower() else
                            500 * item["quantity"] if "sound system" in item["name"].lower() else
                            300 * item["quantity"] if "lighting" in item["name"].lower() else
                            20 * item["quantity"] if "table" in item["name"].lower() else
                            5 * item["quantity"] if "chair" in item["name"].lower() else
                            500 * item["quantity"] if "dance floor" in item["name"].lower() else
                            150 * item["quantity"] if "wi-fi" in item["name"].lower() else
                            750 * item["quantity"] if "streaming" in item["name"].lower() else
                            500 * item["quantity"] if "recording" in item["name"].lower() else
                            25 * item["quantity"] if "translation" in item["name"].lower() else
                            50 * item["quantity"]  # Default cost
                            for item in category.get("items", [])
                        ])
                    }
                    for category in equipment_needs
                ],
                "total_cost": equipment_cost
            },
            "timeline": {
                "setup": {
                    "start": "Day before event, 2:00 PM",
                    "end": "Day before event, 8:00 PM",
                    "tasks": [
                        "Venue access and initial setup",
                        "Equipment delivery and installation",
                        "Basic decoration setup"
                    ]
                },
                "event_day": {
                    "start": "Event day, 8:00 AM",
                    "end": "Event day, 10:00 PM",
                    "tasks": [
                        "Final setup (2 hours before event)",
                        "Service provider arrival and setup",
                        "Event execution",
                        "Initial breakdown"
                    ]
                },
                "teardown": {
                    "start": "Event day, 10:00 PM",
                    "end": "Day after event, 12:00 PM",
                    "tasks": [
                        "Equipment breakdown and removal",
                        "Venue cleanup",
                        "Final walkthrough"
                    ]
                }
            },
            "staffing": {
                "setup_team": {
 
                    "roles": ["Setup coordinator", "Equipment technician", "General labor"]
                },
                "event_team": {
                    "count": max(3, int(event_details.get("attendee_count", 100) or 100) // 50),
                    "roles": ["Event manager", "AV technician", "Service coordinator", "General staff"]
                },
                "teardown_team": {
                    "count": max(2, int(event_details.get("attendee_count", 100) or 100) // 100),
                    "roles": ["Teardown coordinator", "Equipment technician", "General labor"]
                }
            },
            "contingency_plans": [
                {
                    "scenario": "Weather issues (for outdoor components)",
                    "plan": "Indoor backup space or tent rental"
                },
                {
                    "scenario": "Technical failures",
                    "plan": "Backup equipment and technician on standby"
                },
                {
                    "scenario": "Vendor no-show",
                    "plan": "List of backup vendors with contact information"
                }
            ]
        }
        
        return {
            "resource_plan": resource_plan,
            "total_cost": total_cost,
            "cost_breakdown": {
                "venue": venue_cost,
                "service_providers": service_provider_cost,
                "equipment": equipment_cost
            }
        }


def create_resource_planning_graph():
    """
    Create the resource planning agent graph.
    
    Returns:
        Compiled LangGraph for the resource planning agent
    """
    # Initialize the LLM
    llm = get_llm(temperature=0.2)
    
    # Initialize tools
    tools = [
        VenueSearchTool(),
        ServiceProviderSearchTool(),
        EquipmentPlanningTool(),
        ResourcePlanGenerationTool(),
        RequirementsTool(),
        MonitoringTool(),
        ReportingTool(),
        ResourcePlanningSearchTool()
    ]
    
    # Create the tool node
    tool_node = ToolNode(tools)
    
    # Define the nodes
    def analyze_requirements(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Analyze event requirements to determine resource needs.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Get the last message
        last_message = state["messages"][-1]["content"] if state["messages"] else ""
        
        # Create a prompt for the LLM to analyze requirements
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps analyze event planning requirements to determine resource needs.
Based on the event details and conversation, extract key information about:
1. Venue requirements (location, capacity, amenities)
2. Service provider needs (catering, AV, photography, etc.)
3. Equipment needs (furniture, AV equipment, decorations, etc.)

Provide a structured analysis of what resources will be needed for this event."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}

Analyze these event details and the conversation to determine the resource needs for this event. Focus on venue requirements, service provider needs, and equipment needs.""")
        ])
        
        # Analyze requirements using the LLM
        chain = prompt | llm
        # Filter out any messages with empty content to avoid API errors
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"] if m.get("content")]})
        
        # Add the analysis to messages
        state["messages"].append({
            "role": "assistant",
            "content": result.content
        })
        
        # Update phase and next steps
        state["current_phase"] = "requirements_analysis"
        state["next_steps"] = ["search_venues", "identify_service_providers", "plan_equipment"]
        
        return state
    
    def search_venues(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Search for venues based on event requirements.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with venue options
        """
        # Create a prompt for the LLM to extract venue search criteria
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps extract venue search criteria from event details and conversation.
Extract the following information:
1. Event type
2. Preferred location
3. Expected attendee count
4. Budget range (if available)
5. Date range (if available)
6. Special requirements (if any)

Return the extracted information in a structured format."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}

Extract the venue search criteria from these event details and the conversation. If any information is missing, make reasonable assumptions based on the available data.""")
        ])
        
        # Extract venue search criteria using the LLM
        chain = prompt | llm
        # Filter out any messages with empty content to avoid API errors
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"] if m.get("content")]})
        
        # Use the VenueSearchTool to search for venues
        venue_search_tool = VenueSearchTool()
        
        # Extract parameters from the LLM result
        # In a real implementation, this would parse the LLM output more robustly
        # For now, we'll use some default values and extract what we can
        
        # Ensure event_type is a string with a default value
        event_type = state["event_details"].get("event_type", "conference") or "conference"
        location = "New York"  # Default location
        # Ensure attendee_count is an integer with a default value of 100
        attendee_count = int(state["event_details"].get("attendee_count", 100) or 100)
        
        # Simple extraction of location from the LLM result
        if "location" in result.content.lower():
            location_line = [line for line in result.content.split("\n") if "location" in line.lower()]
            if location_line:
                location_parts = location_line[0].split(":")
                if len(location_parts) > 1:
                    location = location_parts[1].strip()
        
        # Search for venues
        venue_results = venue_search_tool._run(
            event_type=event_type,
            location=location,
            attendee_count=attendee_count
        )
        
        # Update state with venue options
        state["venue_options"] = venue_results.get("venue_options", [])
        
        # Add venue options to messages
        venue_summary = "\n".join([
            f"- {venue['name']}: {venue['type']}, capacity {venue['capacity']}, ${venue['price_per_day']} per day"
            for venue in state["venue_options"]
        ])
        
        state["messages"].append({
            "role": "assistant",
            "content": f"Based on the event requirements, I've found the following venue options:\n\n{venue_summary}\n\nWould you like more details on any of these venues or should I proceed with recommending the best option?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "venue_selection"
        state["next_steps"] = ["select_venue", "search_service_providers"]
        
        return state
    
    def select_venue(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Select the best venue from the options.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with selected venue
        """
        # If no venue options, return the state unchanged
        if not state["venue_options"]:
            state["messages"].append({
                "role": "assistant",
                "content": "I couldn't find any suitable venues based on the current requirements. Let's revise the venue criteria."
            })
            return state
        
        # Create a prompt for the LLM to select the best venue
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps select the best venue for an event.
Analyze the venue options and event requirements to determine the most suitable venue.
Consider factors such as:
1. Capacity vs. attendee count
2. Price vs. budget
3. Amenities vs. requirements
4. Location
5. Venue type appropriateness for the event type

Provide a clear recommendation with justification."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Venue options: {state['venue_options']}

Select the best venue for this event and explain your reasoning.""")
        ])
        
        # Select venue using the LLM
        chain = prompt | llm
        # Filter out any messages with empty content to avoid API errors
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"] if m.get("content")]})
        
        # For demonstration purposes, we'll select the first venue
        # In a real implementation, we would parse the LLM output to determine the selected venue
        selected_venue = state["venue_options"][0] if state["venue_options"] else None
        
        # Update state with selected venue
        state["selected_venue"] = selected_venue
        
        # Add venue selection to messages
        if selected_venue:
            state["messages"].append({
                "role": "assistant",
                "content": f"I recommend the {selected_venue['name']} as the best venue for this event.\n\n{result.content}"
            })
        else:
            state["messages"].append({
                "role": "assistant",
                "content": "I couldn't select a venue because no options were available. Let's revise the venue criteria."
            })
        
        # Update phase and next steps
        state["current_phase"] = "service_provider_selection"
        state["next_steps"] = ["search_service_providers", "plan_equipment"]
        
        return state
    
    def search_service_providers(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Search for service providers based on event requirements.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with service provider options
        """
        # Create a prompt for the LLM to determine required service types
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps determine what service providers are needed for an event.
Based on the event details, venue, and conversation, identify what types of service providers are needed.
Common service types include:
1. Catering
2. Audio-Visual (AV)
3. Photography/Videography
4. Decoration
5. Entertainment
6. Security
7. Transportation

Return a list of required service types with brief justifications."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Selected venue: {state['selected_venue']}

Determine what service providers are needed for this event.""")
        ])
        
        # Determine required service types using the LLM
        chain = prompt | llm
        # Filter out any messages with empty content to avoid API errors
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"] if m.get("content")]})
        
        # For demonstration purposes, we'll search for catering and AV services
        # In a real implementation, we would parse the LLM output to determine the required service types
        service_provider_search_tool = ServiceProviderSearchTool()
        
        location = state["selected_venue"]["location"] if state["selected_venue"] else "New York"
        
        # Search for catering providers
        catering_results = service_provider_search_tool._run(
            service_type="catering",
            location=location
        )
        
        # Search for AV providers
        av_results = service_provider_search_tool._run(
            service_type="audio visual",
            location=location
        )
        
        # Combine service providers
        service_providers = catering_results.get("service_providers", []) + av_results.get("service_providers", [])
        
        # Update state with service providers
        state["service_providers"] = service_providers
        
        # Add service providers to messages
        service_summary = "\n".join([
            f"- {provider['name']}: {provider['type']}, Rating: {provider['rating']}, Price: {provider['price_range']}"
            for provider in state["service_providers"]
        ])
        
        state["messages"].append({
            "role": "assistant",
            "content": f"Based on the event requirements, I've identified the following service providers:\n\n{service_summary}\n\nWould you like more details on any of these providers or should I proceed with planning the equipment needs?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "equipment_planning"
        state["next_steps"] = ["plan_equipment", "generate_resource_plan"]
        
        return state
    
    def plan_equipment(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Plan equipment needs based on event requirements.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with equipment needs
        """
        # If no venue selected, return the state unchanged
        if not state["selected_venue"]:
            state["messages"].append({
                "role": "assistant",
                "content": "I need a selected venue before I can plan the equipment needs. Let's select a venue first."
            })
            return state
        
        # Use the EquipmentPlanningTool to plan equipment needs
        equipment_planning_tool = EquipmentPlanningTool()
        
        # Ensure event_type is a string with a default value
        event_type = state["event_details"].get("event_type", "conference") or "conference"
        # Ensure attendee_count is an integer with a default value of 100
        attendee_count = int(state["event_details"].get("attendee_count", 100) or 100)
        venue_type = state["selected_venue"].get("type", "conference center")
        
        # Plan equipment needs
        equipment_results = equipment_planning_tool._run(
            event_type=event_type,
            attendee_count=attendee_count,
            venue_type=venue_type
        )
        
        # Update state with equipment needs
        state["equipment_needs"] = equipment_results.get("equipment_needs", [])
        
        # Add equipment needs to messages
        equipment_summary = ""
        for category in state["equipment_needs"]:
            equipment_summary += f"\n{category['category']}:\n"
            for item in category["items"]:
                equipment_summary += f"- {item['name']}: {item['quantity']} ({item['notes']})\n"
        
        estimated_cost = equipment_results.get("estimated_cost", {})
        cost_summary = f"Total estimated equipment cost: ${estimated_cost.get('total', 0)}"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"Based on the event requirements and selected venue, I've planned the following equipment needs:\n{equipment_summary}\n\n{cost_summary}\n\nShould I proceed with generating a comprehensive resource plan?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "resource_plan_generation"
        state["next_steps"] = ["generate_resource_plan"]
        
        return state
    
    def generate_resource_plan(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Generate a comprehensive resource plan.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with resource plan
        """
        # If no venue selected or no equipment needs, return the state unchanged
        if not state["selected_venue"] or not state["equipment_needs"]:
            state["messages"].append({
                "role": "assistant",
                "content": "I need a selected venue and equipment needs before I can generate a resource plan. Let's complete those steps first."
            })
            return state
        
        # Use the ResourcePlanGenerationTool to generate a resource plan
        resource_plan_tool = ResourcePlanGenerationTool()
        
        # Generate resource plan
        plan_results = resource_plan_tool._run(
            event_details=state["event_details"],
            venue=state["selected_venue"],
            service_providers=state["service_providers"],
            equipment_needs=state["equipment_needs"]
        )
        
        # Update state with resource plan
        state["resource_plan"] = plan_results.get("resource_plan", {})
        
        # Create a prompt for the LLM to generate a summary of the resource plan
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps summarize resource plans for events.
Create a clear, concise summary of the resource plan that highlights:
1. Key venue details
2. Selected service providers
3. Equipment overview
4. Cost breakdown
5. Timeline
6. Staffing
7. Contingency plans

The summary should be professional and easy to understand."""),
            HumanMessage(content=f"""Resource plan: {state['resource_plan']}

Create a concise summary of this resource plan.""")
        ])
        
        # Generate summary using the LLM
        chain = prompt | llm
        # Filter out any messages with empty content to avoid API errors
        result = chain.invoke({})
        
        # Add resource plan to messages
        state["messages"].append({
            "role": "assistant",
            "content": f"I've generated a comprehensive resource plan for the event:\n\n{result.content}\n\nThe total estimated cost is ${state['resource_plan']['summary']['total_cost']}. Would you like me to make any adjustments to this plan?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "plan_review"
        state["next_steps"] = ["finalize_plan"]
        
        return state
    
    def generate_response(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Generate a response to the user or coordinator agent.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create the resource planning prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=RESOURCE_PLANNING_SYSTEM_PROMPT.format(
                current_phase=state["current_phase"],
                event_details=state["event_details"],
                venue_options=state["venue_options"],
                selected_venue=state["selected_venue"],
                service_providers=state["service_providers"],
                equipment_needs=state["equipment_needs"],
                next_steps=state["next_steps"]
            )),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Generate response using the LLM
        chain = prompt | llm
        # Filter out any messages with empty content to avoid API errors
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"] if m.get("content")]})
        
        # Add the response to messages
        new_message = {
            "role": "assistant",
            "content": result.content
        }
        state["messages"].append(new_message)
        
        return state
    
    # Create the graph
    workflow = StateGraph(ResourcePlanningStateDict)
    
    # Add nodes
    workflow.add_node("analyze_requirements", analyze_requirements)
    workflow.add_node("search_venues", search_venues)
    workflow.add_node("select_venue", select_venue)
    workflow.add_node("search_service_providers", search_service_providers)
    workflow.add_node("plan_equipment", plan_equipment)
    workflow.add_node("generate_resource_plan", generate_resource_plan)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("tools", tool_node)
    
    # Add edges
    workflow.add_edge("analyze_requirements", "search_venues")
    workflow.add_edge("search_venues", "select_venue")
    workflow.add_edge("select_venue", "search_service_providers")
    workflow.add_edge("search_service_providers", "plan_equipment")
    workflow.add_edge("plan_equipment", "generate_resource_plan")
    workflow.add_edge("generate_resource_plan", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Set the entry point
    workflow.set_entry_point("analyze_requirements")
    
    return workflow.compile()
def create_initial_state() -> ResourcePlanningStateDict:
    """Create the initial state for the resource planning agent."""
    return {
        "messages": [],
        "event_details": {
            "event_type": None,
            "title": None,
            "description": None,
            "attendee_count": None,
            "scale": None,
            "timeline_start": None,
            "timeline_end": None,
            "budget": None,
            "location": None
        },
        "venue_options": [],
        "selected_venue": None,
        "service_providers": [],
        "equipment_needs": [],
        "current_phase": "requirements_analysis",
        "next_steps": ["analyze_requirements"],
        "resource_plan": None
    }
