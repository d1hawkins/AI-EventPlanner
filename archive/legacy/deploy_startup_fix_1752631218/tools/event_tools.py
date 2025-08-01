from typing import Dict, Any, List, Optional, Type
from datetime import datetime

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.schemas.event import EventDetails, Requirements, AgentAssignment


class RequirementsInput(BaseModel):
    """Input schema for the requirements gathering tool."""
    
    event_type: Optional[str] = Field(None, description="Type of event (e.g., conference, wedding, corporate)")
    scale: Optional[str] = Field(None, description="Scale of the event (e.g., small, medium, large)")
    budget: Optional[float] = Field(None, description="Budget for the event in dollars")
    timeline_start: Optional[str] = Field(None, description="Start date of the event (YYYY-MM-DD)")
    timeline_end: Optional[str] = Field(None, description="End date of the event (YYYY-MM-DD)")
    stakeholders: Optional[List[str]] = Field(None, description="List of stakeholders involved")
    resources: Optional[List[str]] = Field(None, description="List of resources needed")
    risks: Optional[List[str]] = Field(None, description="List of potential risks")
    success_criteria: Optional[List[str]] = Field(None, description="List of success criteria")


class RequirementsTool(BaseTool):
    """Tool for gathering event requirements."""
    
    name: str = "requirements_gathering_tool"
    description: str = "Use this tool to gather and analyze event requirements"
    args_schema: Type[RequirementsInput] = RequirementsInput
    
    def _run(self, event_type: Optional[str] = None, scale: Optional[str] = None, 
             budget: Optional[float] = None, timeline_start: Optional[str] = None, 
             timeline_end: Optional[str] = None, stakeholders: Optional[List[str]] = None, 
             resources: Optional[List[str]] = None, risks: Optional[List[str]] = None, 
             success_criteria: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the requirements gathering tool.
        
        Args:
            event_type: Type of event
            scale: Scale of the event
            budget: Budget for the event
            timeline_start: Start date of the event
            timeline_end: End date of the event
            stakeholders: List of stakeholders
            resources: List of resources
            risks: List of risks
            success_criteria: List of success criteria
            
        Returns:
            Dictionary with event details and requirements
        """
        # Process timeline dates if provided
        start_date = None
        end_date = None
        
        if timeline_start:
            try:
                start_date = datetime.strptime(timeline_start, "%Y-%m-%d")
            except ValueError:
                pass
        
        if timeline_end:
            try:
                end_date = datetime.strptime(timeline_end, "%Y-%m-%d")
            except ValueError:
                pass
        
        # Create event details
        event_details = {
            "event_type": event_type,
            "scale": scale,
            "budget": budget,
            "timeline_start": start_date,
            "timeline_end": end_date
        }
        
        # Create requirements
        requirements = {
            "stakeholders": stakeholders or [],
            "resources": resources or [],
            "risks": risks or [],
            "success_criteria": success_criteria or []
        }
        
        return {
            "event_details": event_details,
            "requirements": requirements
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class DelegationInput(BaseModel):
    """Input schema for the delegation tool."""
    
    agent_type: str = Field(..., description="Type of agent to delegate to")
    task: str = Field(..., description="Task to delegate")
    priority: Optional[str] = Field("medium", description="Priority of the task (low, medium, high)")


class DelegationTool(BaseTool):
    """Tool for delegating tasks to specialized agents."""
    
    name: str = "delegation_tool"
    description: str = "Use this tool to delegate tasks to specialized agents"
    args_schema: Type[DelegationInput] = DelegationInput
    
    def _run(self, agent_type: str, task: str, priority: str = "medium") -> Dict[str, Any]:
        """
        Run the delegation tool.
        
        Args:
            agent_type: Type of agent to delegate to
            task: Task to delegate
            priority: Priority of the task
            
        Returns:
            Dictionary with delegation details
        """
        # Validate agent type
        valid_agent_types = [
            "resource_planning",
            "financial",
            "stakeholder_management",
            "marketing_communications",
            "project_management",
            "analytics",
            "compliance_security"
        ]
        
        if agent_type not in valid_agent_types:
            return {
                "success": False,
                "error": f"Invalid agent type. Must be one of: {', '.join(valid_agent_types)}"
            }
        
        # Create agent assignment
        assignment = {
            "agent_type": agent_type,
            "task": task,
            "status": "pending",
            "priority": priority,
            "assigned_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "assignment": assignment
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class MonitoringInput(BaseModel):
    """Input schema for the monitoring tool."""
    
    agent_type: Optional[str] = Field(None, description="Type of agent to monitor")
    task_id: Optional[str] = Field(None, description="ID of the task to monitor")


class MonitoringTool(BaseTool):
    """Tool for monitoring progress of delegated tasks."""
    
    name: str = "monitoring_tool"
    description: str = "Use this tool to monitor the progress of delegated tasks"
    args_schema: Type[MonitoringInput] = MonitoringInput
    
    def _run(self, agent_type: Optional[str] = None, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the monitoring tool.
        
        Args:
            agent_type: Type of agent to monitor
            task_id: ID of the task to monitor
            
        Returns:
            Dictionary with monitoring details
        """
        # In a real implementation, this would query the status of tasks
        # For now, we'll return mock data
        
        if agent_type:
            # Mock data for agent monitoring
            return {
                "agent_type": agent_type,
                "status": "active",
                "tasks": [
                    {"id": "task1", "status": "in_progress", "completion": 0.7},
                    {"id": "task2", "status": "pending", "completion": 0.0}
                ]
            }
        elif task_id:
            # Mock data for task monitoring
            return {
                "task_id": task_id,
                "status": "in_progress",
                "completion": 0.7,
                "last_update": datetime.utcnow().isoformat(),
                "notes": "Making good progress"
            }
        else:
            # Mock data for overall monitoring
            return {
                "overall_progress": 0.5,
                "agents": {
                    "resource_planning": {"status": "active", "tasks_completed": 2, "tasks_total": 5},
                    "financial": {"status": "active", "tasks_completed": 1, "tasks_total": 3},
                    "project_management": {"status": "active", "tasks_completed": 3, "tasks_total": 7}
                }
            }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class ReportingInput(BaseModel):
    """Input schema for the reporting tool."""
    
    report_type: str = Field(..., description="Type of report (status, summary, detailed)")
    include_agents: Optional[List[str]] = Field(None, description="List of agents to include in the report")


class ReportingTool(BaseTool):
    """Tool for generating status reports."""
    
    name: str = "reporting_tool"
    description: str = "Use this tool to generate status reports"
    args_schema: Type[ReportingInput] = ReportingInput
    
    def _run(self, report_type: str, include_agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the reporting tool.
        
        Args:
            report_type: Type of report
            include_agents: List of agents to include
            
        Returns:
            Dictionary with report details
        """
        # Validate report type
        valid_report_types = ["status", "summary", "detailed"]
        if report_type not in valid_report_types:
            return {
                "success": False,
                "error": f"Invalid report type. Must be one of: {', '.join(valid_report_types)}"
            }
        
        # In a real implementation, this would generate actual reports
        # For now, we'll return mock data
        
        if report_type == "status":
            return {
                "report_type": "status",
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "on_track",
                "completion_percentage": 60,
                "next_milestones": [
                    {"name": "Venue booking confirmation", "due": "2025-03-15"},
                    {"name": "Speaker lineup finalized", "due": "2025-03-20"}
                ]
            }
        elif report_type == "summary":
            return {
                "report_type": "summary",
                "timestamp": datetime.utcnow().isoformat(),
                "event_details": {
                    "title": "Tech Conference 2025",
                    "dates": "2025-05-10 to 2025-05-12",
                    "location": "San Francisco Convention Center"
                },
                "progress": {
                    "venue": "Confirmed",
                    "speakers": "In progress (70%)",
                    "marketing": "In progress (40%)",
                    "registration": "Not started"
                },
                "budget_status": {
                    "allocated": 150000,
                    "spent": 45000,
                    "committed": 65000,
                    "remaining": 40000
                }
            }
        else:  # detailed
            return {
                "report_type": "detailed",
                "timestamp": datetime.utcnow().isoformat(),
                "event_details": {
                    "title": "Tech Conference 2025",
                    "dates": "2025-05-10 to 2025-05-12",
                    "location": "San Francisco Convention Center",
                    "expected_attendees": 500
                },
                "agent_reports": {
                    "resource_planning": {
                        "venue": "Confirmed - San Francisco Convention Center",
                        "rooms": "Main hall (500 capacity), 5 breakout rooms (100 capacity each)",
                        "equipment": "AV equipment confirmed, Wi-Fi capacity upgraded",
                        "catering": "Breakfast and lunch confirmed for all 3 days"
                    },
                    "financial": {
                        "budget_status": "On track",
                        "major_expenses": [
                            {"item": "Venue rental", "amount": 35000, "status": "Paid"},
                            {"item": "Catering", "amount": 25000, "status": "Deposit paid"},
                            {"item": "Speaker fees", "amount": 20000, "status": "Committed"}
                        ],
                        "revenue": [
                            {"source": "Ticket sales", "amount": 75000, "status": "Projected"},
                            {"source": "Sponsorships", "amount": 50000, "status": "Confirmed"}
                        ]
                    },
                    "stakeholder_management": {
                        "speakers": "15 confirmed, 5 pending",
                        "sponsors": "3 gold, 5 silver, 10 bronze",
                        "volunteers": "20 confirmed"
                    }
                },
                "risks": [
                    {"description": "Lower than expected ticket sales", "mitigation": "Increase marketing efforts"},
                    {"description": "Potential speaker cancellations", "mitigation": "Maintain backup speaker list"}
                ]
            }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)
