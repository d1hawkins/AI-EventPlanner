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

# IMPORTANT: Removed TypedDict imports to avoid compatibility issues
# Instead of importing these:
# from app.schemas.event import EventDetails, Requirements, AgentAssignment
# We'll use regular dictionaries


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
    def assess_request(state):
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
    
    def gather_requirements(state):
        """
        Gather event requirements.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
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
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Parse the result
        try:
            import json
            requirements_data = json.loads(result.content)
            
            # Update event details
            if "event_details" in requirements_data:
                for key, value in requirements_data["event_details"].items():
                    if value is not None:
                        state["event_details"][key] = value
            
            # Update timeline
            if "timeline" in requirements_data:
                for key, value in requirements_data["timeline"].items():
                    if value is not None:
                        if key == "start_date":
                            state["event_details"]["timeline_start"] = value
                        elif key == "end_date":
                            state["event_details"]["timeline_end"] = value
                        else:
                            state["event_details"][key] = value
            
            # Update other requirements
            for category in ["stakeholders", "resources", "success_criteria", "risks"]:
                if category in requirements_data and requirements_data[category]:
                    state["requirements"][category] = requirements_data[category]
            
            # Update budget and location in requirements if not already there
            if "budget" in requirements_data and requirements_data["budget"]:
                if "budget" not in state["requirements"]:
                    state["requirements"]["budget"] = {}
                state["requirements"]["budget"] = requirements_data["budget"]
            
            if "location" in requirements_data and requirements_data["location"]:
                if "location" not in state["requirements"]:
                    state["requirements"]["location"] = {}
                state["requirements"]["location"] = requirements_data["location"]
            
            # Update information collected status
            if "information_collected" in requirements_data:
                for category, status in requirements_data["information_collected"].items():
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
    
    def generate_proposal(state):
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
    
    def delegate_tasks(state):
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
        except Exception as e:
            # If parsing fails, add an error message (marked as ephemeral)
            state["messages"].append({
                "role": "system",
                "content": f"Error delegating tasks: {str(e)}",
                "ephemeral": True
            })
        
        return state
    
    def provide_status(state):
        """
        Provide a status update on the event planning process.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to generate a status update
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that provides status updates on event planning progress.
Generate a clear, concise status update based on the current state of the event planning process.

The status update should include:
1. Current phase of the planning process
2. Summary of information collected so far
3. Status of the proposal (if applicable)
4. Status of delegated tasks (if applicable)
5. Next steps in the process

Format the status update in a professional, easy-to-read manner."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Current phase: {state['current_phase']}
Event details: {state['event_details']}
Requirements: {state['requirements']}
Information collected: {state['information_collected']}
Proposal status: {state['proposal']['status'] if 'proposal' in state else 'Not yet generated'}
Agent assignments: {state['agent_assignments']}
Next steps: {state['next_steps']}

Generate a comprehensive status update on the event planning process.""")
        ])
        
        # Generate status update using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Add the status update to messages
        state["messages"].append({
            "role": "assistant",
            "content": result.content
        })
        
        return state
    
    def generate_response(state):
        """
        Generate a response to the user's message.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to generate a response
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=COORDINATOR_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        # Format the system prompt with the current state
        formatted_prompt = prompt.partial(
            current_phase=state["current_phase"],
            event_details=state["event_details"],
            requirements=state["requirements"],
            agent_assignments=state["agent_assignments"],
            next_steps=state["next_steps"],
            information_collected=state["information_collected"]
        )
        
        # Generate response using the LLM
        chain = formatted_prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Add the response to messages
        state["messages"].append({
            "role": "assistant",
            "content": result.content
        })
        
        return state
    
    # Define the graph
    workflow = StateGraph(state_schema=dict)
    
    # Add nodes
    workflow.add_node("assess_request", assess_request)
    workflow.add_node("gather_requirements", gather_requirements)
    workflow.add_node("generate_proposal", generate_proposal)
    workflow.add_node("delegate_tasks", delegate_tasks)
    workflow.add_node("provide_status", provide_status)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("tool_node", tool_node)
    
    # Add edges
    workflow.add_conditional_edges(
        "assess_request",
        lambda state: state["next_action"],
        {
            "gather_requirements": "gather_requirements",
            "generate_proposal": "generate_proposal",
            "delegate_tasks": "delegate_tasks",
            "provide_status": "provide_status",
            "generate_response": "generate_response"
        }
    )
    
    # Connect all nodes back to assess_request
    workflow.add_edge("gather_requirements", "assess_request")
    workflow.add_edge("generate_proposal", "assess_request")
    workflow.add_edge("delegate_tasks", "assess_request")
    workflow.add_edge("provide_status", "assess_request")
    workflow.add_edge("generate_response", "assess_request")
    workflow.add_edge("tool_node", "assess_request")
    
    # Set the entry point
    workflow.set_entry_point("assess_request")
    
    # Compile the graph
    return workflow.compile()


def create_initial_state():
    """
    Create the initial state for the coordinator agent.
    
    Returns:
        Initial state dictionary
    """
    return {
        "messages": [],
        "current_phase": "initial_assessment",
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
            "success_criteria": [],
            "risks": []
        },
        "agent_assignments": [],
        "next_steps": ["gather_basic_information"],
        "information_collected": {
            "basic_details": False,
            "timeline": False,
            "budget": False,
            "location": False,
            "stakeholders": False,
            "resources": False,
            "success_criteria": False,
            "risks": False
        }
    }
