from typing import Dict, Any, List, Optional, Type
from datetime import datetime, timedelta
import uuid

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.schemas.project import Task, Milestone, Risk, Timeline, ProjectPlan

class TaskManagementInput(BaseModel):
    """Input schema for the task management tool."""
    
    action: str = Field(..., description="Action to perform (create, update, delete, list)")
    task_id: Optional[str] = Field(None, description="ID of the task (for update/delete)")
    name: Optional[str] = Field(None, description="Name of the task (for create/update)")
    description: Optional[str] = Field(None, description="Description of the task (for create/update)")
    status: Optional[str] = Field(None, description="Status of the task (for create/update)")
    priority: Optional[str] = Field(None, description="Priority of the task (for create/update)")
    assigned_to: Optional[str] = Field(None, description="Person or agent assigned to the task (for create/update)")
    dependencies: Optional[List[str]] = Field(None, description="IDs of dependent tasks (for create/update)")
    start_date: Optional[str] = Field(None, description="Planned start date (YYYY-MM-DD) (for create/update)")
    end_date: Optional[str] = Field(None, description="Planned end date (YYYY-MM-DD) (for create/update)")
    completion_percentage: Optional[int] = Field(None, description="Percentage of task completed (for update)")

class TaskManagementTool(BaseTool):
    """Tool for managing tasks in a project."""
    
    name: str = "task_management_tool"
    description: str = "Manage tasks in a project (create, update, delete, list)"
    args_schema: Type[TaskManagementInput] = TaskManagementInput
    
    def _run(self, action: str, task_id: Optional[str] = None, name: Optional[str] = None, 
             description: Optional[str] = None, status: Optional[str] = None, 
             priority: Optional[str] = None, assigned_to: Optional[str] = None,
             dependencies: Optional[List[str]] = None, start_date: Optional[str] = None,
             end_date: Optional[str] = None, completion_percentage: Optional[int] = None) -> Dict[str, Any]:
        """
        Run the task management tool.
        
        Args:
            action: Action to perform (create, update, delete, list)
            task_id: ID of the task (for update/delete)
            name: Name of the task (for create/update)
            description: Description of the task (for create/update)
            status: Status of the task (for create/update)
            priority: Priority of the task (for create/update)
            assigned_to: Person or agent assigned to the task (for create/update)
            dependencies: IDs of dependent tasks (for create/update)
            start_date: Planned start date (YYYY-MM-DD) (for create/update)
            end_date: Planned end date (YYYY-MM-DD) (for create/update)
            completion_percentage: Percentage of task completed (for update)
            
        Returns:
            Dictionary with task information or list of tasks
        """
        # In a real implementation, this would interact with a database
        # For now, we'll return mock data
        
        if action == "create":
            # Create a new task
            new_task = {
                "id": str(uuid.uuid4()),
                "name": name or "New Task",
                "description": description or "Task description",
                "status": status or "not_started",
                "priority": priority or "medium",
                "assigned_to": assigned_to,
                "dependencies": dependencies or [],
                "start_date": start_date,
                "end_date": end_date,
                "actual_start_date": None,
                "actual_end_date": None,
                "completion_percentage": 0,
                "notes": None
            }
            
            return {
                "action": "create",
                "task": new_task,
                "message": f"Task '{name}' created successfully"
            }
            
        elif action == "update":
            # Update an existing task
            if not task_id:
                return {
                    "action": "update",
                    "error": "Task ID is required for update action"
                }
            
            # In a real implementation, this would fetch the task from a database
            # For now, we'll create a mock task
            updated_task = {
                "id": task_id,
                "name": name or "Updated Task",
                "description": description or "Updated task description",
                "status": status or "in_progress",
                "priority": priority or "high",
                "assigned_to": assigned_to,
                "dependencies": dependencies or [],
                "start_date": start_date,
                "end_date": end_date,
                "actual_start_date": datetime.now().isoformat() if status == "in_progress" else None,
                "actual_end_date": datetime.now().isoformat() if status == "completed" else None,
                "completion_percentage": completion_percentage or 50,
                "notes": None
            }
            
            return {
                "action": "update",
                "task": updated_task,
                "message": f"Task '{task_id}' updated successfully"
            }
            
        elif action == "delete":
            # Delete an existing task
            if not task_id:
                return {
                    "action": "delete",
                    "error": "Task ID is required for delete action"
                }
            
            return {
                "action": "delete",
                "task_id": task_id,
                "message": f"Task '{task_id}' deleted successfully"
            }
            
        elif action == "list":
            # List all tasks
            # In a real implementation, this would fetch tasks from a database
            # For now, we'll return mock tasks
            tasks = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Setup Venue",
                    "description": "Prepare the venue for the event",
                    "status": "in_progress",
                    "priority": "high",
                    "assigned_to": "Resource Planning Agent",
                    "dependencies": [],
                    "start_date": (datetime.now() - timedelta(days=5)).isoformat(),
                    "end_date": (datetime.now() + timedelta(days=10)).isoformat(),
                    "actual_start_date": (datetime.now() - timedelta(days=5)).isoformat(),
                    "actual_end_date": None,
                    "completion_percentage": 30,
                    "notes": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Finalize Budget",
                    "description": "Complete the budget allocation",
                    "status": "completed",
                    "priority": "critical",
                    "assigned_to": "Financial Agent",
                    "dependencies": [],
                    "start_date": (datetime.now() - timedelta(days=15)).isoformat(),
                    "end_date": (datetime.now() - timedelta(days=5)).isoformat(),
                    "actual_start_date": (datetime.now() - timedelta(days=15)).isoformat(),
                    "actual_end_date": (datetime.now() - timedelta(days=5)).isoformat(),
                    "completion_percentage": 100,
                    "notes": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Confirm Speakers",
                    "description": "Finalize speaker list and schedule",
                    "status": "not_started",
                    "priority": "medium",
                    "assigned_to": "Stakeholder Management Agent",
                    "dependencies": [],
                    "start_date": (datetime.now() + timedelta(days=5)).isoformat(),
                    "end_date": (datetime.now() + timedelta(days=15)).isoformat(),
                    "actual_start_date": None,
                    "actual_end_date": None,
                    "completion_percentage": 0,
                    "notes": None
                }
            ]
            
            return {
                "action": "list",
                "tasks": tasks,
                "count": len(tasks)
            }
        
        else:
            return {
                "error": f"Unknown action: {action}"
            }

class MilestoneManagementInput(BaseModel):
    """Input schema for the milestone management tool."""
    
    action: str = Field(..., description="Action to perform (create, update, delete, list)")
    milestone_id: Optional[str] = Field(None, description="ID of the milestone (for update/delete)")
    name: Optional[str] = Field(None, description="Name of the milestone (for create/update)")
    description: Optional[str] = Field(None, description="Description of the milestone (for create/update)")
    date: Optional[str] = Field(None, description="Date of the milestone (YYYY-MM-DD) (for create/update)")
    status: Optional[str] = Field(None, description="Status of the milestone (for create/update)")
    associated_tasks: Optional[List[str]] = Field(None, description="IDs of associated tasks (for create/update)")

class MilestoneManagementTool(BaseTool):
    """Tool for managing milestones in a project."""
    
    name: str = "milestone_management_tool"
    description: str = "Manage milestones in a project (create, update, delete, list)"
    args_schema: Type[MilestoneManagementInput] = MilestoneManagementInput
    
    def _run(self, action: str, milestone_id: Optional[str] = None, name: Optional[str] = None, 
             description: Optional[str] = None, date: Optional[str] = None, 
             status: Optional[str] = None, associated_tasks: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the milestone management tool.
        
        Args:
            action: Action to perform (create, update, delete, list)
            milestone_id: ID of the milestone (for update/delete)
            name: Name of the milestone (for create/update)
            description: Description of the milestone (for create/update)
            date: Date of the milestone (YYYY-MM-DD) (for create/update)
            status: Status of the milestone (for create/update)
            associated_tasks: IDs of associated tasks (for create/update)
            
        Returns:
            Dictionary with milestone information or list of milestones
        """
        # In a real implementation, this would interact with a database
        # For now, we'll return mock data
        
        if action == "create":
            # Create a new milestone
            new_milestone = {
                "id": str(uuid.uuid4()),
                "name": name or "New Milestone",
                "description": description or "Milestone description",
                "date": date or datetime.now().isoformat(),
                "status": status or "not_reached",
                "associated_tasks": associated_tasks or []
            }
            
            return {
                "action": "create",
                "milestone": new_milestone,
                "message": f"Milestone '{name}' created successfully"
            }
            
        elif action == "update":
            # Update an existing milestone
            if not milestone_id:
                return {
                    "action": "update",
                    "error": "Milestone ID is required for update action"
                }
            
            # In a real implementation, this would fetch the milestone from a database
            # For now, we'll create a mock milestone
            updated_milestone = {
                "id": milestone_id,
                "name": name or "Updated Milestone",
                "description": description or "Updated milestone description",
                "date": date or datetime.now().isoformat(),
                "status": status or "not_reached",
                "associated_tasks": associated_tasks or []
            }
            
            return {
                "action": "update",
                "milestone": updated_milestone,
                "message": f"Milestone '{milestone_id}' updated successfully"
            }
            
        elif action == "delete":
            # Delete an existing milestone
            if not milestone_id:
                return {
                    "action": "delete",
                    "error": "Milestone ID is required for delete action"
                }
            
            return {
                "action": "delete",
                "milestone_id": milestone_id,
                "message": f"Milestone '{milestone_id}' deleted successfully"
            }
            
        elif action == "list":
            # List all milestones
            # In a real implementation, this would fetch milestones from a database
            # For now, we'll return mock milestones
            milestones = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Venue Secured",
                    "description": "Venue contract signed and deposit paid",
                    "date": (datetime.now() - timedelta(days=5)).isoformat(),
                    "status": "reached",
                    "associated_tasks": []
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "All Speakers Confirmed",
                    "description": "All speakers have confirmed their participation",
                    "date": (datetime.now() + timedelta(days=15)).isoformat(),
                    "status": "not_reached",
                    "associated_tasks": []
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Marketing Launch",
                    "description": "Official marketing campaign launch",
                    "date": (datetime.now() + timedelta(days=10)).isoformat(),
                    "status": "not_reached",
                    "associated_tasks": []
                }
            ]
            
            return {
                "action": "list",
                "milestones": milestones,
                "count": len(milestones)
            }
        
        else:
            return {
                "error": f"Unknown action: {action}"
            }

class RiskManagementInput(BaseModel):
    """Input schema for the risk management tool."""
    
    action: str = Field(..., description="Action to perform (create, update, delete, list)")
    risk_id: Optional[str] = Field(None, description="ID of the risk (for update/delete)")
    name: Optional[str] = Field(None, description="Name of the risk (for create/update)")
    description: Optional[str] = Field(None, description="Description of the risk (for create/update)")
    probability: Optional[str] = Field(None, description="Probability of the risk (for create/update)")
    impact: Optional[str] = Field(None, description="Impact of the risk (for create/update)")
    status: Optional[str] = Field(None, description="Status of the risk (for create/update)")
    mitigation_plan: Optional[str] = Field(None, description="Mitigation plan (for create/update)")
    contingency_plan: Optional[str] = Field(None, description="Contingency plan (for create/update)")
    owner: Optional[str] = Field(None, description="Risk owner (for create/update)")

class RiskManagementTool(BaseTool):
    """Tool for managing risks in a project."""
    
    name: str = "risk_management_tool"
    description: str = "Manage risks in a project (create, update, delete, list)"
    args_schema: Type[RiskManagementInput] = RiskManagementInput
    
    def _run(self, action: str, risk_id: Optional[str] = None, name: Optional[str] = None, 
             description: Optional[str] = None, probability: Optional[str] = None, 
             impact: Optional[str] = None, status: Optional[str] = None,
             mitigation_plan: Optional[str] = None, contingency_plan: Optional[str] = None,
             owner: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the risk management tool.
        
        Args:
            action: Action to perform (create, update, delete, list)
            risk_id: ID of the risk (for update/delete)
            name: Name of the risk (for create/update)
            description: Description of the risk (for create/update)
            probability: Probability of the risk (for create/update)
            impact: Impact of the risk (for create/update)
            status: Status of the risk (for create/update)
            mitigation_plan: Mitigation plan (for create/update)
            contingency_plan: Contingency plan (for create/update)
            owner: Risk owner (for create/update)
            
        Returns:
            Dictionary with risk information or list of risks
        """
        # In a real implementation, this would interact with a database
        # For now, we'll return mock data
        
        if action == "create":
            # Create a new risk
            new_risk = {
                "id": str(uuid.uuid4()),
                "name": name or "New Risk",
                "description": description or "Risk description",
                "probability": probability or "medium",
                "impact": impact or "medium",
                "status": status or "identified",
                "mitigation_plan": mitigation_plan,
                "contingency_plan": contingency_plan,
                "owner": owner
            }
            
            return {
                "action": "create",
                "risk": new_risk,
                "message": f"Risk '{name}' created successfully"
            }
            
        elif action == "update":
            # Update an existing risk
            if not risk_id:
                return {
                    "action": "update",
                    "error": "Risk ID is required for update action"
                }
            
            # In a real implementation, this would fetch the risk from a database
            # For now, we'll create a mock risk
            updated_risk = {
                "id": risk_id,
                "name": name or "Updated Risk",
                "description": description or "Updated risk description",
                "probability": probability or "medium",
                "impact": impact or "high",
                "status": status or "mitigated",
                "mitigation_plan": mitigation_plan,
                "contingency_plan": contingency_plan,
                "owner": owner
            }
            
            return {
                "action": "update",
                "risk": updated_risk,
                "message": f"Risk '{risk_id}' updated successfully"
            }
            
        elif action == "delete":
            # Delete an existing risk
            if not risk_id:
                return {
                    "action": "delete",
                    "error": "Risk ID is required for delete action"
                }
            
            return {
                "action": "delete",
                "risk_id": risk_id,
                "message": f"Risk '{risk_id}' deleted successfully"
            }
            
        elif action == "list":
            # List all risks
            # In a real implementation, this would fetch risks from a database
            # For now, we'll return mock risks
            risks = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Speaker Cancellation",
                    "description": "Key speaker cancels at the last minute",
                    "probability": "medium",
                    "impact": "high",
                    "status": "identified",
                    "mitigation_plan": "Confirm speakers early and have backup speakers on standby",
                    "contingency_plan": "Replace with backup speaker or adjust schedule",
                    "owner": "Stakeholder Management Agent"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Budget Overrun",
                    "description": "Project exceeds allocated budget",
                    "probability": "medium",
                    "impact": "high",
                    "status": "mitigated",
                    "mitigation_plan": "Regular budget reviews and contingency fund",
                    "contingency_plan": "Identify areas for cost reduction",
                    "owner": "Financial Agent"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Venue Issues",
                    "description": "Problems with venue availability or facilities",
                    "probability": "low",
                    "impact": "critical",
                    "status": "identified",
                    "mitigation_plan": "Site visits and detailed contract",
                    "contingency_plan": "Backup venue options identified",
                    "owner": "Resource Planning Agent"
                }
            ]
            
            return {
                "action": "list",
                "risks": risks,
                "count": len(risks)
            }
        
        else:
            return {
                "error": f"Unknown action: {action}"
            }

class TimelineGenerationInput(BaseModel):
    """Input schema for the timeline generation tool."""
    
    event_details: Dict[str, Any] = Field(..., description="Event details")
    tasks: Optional[List[Dict[str, Any]]] = Field(None, description="List of tasks (if available)")
    milestones: Optional[List[Dict[str, Any]]] = Field(None, description="List of milestones (if available)")

class TimelineGenerationTool(BaseTool):
    """Tool for generating a project timeline."""
    
    name: str = "timeline_generation_tool"
    description: str = "Generate a project timeline based on event details and tasks"
    args_schema: Type[TimelineGenerationInput] = TimelineGenerationInput
    
    def _run(self, event_details: Dict[str, Any], tasks: Optional[List[Dict[str, Any]]] = None,
             milestones: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Run the timeline generation tool.
        
        Args:
            event_details: Event details
            tasks: List of tasks (if available)
            milestones: List of milestones (if available)
            
        Returns:
            Dictionary with timeline information
        """
        # In a real implementation, this would generate a timeline based on tasks and dependencies
        # For now, we'll return a mock timeline
        
        # Extract event dates
        event_start = None
        event_end = None
        
        if event_details.get("timeline_start"):
            try:
                event_start = datetime.fromisoformat(event_details["timeline_start"])
            except (ValueError, TypeError):
                event_start = datetime.now() + timedelta(days=30)
        else:
            event_start = datetime.now() + timedelta(days=30)
            
        if event_details.get("timeline_end"):
            try:
                event_end = datetime.fromisoformat(event_details["timeline_end"])
            except (ValueError, TypeError):
                event_end = event_start + timedelta(days=1)
        else:
            event_end = event_start + timedelta(days=1)
        
        # Calculate planning period (typically 3-6 months before event)
        planning_start = event_start - timedelta(days=90)
        
        # Generate tasks if not provided
        if not tasks:
            tasks = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Initial Planning",
                    "description": "Define event scope and requirements",
                    "status": "completed",
                    "priority": "high",
                    "assigned_to": "Coordinator Agent",
                    "dependencies": [],
                    "start_date": planning_start.isoformat(),
                    "end_date": (planning_start + timedelta(days=7)).isoformat(),
                    "actual_start_date": planning_start.isoformat(),
                    "actual_end_date": (planning_start + timedelta(days=7)).isoformat(),
                    "completion_percentage": 100,
                    "notes": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Venue Selection",
                    "description": "Research and select venue",
                    "status": "completed",
                    "priority": "critical",
                    "assigned_to": "Resource Planning Agent",
                    "dependencies": [],
                    "start_date": (planning_start + timedelta(days=7)).isoformat(),
                    "end_date": (planning_start + timedelta(days=21)).isoformat(),
                    "actual_start_date": (planning_start + timedelta(days=7)).isoformat(),
                    "actual_end_date": (planning_start + timedelta(days=21)).isoformat(),
                    "completion_percentage": 100,
                    "notes": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Budget Planning",
                    "description": "Create and approve budget",
                    "status": "completed",
                    "priority": "high",
                    "assigned_to": "Financial Agent",
                    "dependencies": [],
                    "start_date": (planning_start + timedelta(days=7)).isoformat(),
                    "end_date": (planning_start + timedelta(days=21)).isoformat(),
                    "actual_start_date": (planning_start + timedelta(days=7)).isoformat(),
                    "actual_end_date": (planning_start + timedelta(days=21)).isoformat(),
                    "completion_percentage": 100,
                    "notes": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Speaker Recruitment",
                    "description": "Identify and confirm speakers",
                    "status": "in_progress",
                    "priority": "high",
                    "assigned_to": "Stakeholder Management Agent",
                    "dependencies": [],
                    "start_date": (planning_start + timedelta(days=21)).isoformat(),
                    "end_date": (event_start - timedelta(days=30)).isoformat(),
                    "actual_start_date": (planning_start + timedelta(days=21)).isoformat(),
                    "actual_end_date": None,
                    "completion_percentage": 60,
                    "notes": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Marketing Campaign",
                    "description": "Develop and execute marketing plan",
                    "status": "in_progress",
                    "priority": "high",
                    "assigned_to": "Marketing & Communications Agent",
                    "dependencies": [],
                    "start_date": (planning_start + timedelta(days=30)).isoformat(),
                    "end_date": event_start.isoformat(),
                    "actual_start_date": (planning_start + timedelta(days=30)).isoformat(),
                    "actual_end_date": None,
                    "completion_percentage": 40,
                    "notes": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Vendor Coordination",
                    "description": "Select and coordinate with vendors",
                    "status": "in_progress",
                    "priority": "medium",
                    "assigned_to": "Resource Planning Agent",
                    "dependencies": [],
                    "start_date": (planning_start + timedelta(days=30)).isoformat(),
                    "end_date": (event_start - timedelta(days=14)).isoformat(),
                    "actual_start_date": (planning_start + timedelta(days=30)).isoformat(),
                    "actual_end_date": None,
                    "completion_percentage": 50,
                    "notes": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Registration Management",
                    "description": "Set up and manage registration system",
                    "status": "not_started",
                    "priority": "medium",
                    "assigned_to": "Marketing & Communications Agent",
                    "dependencies": [],
                    "start_date": (planning_start + timedelta(days=45)).isoformat(),
                    "end_date": event_start.isoformat(),
                    "actual_start_date": None,
                    "actual_end_date": None,
                    "completion_percentage": 0,
                    "notes": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Event Setup",
                    "description": "Prepare venue and setup for event",
                    "status": "not_started",
                    "priority": "high",
                    "assigned_to": "Resource Planning Agent",
                    "dependencies": [],
                    "start_date": (event_start - timedelta(days=1)).isoformat(),
                    "end_date": event_start.isoformat(),
                    "actual_start_date": None,
                    "actual_end_date": None,
                    "completion_percentage": 0,
                    "notes": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Event Execution",
                    "description": "Run the event",
                    "status": "not_started",
                    "priority": "critical",
                    "assigned_to": "Coordinator Agent",
                    "dependencies": [],
                    "start_date": event_start.isoformat(),
                    "end_date": event_end.isoformat(),
                    "actual_start_date": None,
                    "actual_end_date": None,
                    "completion_percentage": 0,
                    "notes": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Post-Event Analysis",
                    "description": "Analyze event performance and gather feedback",
                    "status": "not_started",
                    "priority": "medium",
                    "assigned_to": "Coordinator Agent",
                    "dependencies": [],
                    "start_date": (event_end + timedelta(days=1)).isoformat(),
                    "end_date": (event_end + timedelta(days=14)).isoformat(),
                    "actual_start_date": None,
                    "actual_end_date": None,
                    "completion_percentage": 0,
                    "notes": None
                }
            ]
        
        # Generate milestones if not provided
        if not milestones:
            milestones = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Planning Complete",
                    "description": "All initial planning tasks completed",
                    "date": (planning_start + timedelta(days=21)).isoformat(),
                    "status": "reached",
                    "associated_tasks": []
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Marketing Launch",
                    "description": "Official marketing campaign launch",
                    "date": (planning_start + timedelta(days=30)).isoformat(),
                    "status": "reached",
                    "associated_tasks": []
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "All Speakers Confirmed",
                    "description": "All speakers have confirmed their participation",
                    "date": (event_start - timedelta(days=30)).isoformat(),
                    "status": "not_reached",
                    "associated_tasks": []
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Registration Deadline",
                    "description": "Deadline for attendee registration",
                    "date": (event_start - timedelta(days=7)).isoformat(),
                    "status": "not_reached",
                    "associated_tasks": []
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Event Day",
                    "description": "Main event day",
                    "date": event_start.isoformat(),
                    "status": "not_reached",
                    "associated_tasks": []
                }
            ]
        
        # Identify critical path (simplified approach)
        # In a real implementation, this would use a proper critical path algorithm
        critical_path = [task["id"] for task in tasks if task["priority"] == "critical"]
        
        # Create timeline
        timeline = {
            "tasks": tasks,
            "milestones": milestones,
            "critical_path": critical_path,
            "start_date": planning_start.isoformat(),
            "end_date": (event_end + timedelta(days=14)).isoformat()  # Include post-event tasks
        }
        
        return {
            "timeline": timeline,
            "message": "Timeline generated successfully"
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class ProjectPlanGenerationInput(BaseModel):
    """Input schema for the project plan generation tool."""
    
    event_id: str = Field(..., description="ID of the event")
    event_details: Dict[str, Any] = Field(..., description="Event details")
    timeline: Optional[Dict[str, Any]] = Field(None, description="Timeline information (if available)")
    tasks: Optional[List[Dict[str, Any]]] = Field(None, description="List of tasks (if available)")
    milestones: Optional[List[Dict[str, Any]]] = Field(None, description="List of milestones (if available)")
    risks: Optional[List[Dict[str, Any]]] = Field(None, description="List of risks (if available)")

class ProjectPlanGenerationTool(BaseTool):
    """Tool for generating a comprehensive project plan."""
    
    name: str = "project_plan_generation_tool"
    description: str = "Generate a comprehensive project plan for an event"
    args_schema: Type[ProjectPlanGenerationInput] = ProjectPlanGenerationInput
    
    def _run(self, event_id: str, event_details: Dict[str, Any], 
             timeline: Optional[Dict[str, Any]] = None, tasks: Optional[List[Dict[str, Any]]] = None,
             milestones: Optional[List[Dict[str, Any]]] = None, 
             risks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Run the project plan generation tool.
        
        Args:
            event_id: ID of the event
            event_details: Event details
            timeline: Timeline information (if available)
            tasks: List of tasks (if available)
            milestones: List of milestones (if available)
            risks: List of risks (if available)
            
        Returns:
            Dictionary with project plan information
        """
        # In a real implementation, this would generate a comprehensive project plan
        # For now, we'll return a mock project plan
        
        # Generate timeline if not provided
        if not timeline or not tasks or not milestones:
            timeline_tool = TimelineGenerationTool()
            timeline_result = timeline_tool._run(event_details=event_details)
            timeline = timeline_result["timeline"]
            tasks = timeline["tasks"]
            milestones = timeline["milestones"]
        
        # Generate risks if not provided
        if not risks:
            risk_tool = RiskManagementTool()
            risk_result = risk_tool._run(action="list")
            risks = risk_result["risks"]
        
        # Calculate overall status
        completed_tasks = sum(1 for task in tasks if task["status"] == "completed")
        in_progress_tasks = sum(1 for task in tasks if task["status"] == "in_progress")
        total_tasks = len(tasks)
        
        if total_tasks == 0:
            status_summary = "No tasks defined"
        elif completed_tasks == total_tasks:
            status_summary = "Complete"
        elif completed_tasks + in_progress_tasks == 0:
            status_summary = "Not started"
        else:
            completion_percentage = int((completed_tasks / total_tasks) * 100)
            status_summary = f"In progress ({completion_percentage}% complete)"
        
        # Create project plan
        project_plan = {
            "id": str(uuid.uuid4()),
            "event_id": event_id,
            "timeline": timeline,
            "tasks": tasks,
            "milestones": milestones,
            "risks": risks,
            "status_summary": status_summary,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        return {
            "project_plan": project_plan,
            "message": "Project plan generated successfully"
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)
