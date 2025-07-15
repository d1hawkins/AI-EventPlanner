from typing import Dict, Any, List, Optional, Type, Tuple
from datetime import datetime
import traceback
import json
import logging
from datetime import datetime

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.graphs.resource_planning_graph import create_resource_planning_graph, create_initial_state as create_resource_planning_initial_state
from app.graphs.financial_graph import create_financial_graph, create_initial_state as create_financial_initial_state
from app.graphs.stakeholder_management_graph import create_stakeholder_management_graph, create_initial_state as create_stakeholder_management_initial_state
from app.graphs.marketing_communications_graph import create_marketing_communications_graph, create_initial_state as create_marketing_communications_initial_state
from app.graphs.project_management_graph import create_project_management_graph, create_initial_state as create_project_management_initial_state
from app.graphs.analytics_graph import create_analytics_graph, create_initial_state as create_analytics_initial_state
from app.graphs.compliance_security_graph import create_compliance_security_graph, create_initial_state as create_compliance_security_initial_state
from app.utils.logging_utils_local import setup_logger, log_agent_invocation, log_agent_response, log_agent_error

# Set up logger
logger = setup_logger("agent_communication", log_level="DEBUG")


# Error categories for better error handling
ERROR_CATEGORIES = {
    "INITIALIZATION": "Agent initialization error",
    "INVOCATION": "Agent invocation error",
    "RESPONSE": "Agent response error",
    "TIMEOUT": "Agent timeout error",
    "TOKEN_LIMIT": "Token limit exceeded",
    "INVALID_INPUT": "Invalid input to agent",
    "UNKNOWN": "Unknown error"
}


class ProjectManagementTaskInput(BaseModel):
    """Input schema for the project management task tool."""
    
    task: str = Field(..., description="Task to delegate to the Project Management Agent")
    event_details: Dict[str, Any] = Field(..., description="Event details to provide to the Project Management Agent")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Additional requirements for the task")


class ResourcePlanningTaskInput(BaseModel):
    """Input schema for the resource planning task tool."""
    
    task: str = Field(..., description="Task to delegate to the Resource Planning Agent")
    event_details: Dict[str, Any] = Field(..., description="Event details to provide to the Resource Planning Agent")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Additional requirements for the task")


class StakeholderManagementTaskInput(BaseModel):
    """Input schema for the stakeholder management task tool."""
    
    task: str = Field(..., description="Task to delegate to the Stakeholder Management Agent")
    event_details: Dict[str, Any] = Field(..., description="Event details to provide to the Stakeholder Management Agent")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Additional requirements for the task")


class MarketingCommunicationsTaskInput(BaseModel):
    """Input schema for the marketing and communications task tool."""
    
    task: str = Field(..., description="Task to delegate to the Marketing & Communications Agent")
    event_details: Dict[str, Any] = Field(..., description="Event details to provide to the Marketing & Communications Agent")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Additional requirements for the task")


class FinancialTaskInput(BaseModel):
    """Input schema for the financial task tool."""
    
    task: str = Field(..., description="Task to delegate to the Financial Agent")
    event_details: Dict[str, Any] = Field(..., description="Event details to provide to the Financial Agent")
    budget: Optional[Dict[str, Any]] = Field(None, description="Budget information for the task")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Additional requirements for the task")


class AnalyticsTaskInput(BaseModel):
    """Input schema for the analytics task tool."""
    
    task: str = Field(..., description="Task to delegate to the Analytics Agent")
    event_details: Dict[str, Any] = Field(..., description="Event details to provide to the Analytics Agent")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Additional requirements for the task")


class ComplianceSecurityTaskInput(BaseModel):
    """Input schema for the compliance and security task tool."""
    
    task: str = Field(..., description="Task to delegate to the Compliance & Security Agent")
    event_details: Dict[str, Any] = Field(..., description="Event details to provide to the Compliance & Security Agent")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Additional requirements for the task")


# Set up logger
logger = logging.getLogger(__name__)

class ResourcePlanningTaskTool(BaseTool):
    """Tool for delegating tasks to the Resource Planning Agent."""
    
    name: str = "resource_planning_task_tool"
    description: str = "Delegate a task to the Resource Planning Agent"
    args_schema: Type[ResourcePlanningTaskInput] = ResourcePlanningTaskInput
    
    def _handle_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """
        Handle errors that occur during agent invocation.
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
            
        Returns:
            Dictionary with error information
        """
        # Determine error category
        error_category = "UNKNOWN"
        error_message = str(error)
        
        if "timeout" in error_message.lower():
            error_category = "TIMEOUT"
        elif "token" in error_message.lower() and ("limit" in error_message.lower() or "exceed" in error_message.lower()):
            error_category = "TOKEN_LIMIT"
        elif "invalid" in error_message.lower() and "input" in error_message.lower():
            error_category = "INVALID_INPUT"
        elif "initialize" in error_message.lower() or "create" in error_message.lower():
            error_category = "INITIALIZATION"
        elif "invoke" in error_message.lower() or "run" in error_message.lower():
            error_category = "INVOCATION"
        elif "response" in error_message.lower() or "result" in error_message.lower():
            error_category = "RESPONSE"
        
        # Log the error
        log_agent_error(logger, "Resource Planning", error, context)
        
        # Create a detailed error message
        detailed_error = {
            "error_category": error_category,
            "error_type": ERROR_CATEGORIES.get(error_category, "Unknown error"),
            "error_message": error_message,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "stack_trace": traceback.format_exc()
        }
        
        # Create a user-friendly error message
        user_message = f"Error in Resource Planning Agent: {ERROR_CATEGORIES.get(error_category, 'Unknown error')}"
        
        if error_category == "TOKEN_LIMIT":
            user_message += "\n\nThe task may be too complex for the current model. Try breaking it down into smaller tasks or providing less detailed requirements."
        elif error_category == "TIMEOUT":
            user_message += "\n\nThe agent took too long to respond. This might be due to high server load or a complex task. Please try again later or simplify the task."
        elif error_category == "INVALID_INPUT":
            user_message += "\n\nThe input provided to the agent was invalid. Please check the task description and requirements and try again."
        
        return {
            "task": context,
            "response": user_message,
            "error": detailed_error,
            "resource_plan": None,
            "venue_options": [],
            "selected_venue": None,
            "service_providers": [],
            "equipment_needs": []
        }
    
    def _run(self, task: str, event_details: Dict[str, Any], requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the resource planning task tool.
        
        Args:
            task: Task to delegate
            event_details: Event details
            requirements: Additional requirements
            
        Returns:
            Dictionary with task results
        """
        # Log the invocation
        log_agent_invocation(logger, "Resource Planning", task)
        print(f"Delegating task to Resource Planning Agent: {task}")
        
        try:
            # Create the resource planning graph
            logger.info("Creating Resource Planning graph")
            resource_planning_graph = create_resource_planning_graph()
            
            # Create initial state
            logger.info("Creating initial state for Resource Planning Agent")
            state = create_resource_planning_initial_state()
            
            # Update state with event details
            for key, value in event_details.items():
                if key in state["event_details"]:
                    state["event_details"][key] = value
            
            # Add initial message
            state["messages"].append({
                "role": "system",
                "content": "The Frontend Coordinator Agent has delegated a task to you.",
                "ephemeral": True
            })
            
            # Add task message
            task_message = f"Task: {task}\n\n"
            if requirements:
                task_message += "Requirements:\n"
                for key, value in requirements.items():
                    task_message += f"- {key}: {value}\n"
            
            state["messages"].append({
                "role": "user",
                "content": task_message
            })
            
            # Log the state preparation
            logger.debug(f"Prepared state for Resource Planning Agent with task: {task}")
            
            # DEBUG: Print state before invoking graph
            print(f"DEBUG: State before invoking resource planning graph for task '{task}':")
            import pprint
            pprint.pprint(state)
            print("-" * 20)
            
            # Run the resource planning graph
            logger.info("Invoking Resource Planning graph")
            try:
                result = resource_planning_graph.invoke(state)
                logger.info("Resource Planning graph invocation successful")
            except Exception as e:
                logger.error(f"Error during Resource Planning graph invocation: {str(e)}", exc_info=True)
                return self._handle_error(e, f"Error invoking Resource Planning Agent with task: {task}")
            
            # Extract the response
            assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
            if assistant_messages:
                response = assistant_messages[-1]["content"]
                logger.info(f"Received response from Resource Planning Agent: {response[:100]}...")
            else:
                logger.warning("No response received from Resource Planning Agent")
                response = "No response from Resource Planning Agent. This could be due to an error in processing your request or insufficient information provided."
            
            # Determine the appropriate next action based on the task
            next_action = None
            if "venue" in task.lower() or "location" in task.lower():
                next_action = "search_venues"
                logger.info("Determined next action: search_venues")
            elif "service" in task.lower() or "provider" in task.lower():
                next_action = "search_service_providers"
                logger.info("Determined next action: search_service_providers")
            elif "equipment" in task.lower() or "resource" in task.lower():
                next_action = "plan_equipment"
                logger.info("Determined next action: plan_equipment")
            elif "plan" in task.lower():
                next_action = "generate_resource_plan"
                logger.info("Determined next action: generate_resource_plan")
            
            # If a specific next action is determined, run that action
            if next_action:
                logger.info(f"Invoking Resource Planning graph with next action: {next_action}")
                try:
                    result = resource_planning_graph.invoke(result, {"override_next": next_action})
                    logger.info(f"Resource Planning graph invocation with {next_action} successful")
                    
                    # Extract the updated response
                    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
                    if assistant_messages:
                        response = assistant_messages[-1]["content"]
                        logger.info(f"Updated response from Resource Planning Agent: {response[:100]}...")
                except Exception as e:
                    logger.error(f"Error during Resource Planning graph invocation with next action {next_action}: {str(e)}", exc_info=True)
                    # Continue with the previous response instead of failing completely
                    logger.info("Continuing with previous response due to error in next action")
            
            # Log the response
            log_agent_response(logger, "Resource Planning", response)
            
            # Return the result
            return {
                "task": task,
                "response": response,
                "resource_plan": result.get("resource_plan"),
                "venue_options": result.get("venue_options", []),
                "selected_venue": result.get("selected_venue"),
                "service_providers": result.get("service_providers", []),
                "equipment_needs": result.get("equipment_needs", [])
            }
        except Exception as e:
            # Handle any unexpected errors
            return self._handle_error(e, f"Unexpected error in Resource Planning Agent with task: {task}")
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class ComplianceSecurityTaskTool(BaseTool):
    """Tool for delegating tasks to the Compliance & Security Agent."""
    
    name: str = "compliance_security_task_tool"
    description: str = "Delegate a task to the Compliance & Security Agent"
    args_schema: Type[ComplianceSecurityTaskInput] = ComplianceSecurityTaskInput
    
    def _run(self, task: str, event_details: Dict[str, Any], requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the compliance and security task tool.
        
        Args:
            task: Task to delegate
            event_details: Event details
            requirements: Additional requirements
            
        Returns:
            Dictionary with task results
        """
        print(f"Delegating task to Compliance & Security Agent: {task}")
        
        # Create the compliance and security graph
        compliance_security_graph = create_compliance_security_graph()
        
        # Create initial state
        state = create_compliance_security_initial_state()
        
        # Update state with event details
        for key, value in event_details.items():
            if key in state["event_details"]:
                state["event_details"][key] = value
        
        # Add initial message
        state["messages"].append({
            "role": "system",
            "content": "The Frontend Coordinator Agent has delegated a task to you.",
            "ephemeral": True
        })
        
        # Add task message
        task_message = f"Task: {task}\n\n"
        if requirements:
            task_message += "Requirements:\n"
            for key, value in requirements.items():
                task_message += f"- {key}: {value}\n"
        
        state["messages"].append({
            "role": "user",
            "content": task_message
        })
        
        # Run the compliance and security graph
        result = compliance_security_graph.invoke(state)
        
        # Extract the response
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        response = assistant_messages[-1]["content"] if assistant_messages else "No response from Compliance & Security Agent"
        
        # Determine the appropriate next action based on the task
        next_action = None
        if "requirement" in task.lower() or "regulation" in task.lower() or "compliance" in task.lower():
            next_action = "track_requirements"
        elif "security" in task.lower() or "access control" in task.lower() or "physical security" in task.lower():
            next_action = "plan_security"
        elif "data protection" in task.lower() or "privacy" in task.lower() or "gdpr" in task.lower():
            next_action = "implement_data_protection"
        elif "audit" in task.lower() or "assessment" in task.lower() or "verify" in task.lower():
            next_action = "conduct_audit"
        elif "incident" in task.lower() or "response" in task.lower() or "emergency" in task.lower():
            next_action = "plan_incident_response"
        elif "report" in task.lower() or "documentation" in task.lower():
            next_action = "generate_report"
        elif "update" in task.lower() or "regulatory change" in task.lower():
            next_action = "monitor_updates"
        
        # If a specific next action is determined, run that action
        if next_action:
            result = compliance_security_graph.invoke(result, {"override_next": next_action})
            # Extract the updated response
            assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
            response = assistant_messages[-1]["content"] if assistant_messages else response
        
        # Return the result
        return {
            "task": task,
            "response": response,
            "compliance_requirements": result.get("compliance_requirements", []),
            "security_protocols": result.get("security_protocols", []),
            "data_protection_measures": result.get("data_protection_measures", []),
            "compliance_audits": result.get("compliance_audits", []),
            "incident_response_plans": result.get("incident_response_plans", []),
            "compliance_reports": result.get("compliance_reports", []),
            "regulatory_updates": result.get("regulatory_updates", [])
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class AnalyticsTaskTool(BaseTool):
    """Tool for delegating tasks to the Analytics Agent."""
    
    name: str = "analytics_task_tool"
    description: str = "Delegate a task to the Analytics Agent"
    args_schema: Type[AnalyticsTaskInput] = AnalyticsTaskInput
    
    def _run(self, task: str, event_details: Dict[str, Any], requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the analytics task tool.
        
        Args:
            task: Task to delegate
            event_details: Event details
            requirements: Additional requirements
            
        Returns:
            Dictionary with task results
        """
        print(f"Delegating task to Analytics Agent: {task}")
        
        # Create the analytics graph
        analytics_graph = create_analytics_graph()
        
        # Create initial state
        state = create_analytics_initial_state()
        
        # Update state with event details
        for key, value in event_details.items():
            if key in state["event_details"]:
                state["event_details"][key] = value
        
        # Add initial message
        state["messages"].append({
            "role": "system",
            "content": "The Frontend Coordinator Agent has delegated a task to you.",
            "ephemeral": True
        })
        
        # Add task message
        task_message = f"Task: {task}\n\n"
        if requirements:
            task_message += "Requirements:\n"
            for key, value in requirements.items():
                task_message += f"- {key}: {value}\n"
        
        state["messages"].append({
            "role": "user",
            "content": task_message
        })
        
        # Run the analytics graph
        result = analytics_graph.invoke(state)
        
        # Extract the response
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        response = assistant_messages[-1]["content"] if assistant_messages else "No response from Analytics Agent"
        
        # Determine the appropriate next action based on the task
        next_action = None
        if "data" in task.lower() or "collect" in task.lower():
            next_action = "configure_data_sources"
        elif "metric" in task.lower() or "kpi" in task.lower():
            next_action = "define_metrics"
        elif "segment" in task.lower() or "audience" in task.lower():
            next_action = "create_segments"
        elif "survey" in task.lower() or "feedback" in task.lower():
            next_action = "design_surveys"
        elif "report" in task.lower() or "analysis" in task.lower():
            next_action = "generate_reports"
        elif "roi" in task.lower() or "return" in task.lower():
            next_action = "calculate_roi"
        elif "attendee" in task.lower() or "demographic" in task.lower():
            next_action = "analyze_attendees"
        elif "insight" in task.lower() or "recommend" in task.lower():
            next_action = "generate_insights"
        
        # If a specific next action is determined, run that action
        if next_action:
            result = analytics_graph.invoke(result, {"override_next": next_action})
            # Extract the updated response
            assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
            response = assistant_messages[-1]["content"] if assistant_messages else response
        
        # Return the result
        return {
            "task": task,
            "response": response,
            "data_sources": result.get("data_sources", []),
            "metrics": result.get("metrics", []),
            "segments": result.get("segments", []),
            "surveys": result.get("surveys", []),
            "reports": result.get("reports", []),
            "roi_analysis": result.get("roi_analysis"),
            "attendee_analytics": result.get("attendee_analytics"),
            "insights": result.get("insights", [])
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class MarketingCommunicationsTaskTool(BaseTool):
    """Tool for delegating tasks to the Marketing & Communications Agent."""
    
    name: str = "marketing_communications_task_tool"
    description: str = "Delegate a task to the Marketing & Communications Agent"
    args_schema: Type[MarketingCommunicationsTaskInput] = MarketingCommunicationsTaskInput
    
    def _run(self, task: str, event_details: Dict[str, Any], requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the marketing and communications task tool.
        
        Args:
            task: Task to delegate
            event_details: Event details
            requirements: Additional requirements
            
        Returns:
            Dictionary with task results
        """
        print(f"Delegating task to Marketing & Communications Agent: {task}")
        
        # Create the marketing communications graph
        marketing_graph = create_marketing_communications_graph()
        
        # Create initial state
        state = create_marketing_communications_initial_state()
        
        # Update state with event details
        for key, value in event_details.items():
            if key in state["event_details"]:
                state["event_details"][key] = value
        
        # Add initial message
        state["messages"].append({
            "role": "system",
            "content": "The Frontend Coordinator Agent has delegated a task to you.",
            "ephemeral": True
        })
        
        # Add task message
        task_message = f"Task: {task}\n\n"
        if requirements:
            task_message += "Requirements:\n"
            for key, value in requirements.items():
                task_message += f"- {key}: {value}\n"
        
        state["messages"].append({
            "role": "user",
            "content": task_message
        })
        
        # Run the marketing communications graph
        result = marketing_graph.invoke(state)
        
        # Extract the response
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        response = assistant_messages[-1]["content"] if assistant_messages else "No response from Marketing & Communications Agent"
        
        # Determine the appropriate next action based on the task
        next_action = None
        if "channel" in task.lower() or "platform" in task.lower():
            next_action = "manage_channels"
        elif "content" in task.lower() or "post" in task.lower() or "message" in task.lower():
            next_action = "create_content"
        elif "attendee" in task.lower() or "registration" in task.lower():
            next_action = "manage_attendees"
        elif "form" in task.lower():
            next_action = "create_registration_form"
        elif "campaign" in task.lower() or "promotion" in task.lower():
            next_action = "create_campaign"
        elif "marketing plan" in task.lower() or "strategy" in task.lower():
            next_action = "generate_marketing_plan"
        elif "communication plan" in task.lower() or "stakeholder" in task.lower():
            next_action = "generate_communication_plan"
        
        # If a specific next action is determined, run that action
        if next_action:
            result = marketing_graph.invoke(result, {"override_next": next_action})
            # Extract the updated response
            assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
            response = assistant_messages[-1]["content"] if assistant_messages else response
        
        # Return the result
        return {
            "task": task,
            "response": response,
            "channels": result.get("channels", []),
            "content": result.get("content", []),
            "attendees": result.get("attendees", []),
            "registration_forms": result.get("registration_forms", []),
            "campaigns": result.get("campaigns", []),
            "marketing_plan": result.get("marketing_plan"),
            "communication_plan": result.get("communication_plan")
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class StakeholderManagementTaskTool(BaseTool):
    """Tool for delegating tasks to the Stakeholder Management Agent."""
    
    name: str = "stakeholder_management_task_tool"
    description: str = "Delegate a task to the Stakeholder Management Agent"
    args_schema: Type[StakeholderManagementTaskInput] = StakeholderManagementTaskInput
    
    def _run(self, task: str, event_details: Dict[str, Any], requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the stakeholder management task tool.
        
        Args:
            task: Task to delegate
            event_details: Event details
            requirements: Additional requirements
            
        Returns:
            Dictionary with task results
        """
        print(f"Delegating task to Stakeholder Management Agent: {task}")
        
        # Create the stakeholder management graph
        stakeholder_management_graph = create_stakeholder_management_graph()
        
        # Create initial state
        state = create_stakeholder_management_initial_state()
        
        # Update state with event details
        for key, value in event_details.items():
            if key in state["event_details"]:
                state["event_details"][key] = value
        
        # Add initial message
        state["messages"].append({
            "role": "system",
            "content": "The Frontend Coordinator Agent has delegated a task to you.",
            "ephemeral": True
        })
        
        # Add task message
        task_message = f"Task: {task}\n\n"
        if requirements:
            task_message += "Requirements:\n"
            for key, value in requirements.items():
                task_message += f"- {key}: {value}\n"
        
        state["messages"].append({
            "role": "user",
            "content": task_message
        })
        
        # Run the stakeholder management graph
        result = stakeholder_management_graph.invoke(state)
        
        # Extract the response
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        response = assistant_messages[-1]["content"] if assistant_messages else "No response from Stakeholder Management Agent"
        
        # Determine the appropriate next action based on the task
        next_action = None
        if "speaker" in task.lower() or "presenter" in task.lower():
            next_action = "manage_speakers"
        elif "sponsor" in task.lower() or "funding" in task.lower():
            next_action = "manage_sponsors"
        elif "volunteer" in task.lower() or "staff" in task.lower():
            next_action = "manage_volunteers"
        elif "vip" in task.lower() or "important guest" in task.lower():
            next_action = "manage_vips"
        elif "plan" in task.lower() or "strategy" in task.lower():
            next_action = "generate_stakeholder_plan"
        
        # If a specific next action is determined, run that action
        if next_action:
            result = stakeholder_management_graph.invoke(result, {"override_next": next_action})
            # Extract the updated response
            assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
            response = assistant_messages[-1]["content"] if assistant_messages else response
        
        # Return the result
        return {
            "task": task,
            "response": response,
            "stakeholder_plan": result.get("stakeholder_plan"),
            "speakers": result.get("speakers", []),
            "sponsors": result.get("sponsors", []),
            "volunteers": result.get("volunteers", []),
            "vips": result.get("vips", [])
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class ProjectManagementTaskTool(BaseTool):
    """Tool for delegating tasks to the Project Management Agent."""
    
    name: str = "project_management_task_tool"
    description: str = "Delegate a task to the Project Management Agent"
    args_schema: Type[ProjectManagementTaskInput] = ProjectManagementTaskInput
    
    def _run(self, task: str, event_details: Dict[str, Any], requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the project management task tool.
        
        Args:
            task: Task to delegate
            event_details: Event details
            requirements: Additional requirements
            
        Returns:
            Dictionary with task results
        """
        print(f"Delegating task to Project Management Agent: {task}")
        
        # Create the project management graph
        project_management_graph = create_project_management_graph()
        
        # Create initial state
        state = create_project_management_initial_state()
        
        # Update state with event details
        for key, value in event_details.items():
            if key in state["event_details"]:
                state["event_details"][key] = value
        
        # Add initial message
        state["messages"].append({
            "role": "system",
            "content": "The Frontend Coordinator Agent has delegated a task to you.",
            "ephemeral": True
        })
        
        # Add task message
        task_message = f"Task: {task}\n\n"
        if requirements:
            task_message += "Requirements:\n"
            for key, value in requirements.items():
                task_message += f"- {key}: {value}\n"
        
        state["messages"].append({
            "role": "user",
            "content": task_message
        })
        
        # Run the project management graph
        result = project_management_graph.invoke(state)
        
        # Extract the response
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        response = assistant_messages[-1]["content"] if assistant_messages else "No response from Project Management Agent"
        
        # Determine the appropriate next action based on the task
        next_action = None
        if "task" in task.lower() or "assignment" in task.lower():
            next_action = "manage_tasks"
        elif "milestone" in task.lower() or "deadline" in task.lower():
            next_action = "manage_milestones"
        elif "risk" in task.lower() or "issue" in task.lower():
            next_action = "manage_risks"
        elif "timeline" in task.lower() or "schedule" in task.lower():
            next_action = "generate_timeline"
        elif "plan" in task.lower() or "project plan" in task.lower():
            next_action = "generate_project_plan"
        
        # If a specific next action is determined, run that action
        if next_action:
            result = project_management_graph.invoke(result, {"override_next": next_action})
            # Extract the updated response
            assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
            response = assistant_messages[-1]["content"] if assistant_messages else response
        
        # Return the result
        return {
            "task": task,
            "response": response,
            "tasks": result.get("tasks", []),
            "milestones": result.get("milestones", []),
            "risks": result.get("risks", []),
            "timeline": result.get("timeline"),
            "project_plan": result.get("project_plan")
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class FinancialTaskTool(BaseTool):
    """Tool for delegating tasks to the Financial Agent."""
    
    name: str = "financial_task_tool"
    description: str = "Delegate a task to the Financial Agent"
    args_schema: Type[FinancialTaskInput] = FinancialTaskInput
    
    def _run(self, task: str, event_details: Dict[str, Any], 
             budget: Optional[Dict[str, Any]] = None,
             requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the financial task tool.
        
        Args:
            task: Task to delegate
            event_details: Event details
            budget: Budget information
            requirements: Additional requirements
            
        Returns:
            Dictionary with task results
        """
        print(f"Delegating task to Financial Agent: {task}")
        
        # Create the financial graph
        financial_graph = create_financial_graph()
        
        # Create initial state
        state = create_financial_initial_state()
        
        # Update state with event details
        for key, value in event_details.items():
            if key in state["event_details"]:
                state["event_details"][key] = value
        
        # Update state with budget if provided
        if budget:
            state["budget"] = budget
        
        # Add initial message
        state["messages"].append({
            "role": "system",
            "content": "The Frontend Coordinator Agent has delegated a task to you.",
            "ephemeral": True
        })
        
        # Add task message
        task_message = f"Task: {task}\n\n"
        if requirements:
            task_message += "Requirements:\n"
            for key, value in requirements.items():
                task_message += f"- {key}: {value}\n"
        
        state["messages"].append({
            "role": "user",
            "content": task_message
        })
        
        # Run the financial graph
        result = financial_graph.invoke(state)
        
        # Extract the response
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        response = assistant_messages[-1]["content"] if assistant_messages else "No response from Financial Agent"
        
        # Determine the appropriate next action based on the task
        next_action = None
        if "budget" in task.lower() or "allocate" in task.lower():
            next_action = "allocate_budget"
        elif "expense" in task.lower() or "payment" in task.lower() or "track" in task.lower():
            next_action = "track_expenses"
        elif "contract" in task.lower():
            next_action = "manage_contracts"
        elif "report" in task.lower():
            next_action = "generate_financial_report"
        elif "plan" in task.lower():
            next_action = "generate_financial_plan"
        
        # If a specific next action is determined, run that action
        if next_action:
            result = financial_graph.invoke(result, {"override_next": next_action})
            # Extract the updated response
            assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
            response = assistant_messages[-1]["content"] if assistant_messages else response
        
        # Return the result
        return {
            "task": task,
            "response": response,
            "budget": result.get("budget"),
            "expenses": result.get("expenses", []),
            "contracts": result.get("contracts", []),
            "financial_plan": result.get("financial_plan")
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)
