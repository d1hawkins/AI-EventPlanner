from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.utils.llm_factory import get_llm
from app.tools.event_tools import RequirementsTool, DelegationTool, MonitoringTool, ReportingTool
from app.tools.agent_communication_tools import ResourcePlanningTaskTool, FinancialTaskTool, StakeholderManagementTaskTool, MarketingCommunicationsTaskTool, ProjectManagementTaskTool
from app.tools.coordinator_search_tool import CoordinatorSearchTool
from app.schemas.event import EventDetails, Requirements, AgentAssignment


# Define the state schema as a regular dict to avoid TypedDict compatibility issues
# This avoids the issubclass() error in Azure environment


# Define the system prompt
COORDINATOR_SYSTEM_PROMPT = """You are the Frontend Coordinator Agent for an event planning system. Your role is to:

1. Interface with users to understand their event planning needs
2. Gather comprehensive requirements for events
3. Create detailed event proposals with recommendations (without validating availability)
4. Delegate tasks to specialized agents, including validation tasks
5. Monitor progress and provide status updates
6. Ensure a cohesive event planning experience

You have access to the following specialized agents:
- Resource Planning Agent: Handles venue selection, service providers, equipment
- Financial Agent: Manages budget, payments, contracts
- Stakeholder Management Agent: Coordinates sponsors, speakers, volunteers
- Marketing & Communications Agent: Manages campaigns, website, attendee communications
- Project Management Agent: Tracks tasks, timeline, risks
- Analytics Agent: Collects data, analyzes performance
- Compliance & Security Agent: Ensures legal requirements, security protocols

Your current conversation state:
Current phase: {current_phase}
Event details: {event_details}
Requirements: {requirements}
Agent assignments: {agent_assignments}
Next steps: {next_steps}
Information collected: {information_collected}

IMPORTANT: Your primary goal is to collect comprehensive information about the event before creating a proposal. Follow these guidelines:

1. If this is a new conversation, begin by explaining your role and asking about the basic event details.
2. Systematically collect information in all required categories (see information_collected status).
3. Ask focused questions to gather missing information.
4. Once all required information is collected, generate a comprehensive detailed proposal with recommendations.
   - When making recommendations for venues, dates, speakers, vendors, or any other resources, DO NOT validate their availability.
   - Simply recommend possibilities that match the requirements.
   - Clearly indicate in the proposal that all recommendations are subject to availability validation.
5. Ask the user for approval on the proposal before proceeding.
6. Make revisions to the proposal if needed.
7. After the proposal is approved, create a detailed comprehensive project plan.
   - Include specific validation tasks for all recommended resources (venues, speakers, vendors, etc.).
   - These validation tasks will be assigned to the appropriate specialized agents.
8. Ask the user for approval on the project plan before proceeding.
9. Delegate tasks to specialized agents based on the project plan, including validation tasks.

Respond to the user in a helpful, professional manner. Ask clarifying questions when needed to gather complete requirements. Provide clear updates on the event planning progress.
"""

# Define the information collection categories
INFORMATION_CATEGORIES = [
    "basic_details",      # Event type, title, description, attendee count, scale
    "timeline",           # Start/end dates, key milestones, setup/teardown
    "budget",             # Budget range, allocation priorities, payment timeline
    "location",           # Geographic preferences, venue type, space requirements
    "stakeholders",       # Key stakeholders, speakers, sponsors, VIPs
    "resources",          # Equipment, staffing, service providers
    "success_criteria",   # Goals, KPIs, expected outcomes
    "risks"               # Challenges, contingencies, insurance
]


def create_coordinator_graph():
    """
    Create the coordinator agent graph.
    
    Returns:
        Compiled LangGraph for the coordinator agent
    """
    # Initialize the LLM
    llm = get_llm(temperature=0.2)
    
    # Initialize tools
    tools = [
        RequirementsTool(),
        DelegationTool(),
        MonitoringTool(),
        ReportingTool(),
        ResourcePlanningTaskTool(),
        FinancialTaskTool(),
        StakeholderManagementTaskTool(),
        MarketingCommunicationsTaskTool(),
        ProjectManagementTaskTool(),
        CoordinatorSearchTool()
    ]
    
    # Create the tool node
    tool_node = ToolNode(tools)
    
    # Define the nodes
    def assess_request(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the user's request and determine the next action.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with next node to execute
        """
        # Get the last message
        last_message = state["messages"][-1]["content"] if state["messages"] else ""
        current_phase = state["current_phase"]
        
        # For new conversations or initial messages, always start with information gathering
        if len(state["messages"]) <= 1:  # Only system message or first user message
            state["current_phase"] = "information_collection"
            state["next_action"] = "gather_requirements"
            return state
        
        # Check if all information has been collected
        all_info_collected = all(state["information_collected"].values())
        
        # Check if we need to generate a proposal - only if ALL information is collected
        if all_info_collected and current_phase == "information_collection" and "proposal" not in state:
            # Double check that we have meaningful information before generating proposal
            has_meaningful_info = (
                state["event_details"]["event_type"] is not None and
                state["event_details"]["title"] is not None and
                (state["event_details"]["timeline_start"] is not None or 
                 state["event_details"]["timeline_end"] is not None)
            )
            
            if has_meaningful_info:
                state["next_action"] = "generate_proposal"
                return state
            else:
                # If we don't have meaningful info, continue gathering requirements
                state["next_action"] = "gather_requirements"
                return state
            
        # Check if proposal has been approved
        if current_phase == "proposal_review" and any(keyword in last_message.lower() for keyword in ["approve", "approved", "accept", "accepted", "good", "proceed", "go ahead"]):
            state["current_phase"] = "task_delegation"
            state["next_action"] = "delegate_tasks"
            return state
            
        # Simple keyword-based routing
        if any(keyword in last_message.lower() for keyword in ["what type", "when is", "how many", "requirements", "details", "information"]):
            state["next_action"] = "gather_requirements"
        elif any(keyword in last_message.lower() for keyword in ["assign", "delegate", "task", "responsibility"]):
            state["next_action"] = "delegate_tasks"
        elif any(keyword in last_message.lower() for keyword in ["status", "progress", "update", "report"]):
            state["next_action"] = "provide_status"
        elif any(keyword in last_message.lower() for keyword in ["proposal", "plan", "summary"]) and current_phase != "proposal_review":
            # Only generate proposal if explicitly requested AND we have some information
            if any(state["information_collected"].values()):
                state["next_action"] = "generate_proposal"
            else:
                state["next_action"] = "gather_requirements"
        else:
            # Default to gather requirements if we're still collecting information
            if not all_info_collected and (current_phase == "information_collection" or current_phase == "initial_assessment"):
                state["next_action"] = "gather_requirements"
            else:
                # Default to generate response
                state["next_action"] = "generate_response"
        
        return state
    
    def gather_requirements(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather event requirements and save to conversation memory.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Get conversation memory if available
        memory = state.get("memory")
        
        # Create a prompt for the LLM to extract requirements
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps extract event planning requirements from user messages. 
Extract any details about:
1. Basic details: event type, title, description, attendee count, scale
2. Timeline: start/end dates, key milestones, setup/teardown
3. Budget: budget range, allocation priorities, payment timeline
4. Location: geographic preferences, venue type, space requirements
5. Stakeholders: key stakeholders, speakers, sponsors, VIPs
6. Resources: equipment, staffing, service providers
7. Success criteria: goals, KPIs, expected outcomes
8. Risks: challenges, contingencies, insurance

Also determine which information categories have been sufficiently addressed."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content="""Based on the conversation, extract the event requirements in JSON format with the following structure:
{
  "event_details": {
    "event_type": null,
    "title": null,
    "description": null,
    "attendee_count": null,
    "scale": null
  },
  "timeline": {
    "start_date": null,
    "end_date": null,
    "key_milestones": []
  },
  "budget": {
    "range": null,
    "allocation_priorities": []
  },
  "location": {
    "preferences": [],
    "venue_type": null,
    "space_requirements": null
  },
  "stakeholders": [],
  "resources": [],
  "success_criteria": [],
  "risks": [],
  "information_collected": {
    "basic_details": false,
    "timeline": false,
    "budget": false,
    "location": false,
    "stakeholders": false,
    "resources": false,
    "success_criteria": false,
    "risks": false
  }
}

For each field, extract the information if available in the conversation. For the information_collected object, set a category to true only if sufficient information has been provided for that category.
""")
        ])
        
        # Extract requirements using the LLM
        # Filter out system messages before invoking the chain
        filtered_messages = [
            {"role": m["role"], "content": m["content"]} 
            for m in state["messages"] 
            if m["role"] != "system"
        ]
        chain = prompt | llm
        result = chain.invoke({"messages": filtered_messages})
        
        # Parse the result
        try:
            import json
            requirements_data = json.loads(result.content)
            
            # Update event details and save to memory
            if "event_details" in requirements_data:
                for key, value in requirements_data["event_details"].items():
                    if value is not None:
                        state["event_details"][key] = value
                        # Save user preferences to memory
                        if memory:
                            if key == "event_type":
                                memory.track_user_preference("event_type", value, confidence=0.9)
                            elif key == "attendee_count":
                                memory.track_user_preference("attendee_count", value, confidence=0.9)
                            elif key == "scale":
                                memory.track_user_preference("event_scale", value, confidence=0.8)
            
            # Update timeline and save to memory
            if "timeline" in requirements_data:
                for key, value in requirements_data["timeline"].items():
                    if value is not None:
                        if key == "start_date":
                            state["event_details"]["timeline_start"] = value
                            if memory:
                                memory.track_user_preference("start_date", value, confidence=0.9)
                        elif key == "end_date":
                            state["event_details"]["timeline_end"] = value
                            if memory:
                                memory.track_user_preference("end_date", value, confidence=0.9)
                        else:
                            state["event_details"][key] = value
            
            # Update other requirements and save to memory
            for category in ["stakeholders", "resources", "success_criteria", "risks"]:
                if category in requirements_data and requirements_data[category]:
                    state["requirements"][category] = requirements_data[category]
                    # Save to memory
                    if memory and requirements_data[category]:
                        memory.track_user_preference(f"{category}_requirements", requirements_data[category], confidence=0.8)
            
            # Update budget and location in requirements and save to memory
            if "budget" in requirements_data and requirements_data["budget"]:
                if "budget" not in state["requirements"]:
                    state["requirements"]["budget"] = []
                state["requirements"]["budget"] = requirements_data["budget"]
                if memory:
                    memory.track_user_preference("budget_preferences", requirements_data["budget"], confidence=0.8)
            
            if "location" in requirements_data and requirements_data["location"]:
                if "location" not in state["requirements"]:
                    state["requirements"]["location"] = []
                state["requirements"]["location"] = requirements_data["location"]
                if memory:
                    memory.track_user_preference("location_preferences", requirements_data["location"], confidence=0.8)
            
            # Update information collected status and track clarifications
            if "information_collected" in requirements_data:
                for category, status in requirements_data["information_collected"].items():
                    # If this category was just completed, track it as a clarification
                    if status and not state["information_collected"].get(category, False) and memory:
                        memory.track_clarification(
                            f"Information about {category.replace('_', ' ')}",
                            "Provided by user",
                            f"Collected {category.replace('_', ' ')} information"
                        )
                    state["information_collected"][category] = status
            
            # Update phase and next steps
            state["current_phase"] = "information_collection"
            
            # Check if all information has been collected
            all_info_collected = all(state["information_collected"].values())
            if all_info_collected:
                state["next_steps"] = ["generate_proposal"]
            else:
                # Determine which information is still needed
                missing_info = [category for category, collected in state["information_collected"].items() if not collected]
                state["next_steps"] = [f"collect_{category}_information" for category in missing_info]
            
        except Exception as e:
            # If parsing fails, add an error message (marked as ephemeral)
            state["messages"].append({
                "role": "system",
                "content": f"Error extracting requirements: {str(e)}",
                "ephemeral": True
            })
        
        return state
    
    def generate_proposal(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an event proposal based on collected information.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with proposal
        """
        # Create a prompt for the LLM to generate a proposal
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that generates comprehensive event planning proposals. 
Create a detailed, well-structured proposal based on the information collected about the event.

IMPORTANT: When making recommendations for venues, dates, speakers, vendors, or any other resources, DO NOT validate their availability. 
Simply recommend possibilities that match the requirements. Actual availability validation will be performed later as part of the project plan.

The proposal should include:
1. Executive summary
2. Detailed event description
3. Timeline with milestones
4. Budget breakdown
5. Resource allocation plan (recommended options without availability validation)
6. Stakeholder management approach (recommended speakers/participants without availability validation)
7. Risk management strategy
8. Success metrics
9. Next steps

Format the proposal with clear headings, bullet points where appropriate, and a professional tone.
Include a note in the proposal that all recommendations are subject to availability validation during the implementation phase."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Requirements: {state['requirements']}

Generate a comprehensive event proposal based on this information. The proposal should be well-structured, detailed, and ready to present to stakeholders. Remember to clearly indicate that all venue, speaker, vendor, and date recommendations are subject to availability validation during the implementation phase.""")
        ])
        
        # Generate proposal using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Store the proposal in the state
        state["proposal"] = {
            "content": result.content,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "pending_approval"
        }
        
        # Add the proposal to messages
        state["messages"].append({
            "role": "assistant",
            "content": f"Based on the information collected, I've prepared the following event proposal:\n\n{result.content}\n\nPlease review this proposal and let me know if you'd like to make any changes or if you approve it to proceed with implementation."
        })
        
        # Update phase and next steps
        state["current_phase"] = "proposal_review"
        state["next_steps"] = ["await_proposal_approval", "make_proposal_revisions"]
        
        return state
    
    def delegate_tasks(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate tasks to specialized agents.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to determine task delegation
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps delegate event planning tasks to specialized agents.
            
Available agents:
- resource_planning: Handles venue selection, service providers, equipment
- financial: Manages budget, payments, contracts
- stakeholder_management: Coordinates sponsors, speakers, volunteers
- marketing_communications: Manages campaigns, website, attendee communications
- project_management: Tracks tasks, timeline, risks
- analytics: Collects data, analyzes performance
- compliance_security: Ensures legal requirements, security protocols

Based on the event details, requirements, and approved proposal, determine which tasks should be delegated to which agents.

IMPORTANT: Include validation tasks for resources mentioned in the proposal. These should include:
1. Validating venue availability for the proposed dates
2. Validating speaker availability for the proposed dates
3. Validating vendor/service provider availability
4. Validating equipment availability
5. Validating sponsor availability and interest

These validation tasks are critical as the proposal contains recommendations that have not yet been validated for availability."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Requirements: {state['requirements']}
Current assignments: {state['agent_assignments']}
Proposal: {state['proposal']['content'] if 'proposal' in state else 'Not yet generated'}

Determine up to 8 new tasks that should be delegated to specialized agents, including necessary validation tasks for resources mentioned in the proposal. Return the result as a JSON array with objects containing 'agent_type' and 'task' fields.""")
        ])
        
        # Determine task delegation using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Parse the result
        try:
            import json
            delegation_data = json.loads(result.content)
            
            # Add new assignments
            for assignment in delegation_data:
                if isinstance(assignment, dict) and "agent_type" in assignment and "task" in assignment:
                    # Add the assignment to the state
                    state["agent_assignments"].append({
                        "agent_type": assignment["agent_type"],
                        "task": assignment["task"],
                        "status": "pending",
                        "assigned_at": datetime.utcnow().isoformat()
                    })
                    
                    # If it's a resource planning task, actually delegate it to the Resource Planning Agent
                    if assignment["agent_type"] == "resource_planning":
                        try:
                            # Use the ResourcePlanningTaskTool to delegate the task
                            resource_planning_tool = ResourcePlanningTaskTool()
                            task_result = resource_planning_tool._run(
                                task=assignment["task"],
                                event_details=state["event_details"],
                                requirements=state["requirements"]
                            )
                            
                            # Check if there was an error
                            if "error" in task_result:
                                # Update the assignment with the error
                                state["agent_assignments"][-1]["status"] = "failed"
                                state["agent_assignments"][-1]["completed_at"] = datetime.utcnow().isoformat()
                                state["agent_assignments"][-1]["result"] = task_result["response"]
                                state["agent_assignments"][-1]["error"] = task_result["error"]
                                
                                # Add an error message to the conversation (not ephemeral so it's visible)
                                state["messages"].append({
                                    "role": "assistant",
                                    "content": f"I encountered an issue when delegating to the Resource Planning Agent: {task_result['response']}"
                                })
                                
                                print(f"Error in Resource Planning Agent: {task_result['error']['error_message']}")
                            else:
                                # Update the assignment with the result
                                state["agent_assignments"][-1]["status"] = "completed"
                                state["agent_assignments"][-1]["completed_at"] = datetime.utcnow().isoformat()
                                state["agent_assignments"][-1]["result"] = task_result["response"]
                                
                                # If the task resulted in a resource plan, store it
                                if task_result.get("resource_plan"):
                                    if "agent_results" not in state:
                                        state["agent_results"] = {}
                                    if "resource_planning" not in state["agent_results"]:
                                        state["agent_results"]["resource_planning"] = {}
                                    
                                    state["agent_results"]["resource_planning"]["resource_plan"] = task_result["resource_plan"]
                                    state["agent_results"]["resource_planning"]["venue_options"] = task_result["venue_options"]
                                    state["agent_results"]["resource_planning"]["selected_venue"] = task_result["selected_venue"]
                                    state["agent_results"]["resource_planning"]["service_providers"] = task_result["service_providers"]
                                    state["agent_results"]["resource_planning"]["equipment_needs"] = task_result["equipment_needs"]
                        except Exception as e:
                            # If delegation fails, add an error message (not ephemeral so it's visible)
                            error_message = f"Error delegating task to Resource Planning Agent: {str(e)}"
                            print(error_message)
                            
                            # Update the assignment with the error
                            state["agent_assignments"][-1]["status"] = "failed"
                            state["agent_assignments"][-1]["completed_at"] = datetime.utcnow().isoformat()
                            state["agent_assignments"][-1]["error"] = {
                                "error_message": str(e),
                                "error_type": "Exception",
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            
                            # Add an error message to the conversation
                            state["messages"].append({
                                "role": "assistant",
                                "content": f"I encountered an error when delegating to the Resource Planning Agent: {str(e)}\n\nThis might be due to insufficient information about the event or a technical issue. Please provide more details about your requirements or try again later."
                            })
                    
                    # If it's a financial task, delegate it to the Financial Agent
                    elif assignment["agent_type"] == "financial":
                        try:
                            # Use the FinancialTaskTool to delegate the task
                            financial_task_tool = FinancialTaskTool()
                            
                            # Extract budget information from requirements if available
                            budget = None
                            if "budget" in state["requirements"]:
                                budget = state["requirements"]["budget"]
                            
                            task_result = financial_task_tool._run(
                                task=assignment["task"],
                                event_details=state["event_details"],
                                budget=budget,
                                requirements=state["requirements"]
                            )
                            
                            # Update the assignment with the result
                            state["agent_assignments"][-1]["status"] = "completed"
                            state["agent_assignments"][-1]["completed_at"] = datetime.utcnow().isoformat()
                            state["agent_assignments"][-1]["result"] = task_result["response"]
                            
                            # Store the financial results
                            if task_result.get("budget") or task_result.get("expenses") or task_result.get("contracts") or task_result.get("financial_plan"):
                                if "agent_results" not in state:
                                    state["agent_results"] = {}
                                if "financial" not in state["agent_results"]:
                                    state["agent_results"]["financial"] = {}
                                
                                if task_result.get("budget"):
                                    state["agent_results"]["financial"]["budget"] = task_result["budget"]
                                if task_result.get("expenses"):
                                    state["agent_results"]["financial"]["expenses"] = task_result["expenses"]
                                if task_result.get("contracts"):
                                    state["agent_results"]["financial"]["contracts"] = task_result["contracts"]
                                if task_result.get("financial_plan"):
                                    state["agent_results"]["financial"]["financial_plan"] = task_result["financial_plan"]
                        except Exception as e:
                            # If delegation fails, add an error message (marked as ephemeral)
                            state["messages"].append({
                                "role": "system",
                                "content": f"Error delegating task to Financial Agent: {str(e)}",
                                "ephemeral": True
                            })
                    
                    # If it's a stakeholder management task, delegate it to the Stakeholder Management Agent
                    elif assignment["agent_type"] == "stakeholder_management":
                        try:
                            # Use the StakeholderManagementTaskTool to delegate the task
                            stakeholder_task_tool = StakeholderManagementTaskTool()
                            
                            task_result = stakeholder_task_tool._run(
                                task=assignment["task"],
                                event_details=state["event_details"],
                                requirements=state["requirements"]
                            )
                            
                            # Update the assignment with the result
                            state["agent_assignments"][-1]["status"] = "completed"
                            state["agent_assignments"][-1]["completed_at"] = datetime.utcnow().isoformat()
                            state["agent_assignments"][-1]["result"] = task_result["response"]
                            
                            # Store the stakeholder management results
                            if (task_result.get("stakeholder_plan") or task_result.get("speakers") or 
                                task_result.get("sponsors") or task_result.get("volunteers") or 
                                task_result.get("vips")):
                                if "agent_results" not in state:
                                    state["agent_results"] = {}
                                if "stakeholder_management" not in state["agent_results"]:
                                    state["agent_results"]["stakeholder_management"] = {}
                                
                                if task_result.get("stakeholder_plan"):
                                    state["agent_results"]["stakeholder_management"]["stakeholder_plan"] = task_result["stakeholder_plan"]
                                if task_result.get("speakers"):
                                    state["agent_results"]["stakeholder_management"]["speakers"] = task_result["speakers"]
                                if task_result.get("sponsors"):
                                    state["agent_results"]["stakeholder_management"]["sponsors"] = task_result["sponsors"]
                                if task_result.get("volunteers"):
                                    state["agent_results"]["stakeholder_management"]["volunteers"] = task_result["volunteers"]
                                if task_result.get("vips"):
                                    state["agent_results"]["stakeholder_management"]["vips"] = task_result["vips"]
                        except Exception as e:
                            # If delegation fails, add an error message (marked as ephemeral)
                            state["messages"].append({
                                "role": "system",
                                "content": f"Error delegating task to Stakeholder Management Agent: {str(e)}",
                                "ephemeral": True
                            })
                    
                    # If it's a marketing and communications task, delegate it to the Marketing & Communications Agent
                    elif assignment["agent_type"] == "marketing_communications":
                        try:
                            # Use the MarketingCommunicationsTaskTool to delegate the task
                            marketing_task_tool = MarketingCommunicationsTaskTool()
                            
                            task_result = marketing_task_tool._run(
                                task=assignment["task"],
                                event_details=state["event_details"],
                                requirements=state["requirements"]
                            )
                            
                            # Update the assignment with the result
                            state["agent_assignments"][-1]["status"] = "completed"
                            state["agent_assignments"][-1]["completed_at"] = datetime.utcnow().isoformat()
                            state["agent_assignments"][-1]["result"] = task_result["response"]
                            
                            # Store the marketing and communications results
                            if (task_result.get("channels") or task_result.get("content") or 
                                task_result.get("attendees") or task_result.get("registration_forms") or 
                                task_result.get("campaigns") or task_result.get("marketing_plan") or
                                task_result.get("communication_plan")):
                                if "agent_results" not in state:
                                    state["agent_results"] = {}
                                if "marketing_communications" not in state["agent_results"]:
                                    state["agent_results"]["marketing_communications"] = {}
                                
                                if task_result.get("channels"):
                                    state["agent_results"]["marketing_communications"]["channels"] = task_result["channels"]
                                if task_result.get("content"):
                                    state["agent_results"]["marketing_communications"]["content"] = task_result["content"]
                                if task_result.get("attendees"):
                                    state["agent_results"]["marketing_communications"]["attendees"] = task_result["attendees"]
                                if task_result.get("registration_forms"):
                                    state["agent_results"]["marketing_communications"]["registration_forms"] = task_result["registration_forms"]
                                if task_result.get("campaigns"):
                                    state["agent_results"]["marketing_communications"]["campaigns"] = task_result["campaigns"]
                                if task_result.get("marketing_plan"):
                                    state["agent_results"]["marketing_communications"]["marketing_plan"] = task_result["marketing_plan"]
                                if task_result.get("communication_plan"):
                                    state["agent_results"]["marketing_communications"]["communication_plan"] = task_result["communication_plan"]
                        except Exception as e:
                            # If delegation fails, add an error message (marked as ephemeral)
                            state["messages"].append({
                                "role": "system",
                                "content": f"Error delegating task to Marketing & Communications Agent: {str(e)}",
                                "ephemeral": True
                            })
                    
                    # If it's a project management task, delegate it to the Project Management Agent
                    elif assignment["agent_type"] == "project_management":
                        try:
                            # Use the ProjectManagementTaskTool to delegate the task
                            project_management_tool = ProjectManagementTaskTool()
                            
                            task_result = project_management_tool._run(
                                task=assignment["task"],
                                event_details=state["event_details"],
                                requirements=state["requirements"]
                            )
                            
                            # Update the assignment with the result
                            state["agent_assignments"][-1]["status"] = "completed"
                            state["agent_assignments"][-1]["completed_at"] = datetime.utcnow().isoformat()
                            state["agent_assignments"][-1]["result"] = task_result["response"]
                            
                            # Store the project management results
                            if (task_result.get("tasks") or task_result.get("milestones") or 
                                task_result.get("risks") or task_result.get("timeline") or 
                                task_result.get("project_plan")):
                                if "agent_results" not in state:
                                    state["agent_results"] = {}
                                if "project_management" not in state["agent_results"]:
                                    state["agent_results"]["project_management"] = {}
                                
                                if task_result.get("tasks"):
                                    state["agent_results"]["project_management"]["tasks"] = task_result["tasks"]
                                if task_result.get("milestones"):
                                    state["agent_results"]["project_management"]["milestones"] = task_result["milestones"]
                                if task_result.get("risks"):
                                    state["agent_results"]["project_management"]["risks"] = task_result["risks"]
                                if task_result.get("timeline"):
                                    state["agent_results"]["project_management"]["timeline"] = task_result["timeline"]
                                if task_result.get("project_plan"):
                                    state["agent_results"]["project_management"]["project_plan"] = task_result["project_plan"]
                        except Exception as e:
                            # If delegation fails, add an error message (marked as ephemeral)
                            state["messages"].append({
                                "role": "system",
                                "content": f"Error delegating task to Project Management Agent: {str(e)}",
                                "ephemeral": True
                            })
            
            # Update phase and next steps
            state["current_phase"] = "implementation"
            state["next_steps"] = ["monitor_progress", "provide_status_update"]
            
            # Add a message about the delegated tasks
            task_summary = []
            for a in state["agent_assignments"]:
                status_info = f" (Status: {a['status']})"
                if a.get("result"):
                    result_preview = a["result"][:100] + "..." if len(a["result"]) > 100 else a["result"]
                    status_info += f"\nResult: {result_preview}"
                task_summary.append(f"- Assigned to {a['agent_type']}: {a['task']}{status_info}")
            
            state["messages"].append({
                "role": "assistant",
                "content": f"I've delegated the following tasks to our specialized agents:\n\n{chr(10).join(task_summary)}\n\nI'll monitor their progress and provide regular updates."
            })
            
        except Exception as e:
            # If parsing fails, add an error message (marked as ephemeral)
            state["messages"].append({
                "role": "system",
                "content": f"Error delegating tasks: {str(e)}",
                "ephemeral": True
            })
        
        return state
    
    def provide_status(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide status updates.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to generate a status report
        agent_results_info = ""
        if "agent_results" in state and state["agent_results"]:
            agent_results_info = "Agent Results:\n"
            for agent_type, results in state["agent_results"].items():
                agent_results_info += f"\n{agent_type.replace('_', ' ').title()} Agent:\n"
                if agent_type == "resource_planning":
                    if "resource_plan" in results and results["resource_plan"]:
                        resource_plan = results["resource_plan"]
                        if "summary" in resource_plan:
                            agent_results_info += f"- Resource Plan Summary: {resource_plan['summary']}\n"
                        if "venue" in resource_plan:
                            agent_results_info += f"- Selected Venue: {resource_plan['venue']['name']}\n"
                        if "service_providers" in resource_plan:
                            agent_results_info += f"- Service Providers: {len(resource_plan['service_providers'])} providers selected\n"
                        if "equipment" in resource_plan and "total_cost" in resource_plan["equipment"]:
                            agent_results_info += f"- Equipment Cost: ${resource_plan['equipment']['total_cost']}\n"
                    
                    if "venue_options" in results and results["venue_options"]:
                        agent_results_info += f"- Venue Options: {len(results['venue_options'])} options found\n"
                    
                    if "selected_venue" in results and results["selected_venue"]:
                        venue = results["selected_venue"]
                        agent_results_info += f"- Selected Venue: {venue.get('name', 'Unknown')} ({venue.get('type', 'Unknown')})\n"
                        agent_results_info += f"  Capacity: {venue.get('capacity', 'Unknown')}, Price: ${venue.get('price_per_day', 'Unknown')} per day\n"
                    
                    if "service_providers" in results and results["service_providers"]:
                        agent_results_info += f"- Service Providers: {len(results['service_providers'])} providers found\n"
                        for provider in results["service_providers"][:3]:  # Show only first 3 for brevity
                            agent_results_info += f"  * {provider.get('name', 'Unknown')} ({provider.get('type', 'Unknown')})\n"
                        if len(results["service_providers"]) > 3:
                            agent_results_info += f"  * ... and {len(results['service_providers']) - 3} more\n"
                    
                    if "equipment_needs" in results and results["equipment_needs"]:
                        agent_results_info += f"- Equipment Needs: {len(results['equipment_needs'])} categories\n"
                        for category in results["equipment_needs"][:3]:  # Show only first 3 for brevity
                            agent_results_info += f"  * {category.get('category', 'Unknown')}: {len(category.get('items', []))} items\n"
                        if len(results["equipment_needs"]) > 3:
                            agent_results_info += f"  * ... and {len(results['equipment_needs']) - 3} more categories\n"
                
                elif agent_type == "financial":
                    if "budget" in results and results["budget"]:
                        budget = results["budget"]
                        agent_results_info += f"- Budget: ${budget.get('total_amount', 0):.2f}\n"
                        if "categories" in budget:
                            agent_results_info += f"- Budget Categories: {len(budget['categories'])} categories\n"
                            for category in budget['categories'][:3]:  # Show only first 3 for brevity
                                agent_results_info += f"  * {category.get('name', 'Unknown')}: ${category.get('amount', 0):.2f}\n"
                            if len(budget['categories']) > 3:
                                agent_results_info += f"  * ... and {len(budget['categories']) - 3} more categories\n"
                    
                    if "expenses" in results and results["expenses"]:
                        expenses = results["expenses"]
                        total_expenses = sum(expense.get("amount", 0) for expense in expenses)
                        agent_results_info += f"- Total Expenses: ${total_expenses:.2f}\n"
                        agent_results_info += f"- Expense Entries: {len(expenses)} entries\n"
                        for expense in expenses[:3]:  # Show only first 3 for brevity
                            agent_results_info += f"  * {expense.get('category', 'Unknown')}: ${expense.get('amount', 0):.2f} - {expense.get('vendor', 'Unknown')}\n"
                        if len(expenses) > 3:
                            agent_results_info += f"  * ... and {len(expenses) - 3} more expenses\n"
                    
                    if "contracts" in results and results["contracts"]:
                        contracts = results["contracts"]
                        agent_results_info += f"- Contracts: {len(contracts)} contracts\n"
                        for contract in contracts[:3]:  # Show only first 3 for brevity
                            agent_results_info += f"  * {contract.get('vendor_name', 'Unknown')}: {contract.get('service_type', 'Unknown')} - ${contract.get('amount', 0):.2f}\n"
                        if len(contracts) > 3:
                            agent_results_info += f"  * ... and {len(contracts) - 3} more contracts\n"
                    
                    if "financial_plan" in results and results["financial_plan"]:
                        financial_plan = results["financial_plan"]
                        agent_results_info += f"- Financial Plan: {financial_plan.get('approval_status', 'pending')}\n"
                        if "budget" in financial_plan:
                            agent_results_info += f"  * Budget: ${financial_plan['budget'].get('total_amount', 0):.2f}\n"
                        if "payment_schedule" in financial_plan:
                            agent_results_info += f"  * Payment Schedule: {len(financial_plan['payment_schedule'])} milestones\n"
                        if "financial_risks" in financial_plan:
                            agent_results_info += f"  * Financial Risks: {len(financial_plan['financial_risks'])} identified\n"
                        if "contingency_fund" in financial_plan:
                            agent_results_info += f"  * Contingency Fund: ${financial_plan.get('contingency_fund', 0):.2f}\n"
                
                elif agent_type == "stakeholder_management":
                    if "stakeholder_plan" in results and results["stakeholder_plan"]:
                        stakeholder_plan = results["stakeholder_plan"]
                        agent_results_info += f"- Stakeholder Plan: {stakeholder_plan.get('approval_status', 'pending')}\n"
                        if "communication_schedule" in stakeholder_plan:
                            agent_results_info += f"- Communication Schedule: {len(stakeholder_plan['communication_schedule'])} milestones\n"
                        if "engagement_strategies" in stakeholder_plan:
                            agent_results_info += f"- Engagement Strategies: {len(stakeholder_plan['engagement_strategies'])} stakeholder types\n"
                    
                    if "speakers" in results and results["speakers"]:
                        speakers = results["speakers"]
                        confirmed_speakers = sum(1 for s in speakers if s.get("confirmed", False))
                        agent_results_info += f"- Speakers: {len(speakers)} total ({confirmed_speakers} confirmed)\n"
                        for speaker in speakers[:3]:  # Show only first 3 for brevity
                            status = "Confirmed" if speaker.get("confirmed", False) else "Pending"
                            agent_results_info += f"  * {speaker.get('name', 'Unknown')} ({speaker.get('role', 'Unknown')}): {speaker.get('topic', 'Unknown')} - {status}\n"
                        if len(speakers) > 3:
                            agent_results_info += f"  * ... and {len(speakers) - 3} more speakers\n"
                    
                    if "sponsors" in results and results["sponsors"]:
                        sponsors = results["sponsors"]
                        confirmed_sponsors = sum(1 for s in sponsors if s.get("confirmed", False))
                        total_contribution = sum(s.get("contribution", 0) for s in sponsors)
                        agent_results_info += f"- Sponsors: {len(sponsors)} total ({confirmed_sponsors} confirmed)\n"
                        agent_results_info += f"- Total Sponsorship: ${total_contribution:.2f}\n"
                        for sponsor in sponsors[:3]:  # Show only first 3 for brevity
                            status = "Confirmed" if sponsor.get("confirmed", False) else "Pending"
                            agent_results_info += f"  * {sponsor.get('name', 'Unknown')} ({sponsor.get('level', 'Unknown')}): ${sponsor.get('contribution', 0):.2f} - {status}\n"
                        if len(sponsors) > 3:
                            agent_results_info += f"  * ... and {len(sponsors) - 3} more sponsors\n"
                    
                    if "volunteers" in results and results["volunteers"]:
                        volunteers = results["volunteers"]
                        confirmed_volunteers = sum(1 for v in volunteers if v.get("confirmed", False))
                        agent_results_info += f"- Volunteers: {len(volunteers)} total ({confirmed_volunteers} confirmed)\n"
                        roles = {}
                        for volunteer in volunteers:
                            role = volunteer.get("role", "Unknown")
                            roles[role] = roles.get(role, 0) + 1
                        for role, count in list(roles.items())[:3]:  # Show only first 3 for brevity
                            agent_results_info += f"  * {role}: {count} volunteers\n"
                        if len(roles) > 3:
                            agent_results_info += f"  * ... and {len(roles) - 3} more roles\n"
                    
                    if "vips" in results and results["vips"]:
                        vips = results["vips"]
                        confirmed_vips = sum(1 for v in vips if v.get("confirmed", False))
                        agent_results_info += f"- VIPs: {len(vips)} total ({confirmed_vips} confirmed)\n"
                        for vip in vips[:3]:  # Show only first 3 for brevity
                            status = "Confirmed" if vip.get("confirmed", False) else "Pending"
                            agent_results_info += f"  * {vip.get('name', 'Unknown')} ({vip.get('organization', 'Unknown')}, {vip.get('role', 'Unknown')}) - {status}\n"
                        if len(vips) > 3:
                            agent_results_info += f"  * ... and {len(vips) - 3} more VIPs\n"
                
                elif agent_type == "marketing_communications":
                    if "marketing_plan" in results and results["marketing_plan"]:
                        marketing_plan = results["marketing_plan"]
                        agent_results_info += f"- Marketing Plan: {marketing_plan.get('approval_status', 'pending')}\n"
                        if "objectives" in marketing_plan:
                            agent_results_info += f"- Marketing Objectives: {len(marketing_plan['objectives'])} objectives\n"
                        if "channels" in marketing_plan:
                            agent_results_info += f"- Marketing Channels: {len(marketing_plan['channels'])} channels\n"
                        if "campaigns" in marketing_plan:
                            agent_results_info += f"- Marketing Campaigns: {len(marketing_plan['campaigns'])} campaigns\n"
                        if "budget" in marketing_plan and "total_amount" in marketing_plan["budget"]:
                            agent_results_info += f"- Marketing Budget: ${marketing_plan['budget']['total_amount']:.2f}\n"
                    
                    if "communication_plan" in results and results["communication_plan"]:
                        communication_plan = results["communication_plan"]
                        agent_results_info += f"- Communication Plan: {communication_plan.get('approval_status', 'pending')}\n"
                        if "stakeholder_groups" in communication_plan:
                            agent_results_info += f"- Stakeholder Groups: {len(communication_plan['stakeholder_groups'])} groups\n"
                        if "schedule" in communication_plan:
                            agent_results_info += f"- Communication Schedule: {len(communication_plan['schedule'])} scheduled communications\n"
                    
                    if "channels" in results and results["channels"]:
                        channels = results["channels"]
                        agent_results_info += f"- Marketing Channels: {len(channels)} channels\n"
                        for channel in channels[:3]:  # Show only first 3 for brevity
                            agent_results_info += f"  * {channel.get('name', 'Unknown')} ({channel.get('type', 'Unknown')})\n"
                        if len(channels) > 3:
                            agent_results_info += f"  * ... and {len(channels) - 3} more channels\n"
                    
                    if "content" in results and results["content"]:
                        content = results["content"]
                        agent_results_info += f"- Marketing Content: {len(content)} content items\n"
                        for item in content[:3]:  # Show only first 3 for brevity
                            agent_results_info += f"  * {item.get('title', 'Unknown')} ({item.get('type', 'Unknown')}) for {item.get('channel', 'Unknown')}\n"
                        if len(content) > 3:
                            agent_results_info += f"  * ... and {len(content) - 3} more content items\n"
                    
                    if "campaigns" in results and results["campaigns"]:
                        campaigns = results["campaigns"]
                        agent_results_info += f"- Marketing Campaigns: {len(campaigns)} campaigns\n"
                        for campaign in campaigns[:3]:  # Show only first 3 for brevity
                            agent_results_info += f"  * {campaign.get('name', 'Unknown')}: {campaign.get('description', 'Unknown')}\n"
                            if "budget" in campaign:
                                agent_results_info += f"    Budget: ${campaign.get('budget', 0):.2f}\n"
                        if len(campaigns) > 3:
                            agent_results_info += f"  * ... and {len(campaigns) - 3} more campaigns\n"
                    
                    if "registration_forms" in results and results["registration_forms"]:
                        forms = results["registration_forms"]
                        agent_results_info += f"- Registration Forms: {len(forms)} forms\n"
                        for form in forms[:3]:  # Show only first 3 for brevity
                            agent_results_info += f"  * {form.get('title', 'Unknown')}: {len(form.get('fields', []))} fields, {len(form.get('ticket_types', []))} ticket types\n"
                        if len(forms) > 3:
                            agent_results_info += f"  * ... and {len(forms) - 3} more forms\n"
                
                elif agent_type == "project_management":
                    if "project_plan" in results and results["project_plan"]:
                        project_plan = results["project_plan"]
                        agent_results_info += f"- Project Plan: {project_plan.get('status_summary', 'In progress')}\n"
                        if "tasks" in project_plan:
                            completed_tasks = sum(1 for t in project_plan["tasks"] if t.get("status") == "completed")
                            total_tasks = len(project_plan["tasks"])
                            agent_results_info += f"- Tasks: {completed_tasks}/{total_tasks} completed\n"
                        if "milestones" in project_plan:
                            reached_milestones = sum(1 for m in project_plan["milestones"] if m.get("status") == "reached")
                            total_milestones = len(project_plan["milestones"])
                            agent_results_info += f"- Milestones: {reached_milestones}/{total_milestones} reached\n"
                        if "risks" in project_plan:
                            agent_results_info += f"- Risks: {len(project_plan['risks'])} identified\n"
                        if "timeline" in project_plan:
                            timeline = project_plan["timeline"]
                            if "start_date" in timeline and "end_date" in timeline:
                                agent_results_info += f"- Timeline: {timeline['start_date']} to {timeline['end_date']}\n"
                    
                    if "tasks" in results and results["tasks"]:
                        tasks = results["tasks"]
                        completed_tasks = sum(1 for t in tasks if t.get("status") == "completed")
                        in_progress_tasks = sum(1 for t in tasks if t.get("status") == "in_progress")
                        not_started_tasks = sum(1 for t in tasks if t.get("status") == "not_started")
                        blocked_tasks = sum(1 for t in tasks if t.get("status") == "blocked")
                        
                        agent_results_info += f"- Tasks: {len(tasks)} total\n"
                        agent_results_info += f"  * Completed: {completed_tasks}\n"
                        agent_results_info += f"  * In Progress: {in_progress_tasks}\n"
                        agent_results_info += f"  * Not Started: {not_started_tasks}\n"
                        agent_results_info += f"  * Blocked: {blocked_tasks}\n"
                        
                        # Show high priority tasks
                        high_priority_tasks = [t for t in tasks if t.get("priority") in ["high", "critical"]]
                        if high_priority_tasks:
                            agent_results_info += f"- High Priority Tasks: {len(high_priority_tasks)}\n"
                            for task in high_priority_tasks[:3]:  # Show only first 3 for brevity
                                agent_results_info += f"  * {task.get('name', 'Unknown')} ({task.get('priority', 'Unknown')}): {task.get('status', 'Unknown')}\n"
                            if len(high_priority_tasks) > 3:
                                agent_results_info += f"  * ... and {len(high_priority_tasks) - 3} more high priority tasks\n"
                    
                    if "milestones" in results and results["milestones"]:
                        milestones = results["milestones"]
                        reached_milestones = sum(1 for m in milestones if m.get("status") == "reached")
                        not_reached_milestones = sum(1 for m in milestones if m.get("status") == "not_reached")
                        delayed_milestones = sum(1 for m in milestones if m.get("status") == "delayed")
                        
                        agent_results_info += f"- Milestones: {len(milestones)} total\n"
                        agent_results_info += f"  * Reached: {reached_milestones}\n"
                        agent_results_info += f"  * Not Reached: {not_reached_milestones}\n"
                        agent_results_info += f"  * Delayed: {delayed_milestones}\n"
                        
                        # Show upcoming milestones
                        upcoming_milestones = sorted(
                            [m for m in milestones if m.get("status") == "not_reached"],
                            key=lambda x: x.get("date", "9999-12-31")
                        )
                        if upcoming_milestones:
                            agent_results_info += f"- Upcoming Milestones:\n"
                            for milestone in upcoming_milestones[:3]:  # Show only first 3 for brevity
                                agent_results_info += f"  * {milestone.get('name', 'Unknown')}: {milestone.get('date', 'No date')}\n"
                            if len(upcoming_milestones) > 3:
                                agent_results_info += f"  * ... and {len(upcoming_milestones) - 3} more upcoming milestones\n"
                    
                    if "risks" in results and results["risks"]:
                        risks = results["risks"]
                        high_impact_risks = sum(1 for r in risks if r.get("impact") == "high")
                        high_probability_risks = sum(1 for r in risks if r.get("probability") == "high")
                        
                        agent_results_info += f"- Risks: {len(risks)} total\n"
                        agent_results_info += f"  * High Impact: {high_impact_risks}\n"
                        agent_results_info += f"  * High Probability: {high_probability_risks}\n"
                        
                        # Show critical risks (high impact AND high probability)
                        critical_risks = [r for r in risks if r.get("impact") == "high" and r.get("probability") == "high"]
                        if critical_risks:
                            agent_results_info += f"- Critical Risks:\n"
                            for risk in critical_risks[:3]:  # Show only first 3 for brevity
                                agent_results_info += f"  * {risk.get('name', 'Unknown')}: {risk.get('status', 'Unknown')}\n"
                            if len(critical_risks) > 3:
                                agent_results_info += f"  * ... and {len(critical_risks) - 3} more critical risks\n"
                    
                    if "timeline" in results and results["timeline"]:
                        timeline = results["timeline"]
                        agent_results_info += f"- Timeline:\n"
                        if "start_date" in timeline and "end_date" in timeline:
                            agent_results_info += f"  * Project Duration: {timeline.get('start_date', 'Unknown')} to {timeline.get('end_date', 'Unknown')}\n"
                        if "critical_path" in timeline and timeline["critical_path"]:
                            agent_results_info += f"  * Critical Path: {len(timeline['critical_path'])} tasks\n"
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are an AI assistant that generates status reports for event planning. Create a concise but informative status update based on the current state of the event planning process."),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Requirements: {state['requirements']}
Agent assignments: {state['agent_assignments']}
Current phase: {state['current_phase']}
{agent_results_info}

Generate a status report for the event planning process. Include progress on key tasks, upcoming milestones, and any issues that need attention. If there are results from specialized agents, incorporate those into your report.""")
        ])
        
        # Generate status report using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Add the status report to messages
        state["messages"].append({
            "role": "assistant",
            "content": result.content
        })
        
        # Update phase and next steps
        state["current_phase"] = "status_reporting"
        state["next_steps"] = ["continue_monitoring", "address_issues"]
        
        return state
    
    def generate_response(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a response to the user using conversation memory for context.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Get conversation memory if available
        memory = state.get("memory")
        
        # First, process the user's latest response and save it to memory
        if state["messages"] and state["messages"][-1]["role"] == "user":
            user_message = state["messages"][-1]["content"]
            
            # Extract information from the user's response and save to memory
            if memory:
                # Determine what information category this response is about
                missing_categories = [category for category, collected in state["information_collected"].items() if not collected]
                if missing_categories:
                    current_category = missing_categories[0]
                    
                    # Save the user's response as a preference for this category
                    if current_category == "basic_details":
                        # Extract event type, title, description, attendee count
                        if any(keyword in user_message.lower() for keyword in ["conference", "meeting", "workshop", "seminar", "training", "corporate", "retreat", "wedding", "party", "celebration", "festival", "concert", "exhibition", "trade show", "networking"]):
                            memory.track_user_preference("event_type", user_message, confidence=0.9)
                            state["event_details"]["event_type"] = user_message
                            state["information_collected"]["basic_details"] = True
                            memory.track_clarification("Event type", user_message, f"User specified event type: {user_message}")
                    
                    elif current_category == "timeline":
                        # Extract timeline information
                        memory.track_user_preference("timeline", user_message, confidence=0.9)
                        state["event_details"]["timeline_start"] = user_message
                        state["information_collected"]["timeline"] = True
                        memory.track_clarification("Event timeline", user_message, f"User specified timeline: {user_message}")
                    
                    elif current_category == "budget":
                        # Extract budget information
                        memory.track_user_preference("budget", user_message, confidence=0.9)
                        if "requirements" not in state:
                            state["requirements"] = {}
                        if "budget" not in state["requirements"]:
                            state["requirements"]["budget"] = {}
                        state["requirements"]["budget"]["range"] = user_message
                        state["information_collected"]["budget"] = True
                        memory.track_clarification("Budget range", user_message, f"User specified budget: {user_message}")
                    
                    elif current_category == "location":
                        # Extract location information
                        memory.track_user_preference("location", user_message, confidence=0.9)
                        if "requirements" not in state:
                            state["requirements"] = {}
                        if "location" not in state["requirements"]:
                            state["requirements"]["location"] = {}
                        state["requirements"]["location"]["preferences"] = [user_message]
                        state["information_collected"]["location"] = True
                        memory.track_clarification("Location preferences", user_message, f"User specified location: {user_message}")
                    
                    elif current_category == "stakeholders":
                        # Extract stakeholder information
                        memory.track_user_preference("stakeholders", user_message, confidence=0.9)
                        if "requirements" not in state:
                            state["requirements"] = {}
                        if "stakeholders" not in state["requirements"]:
                            state["requirements"]["stakeholders"] = []
                        state["requirements"]["stakeholders"].append(user_message)
                        state["information_collected"]["stakeholders"] = True
                        memory.track_clarification("Key stakeholders", user_message, f"User specified stakeholders: {user_message}")
                    
                    elif current_category == "resources":
                        # Extract resource information
                        memory.track_user_preference("resources", user_message, confidence=0.9)
                        if "requirements" not in state:
                            state["requirements"] = {}
                        if "resources" not in state["requirements"]:
                            state["requirements"]["resources"] = []
                        state["requirements"]["resources"].append(user_message)
                        state["information_collected"]["resources"] = True
                        memory.track_clarification("Resource requirements", user_message, f"User specified resources: {user_message}")
                    
                    elif current_category == "success_criteria":
                        # Extract success criteria
                        memory.track_user_preference("success_criteria", user_message, confidence=0.9)
                        if "requirements" not in state:
                            state["requirements"] = {}
                        if "success_criteria" not in state["requirements"]:
                            state["requirements"]["success_criteria"] = []
                        state["requirements"]["success_criteria"].append(user_message)
                        state["information_collected"]["success_criteria"] = True
                        memory.track_clarification("Success criteria", user_message, f"User specified success criteria: {user_message}")
                    
                    elif current_category == "risks":
                        # Extract risk information
                        memory.track_user_preference("risks", user_message, confidence=0.9)
                        if "requirements" not in state:
                            state["requirements"] = {}
                        if "risks" not in state["requirements"]:
                            state["requirements"]["risks"] = []
                        state["requirements"]["risks"].append(user_message)
                        state["information_collected"]["risks"] = True
                        memory.track_clarification("Risk concerns", user_message, f"User specified risks: {user_message}")
        
        # Check if the user is approving a proposal
        if state["messages"] and state["messages"][-1]["role"] == "user":
            user_message = state["messages"][-1]["content"].lower()
            if "approve" in user_message and "proposal" in user_message:
                print("User approved the proposal. Transitioning to implementation phase.")
                state["current_phase"] = "implementation"
                
                # Track this decision in memory
                if memory:
                    memory.track_decision(
                        "proposal_approval",
                        "Approved the event proposal",
                        "User reviewed and approved the comprehensive event proposal",
                        ["request_changes", "reject_proposal"]
                    )
                
                # Add a message about transitioning to implementation
                state["messages"].append({
                    "role": "assistant",
                    "content": "Thank you for approving the proposal! I'll now begin implementing the plan by delegating tasks to our specialized agents."
                })
                
                # Delegate tasks to specialized agents
                return delegate_tasks(state)

        # Get conversation context from memory if available
        context_summary = ""
        context_reference = ""
        if memory:
            # Get a summary of the conversation context
            context_summary = memory.get_context_summary()
            
            # Check if we should reference previous context based on the current topic
            current_user_message = state["messages"][-1]["content"] if state["messages"] and state["messages"][-1]["role"] == "user" else ""
            
            # Determine current topic from user message
            current_topic = "general"
            if any(keyword in current_user_message.lower() for keyword in ["venue", "location", "place"]):
                current_topic = "venue"
            elif any(keyword in current_user_message.lower() for keyword in ["budget", "cost", "money", "price"]):
                current_topic = "budget"
            elif any(keyword in current_user_message.lower() for keyword in ["date", "time", "when", "schedule"]):
                current_topic = "timeline"
            elif any(keyword in current_user_message.lower() for keyword in ["speaker", "guest", "attendee", "people"]):
                current_topic = "stakeholders"
            elif any(keyword in current_user_message.lower() for keyword in ["equipment", "catering", "service"]):
                current_topic = "resources"
            
            # Check if we should reference previous context
            if memory.should_reference_previous_context(current_topic):
                context_reference = memory.get_context_reference_text(current_topic)

        # Determine what information is still needed and ask ONE question at a time
        missing_categories = [category for category, collected in state["information_collected"].items() if not collected]
        
        # Create enhanced system prompt with memory context and single question focus
        enhanced_system_prompt = COORDINATOR_SYSTEM_PROMPT.format(
            current_phase=state["current_phase"],
            event_details=state["event_details"],
            requirements=state["requirements"],
            agent_assignments=state["agent_assignments"],
            next_steps=state["next_steps"],
            information_collected=state["information_collected"]
        )
        
        # Add memory context to the system prompt if available
        if context_summary:
            enhanced_system_prompt += f"\n\nConversation Context Summary: {context_summary}"
        
        if context_reference:
            enhanced_system_prompt += f"\n\nRELEVANT CONTEXT: {context_reference}When responding, naturally reference this previous context to show continuity and avoid asking for information already provided."

        # Add single question instruction
        if missing_categories:
            next_category = missing_categories[0]
            enhanced_system_prompt += f"\n\nIMPORTANT: You are currently collecting information about '{next_category.replace('_', ' ')}'. Ask ONLY ONE focused question about this category. Do not ask multiple questions at once. Wait for the user's response before asking about other categories."
            
            # Add specific guidance for each category
            category_guidance = {
                "basic_details": "Ask about the type of event they're planning (e.g., conference, wedding, corporate retreat, etc.)",
                "timeline": "Ask about when they want to hold the event (specific dates or timeframe)",
                "budget": "Ask about their budget range or total budget for the event",
                "location": "Ask about their preferred location or venue type",
                "stakeholders": "Ask about key people involved (speakers, VIPs, sponsors, etc.)",
                "resources": "Ask about specific resources they need (equipment, catering, services, etc.)",
                "success_criteria": "Ask about what would make this event successful in their view",
                "risks": "Ask about any concerns or potential challenges they foresee"
            }
            
            if next_category in category_guidance:
                enhanced_system_prompt += f"\n\nSpecific guidance for {next_category}: {category_guidance[next_category]}"

        # Create the coordinator prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=enhanced_system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Convert message dicts to message objects
        message_objects = []
        for m in state["messages"]:
            role = m.get("role")
            content = m.get("content")
            if role == "user":
                message_objects.append(HumanMessage(content=content))
            elif role == "assistant":
                message_objects.append(AIMessage(content=content))
            # Avoid adding system messages from history here, as the template adds one
            # elif role == "system":
            #     message_objects.append(SystemMessage(content=content))

        # Generate response using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": message_objects})
        
        # Track the response in memory if available
        if memory and state["messages"] and state["messages"][-1]["role"] == "user":
            user_message = state["messages"][-1]["content"]
            
            # Track this as a recommendation if we're providing suggestions
            if any(keyword in result.content.lower() for keyword in ["recommend", "suggest", "propose", "consider"]):
                memory.track_recommendation(
                    current_topic,
                    result.content[:200] + "..." if len(result.content) > 200 else result.content,
                    user_reaction=None,  # Will be updated when user responds
                    accepted=None  # Will be updated when user responds
                )
        
        # Add the response to messages (as dict)
        new_message = {
            "role": "assistant",
            "content": result.content
        }
        state["messages"].append(new_message)
        
        # Print the response for debugging
        print(f"Generated response: {result.content[:100]}...")
        
        return state
    
    # Create the graph
    workflow = StateGraph(dict)
    
    # Add nodes
    workflow.add_node("assess_request", assess_request)
    workflow.add_node("gather_requirements", gather_requirements)
    workflow.add_node("generate_proposal", generate_proposal)
    workflow.add_node("delegate_tasks", delegate_tasks)
    workflow.add_node("provide_status", provide_status)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("tools", tool_node)
    
    # Add edges
    workflow.add_conditional_edges(
        "assess_request",
        lambda state: state["next_action"]
    )
    
    workflow.add_edge("gather_requirements", "generate_response")
    workflow.add_edge("generate_proposal", "generate_response")  # Changed from END to generate_response
    workflow.add_edge("delegate_tasks", "generate_response")
    workflow.add_edge("provide_status", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Set the entry point
    workflow.set_entry_point("assess_request")
    
    return workflow.compile()


def create_initial_state() -> Dict[str, Any]:
    """
    Create the initial state for the coordinator agent.
    
    Returns:
        Initial state dictionary
    """
    return {
        "messages": [],
        "event_details": {
            "event_type": None,
            "title": None,
            "description": None,
            "attendee_count": None,
            "scale": None,
            "timeline_start": None,
            "timeline_end": None
        },
        "requirements": {
            "stakeholders": [],
            "resources": [],
            "risks": [],
            "success_criteria": [],
            "budget": {},
            "location": {}
        },
        "agent_assignments": [],
        "current_phase": "information_collection",  # Changed from initial_assessment to information_collection
        "next_steps": ["gather_event_details"],
        "proposal": None,
        "information_collected": {
            "basic_details": False,
            "timeline": False,
            "budget": False,
            "location": False,
            "stakeholders": False,
            "resources": False,
            "success_criteria": False,
            "risks": False
        },
        "agent_results": {}
    }
