from typing import Dict, List, Any, TypedDict, Literal, Optional
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.utils.llm_factory import get_llm
from app.tools.project_tools import (
    TaskManagementTool,
    MilestoneManagementTool,
    RiskManagementTool,
    TimelineGenerationTool,
    ProjectPlanGenerationTool
)
from app.tools.event_tools import RequirementsTool, MonitoringTool, ReportingTool
from app.tools.project_management_search_tool import ProjectManagementSearchTool


# Define the state schema for the Project Management Agent
class ProjectManagementStateDict(TypedDict):
    """State for the project management agent."""
    
    messages: List[Dict[str, str]]
    event_details: Dict[str, Any]
    tasks: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    risks: List[Dict[str, Any]]
    timeline: Optional[Dict[str, Any]]
    project_plan: Optional[Dict[str, Any]]
    current_phase: str
    next_steps: List[str]


# Define the system prompt for the Project Management Agent
PROJECT_MANAGEMENT_SYSTEM_PROMPT = """You are the Project Management Agent for an event planning system. Your role is to:

1. Track tasks and their dependencies
2. Manage project timeline and milestones
3. Identify and mitigate risks
4. Ensure timely event delivery
5. Provide status updates and reports

Your primary responsibilities include:

Task Management:
- Task creation and assignment
- Progress tracking
- Dependency management
- Status reporting

Timeline Control:
- Milestone setting
- Critical path analysis
- Delay mitigation
- Schedule optimization

Risk Management:
- Risk identification
- Mitigation planning
- Issue tracking
- Contingency activation

Your current state:
Current phase: {current_phase}
Event details: {event_details}
Tasks: {tasks}
Milestones: {milestones}
Risks: {risks}
Timeline: {timeline}
Project plan: {project_plan}
Next steps: {next_steps}

Follow these guidelines:
1. Analyze the event requirements to understand the project management needs
2. Create a comprehensive project plan with tasks, milestones, and timeline
3. Identify potential risks and develop mitigation strategies
4. Track task progress and provide regular status updates
5. Optimize the timeline to ensure timely event delivery
6. Provide clear recommendations with justifications

Respond to the coordinator agent or user in a helpful, professional manner. Ask clarifying questions when needed to gather complete project management requirements.
"""


def create_project_management_graph():
    """
    Create the project management agent graph.
    
    Returns:
        Compiled LangGraph for the project management agent
    """
    # Initialize the LLM
    llm = get_llm(temperature=0.2)
    
    # Initialize tools
    tools = [
        TaskManagementTool(),
        MilestoneManagementTool(),
        RiskManagementTool(),
        TimelineGenerationTool(),
        ProjectPlanGenerationTool(),
        RequirementsTool(),
        MonitoringTool(),
        ReportingTool(),
        ProjectManagementSearchTool()
    ]
    
    # Create the tool node
    tool_node = ToolNode(tools)
    
    # Define the nodes
    def analyze_requirements(state: ProjectManagementStateDict) -> ProjectManagementStateDict:
        """
        Analyze event requirements to determine project management needs.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Get the last message
        last_message = state["messages"][-1]["content"] if state["messages"] else ""
        
        # Create a prompt for the LLM to analyze project management requirements
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps analyze event planning requirements to determine project management needs.
Based on the event details and conversation, extract key information about:
1. Task requirements (types of tasks, dependencies, assignments)
2. Timeline requirements (milestones, deadlines, critical path)
3. Risk management needs (potential risks, mitigation strategies)

Provide a structured analysis of the project management requirements for this event."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}

Analyze these event details and the conversation to determine the project management requirements for this event. Focus on task management, timeline control, and risk management needs.""")
        ])
        
        # Analyze requirements using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Add the analysis to messages
        state["messages"].append({
            "role": "assistant",
            "content": result.content
        })
        
        # Update phase and next steps
        state["current_phase"] = "requirements_analysis"
        state["next_steps"] = ["manage_tasks", "manage_milestones", "manage_risks", "generate_timeline"]
        
        return state
    
    def manage_tasks(state: ProjectManagementStateDict) -> ProjectManagementStateDict:
        """
        Manage tasks for the project.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with task information
        """
        # Create a prompt for the LLM to determine task management needs
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps identify task management needs for events.
Based on the event details and conversation, determine:
1. What types of tasks are needed
2. Task dependencies and sequencing
3. Task assignments
4. Task priorities

Provide specific recommendations for tasks that would be appropriate for this event."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Current tasks: {state['tasks']}

Identify task management needs for this event and recommend specific tasks. If tasks are already identified, suggest improvements or additions.""")
        ])
        
        # Determine task management needs using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the TaskManagementTool to list tasks
        task_management_tool = TaskManagementTool()
        task_result = task_management_tool._run(action="list")
        
        # Update state with tasks
        state["tasks"] = task_result.get("tasks", [])
        
        # Add task management to messages
        task_summary = "Current Tasks:\n"
        for task in state["tasks"]:
            status = task.get("status", "unknown")
            priority = task.get("priority", "medium")
            assigned_to = task.get("assigned_to", "Unassigned")
            task_summary += f"- {task['name']} ({priority} priority): {status}, Assigned to: {assigned_to}\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"{result.content}\n\n{task_summary}\n\nI've identified and managed the tasks for this event. Would you like to add more tasks or modify the existing ones?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "task_management"
        state["next_steps"] = ["manage_milestones", "manage_risks", "generate_timeline"]
        
        return state
    
    def manage_milestones(state: ProjectManagementStateDict) -> ProjectManagementStateDict:
        """
        Manage milestones for the project.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with milestone information
        """
        # Create a prompt for the LLM to determine milestone needs
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps identify milestone needs for events.
Based on the event details and conversation, determine:
1. What key milestones are needed
2. Milestone dates and sequencing
3. Milestone dependencies
4. Milestone tracking

Provide specific recommendations for milestones that would be appropriate for this event."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Current milestones: {state['milestones']}
Tasks: {state['tasks']}

Identify milestone needs for this event and recommend specific milestones. If milestones are already identified, suggest improvements or additions.""")
        ])
        
        # Determine milestone needs using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the MilestoneManagementTool to list milestones
        milestone_management_tool = MilestoneManagementTool()
        milestone_result = milestone_management_tool._run(action="list")
        
        # Update state with milestones
        state["milestones"] = milestone_result.get("milestones", [])
        
        # Add milestone management to messages
        milestone_summary = "Current Milestones:\n"
        for milestone in state["milestones"]:
            status = milestone.get("status", "unknown")
            date = milestone.get("date", "No date set")
            milestone_summary += f"- {milestone['name']}: {status}, Date: {date}\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"{result.content}\n\n{milestone_summary}\n\nI've identified and managed the milestones for this event. Would you like to add more milestones or modify the existing ones?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "milestone_management"
        state["next_steps"] = ["manage_risks", "generate_timeline"]
        
        return state
    
    def manage_risks(state: ProjectManagementStateDict) -> ProjectManagementStateDict:
        """
        Manage risks for the project.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with risk information
        """
        # Create a prompt for the LLM to determine risk management needs
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps identify risk management needs for events.
Based on the event details and conversation, determine:
1. What potential risks exist
2. Risk probability and impact
3. Risk mitigation strategies
4. Contingency plans

Provide specific recommendations for risks that should be monitored for this event."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Current risks: {state['risks']}
Tasks: {state['tasks']}
Milestones: {state['milestones']}

Identify risk management needs for this event and recommend specific risks to monitor. If risks are already identified, suggest improvements or additions.""")
        ])
        
        # Determine risk management needs using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the RiskManagementTool to list risks
        risk_management_tool = RiskManagementTool()
        risk_result = risk_management_tool._run(action="list")
        
        # Update state with risks
        state["risks"] = risk_result.get("risks", [])
        
        # Add risk management to messages
        risk_summary = "Current Risks:\n"
        for risk in state["risks"]:
            probability = risk.get("probability", "unknown")
            impact = risk.get("impact", "unknown")
            status = risk.get("status", "identified")
            risk_summary += f"- {risk['name']} (Probability: {probability}, Impact: {impact}): {status}\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"{result.content}\n\n{risk_summary}\n\nI've identified and managed the risks for this event. Would you like to add more risks or modify the existing ones?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "risk_management"
        state["next_steps"] = ["generate_timeline", "generate_project_plan"]
        
        return state
    
    def generate_timeline(state: ProjectManagementStateDict) -> ProjectManagementStateDict:
        """
        Generate a timeline for the project.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with timeline information
        """
        # Use the TimelineGenerationTool to generate a timeline
        timeline_generation_tool = TimelineGenerationTool()
        
        # Generate the timeline
        timeline_result = timeline_generation_tool._run(
            event_details=state["event_details"],
            tasks=state["tasks"],
            milestones=state["milestones"]
        )
        
        # Update state with timeline
        state["timeline"] = timeline_result.get("timeline", {})
        
        # Create a prompt for the LLM to analyze the timeline
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps analyze project timelines.
Based on the timeline, tasks, and milestones, provide an analysis of:
1. Critical path and potential bottlenecks
2. Timeline feasibility
3. Resource allocation over time
4. Recommendations for optimization

Provide a clear, concise analysis with specific recommendations."""),
            HumanMessage(content=f"""Timeline: {state['timeline']}
Tasks: {state['tasks']}
Milestones: {state['milestones']}

Analyze this timeline and provide insights and recommendations.""")
        ])
        
        # Analyze the timeline using the LLM
        chain = prompt | llm
        result = chain.invoke({})
        
        # Add timeline generation to messages
        state["messages"].append({
            "role": "assistant",
            "content": f"I've generated a timeline for this event:\n\n{result.content}\n\nThe timeline includes {len(state['tasks'])} tasks and {len(state['milestones'])} milestones. Would you like to make any adjustments to this timeline?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "timeline_generation"
        state["next_steps"] = ["generate_project_plan"]
        
        return state
    
    def generate_project_plan(state: ProjectManagementStateDict) -> ProjectManagementStateDict:
        """
        Generate a comprehensive project plan.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with project plan
        """
        # Use the ProjectPlanGenerationTool to generate a project plan
        project_plan_tool = ProjectPlanGenerationTool()
        
        # Generate a unique event ID
        import uuid
        event_id = str(uuid.uuid4())
        
        # Generate the project plan
        plan_result = project_plan_tool._run(
            event_id=event_id,
            event_details=state["event_details"],
            timeline=state["timeline"],
            tasks=state["tasks"],
            milestones=state["milestones"],
            risks=state["risks"]
        )
        
        # Update state with project plan
        state["project_plan"] = plan_result.get("project_plan", {})
        
        # Create a prompt for the LLM to generate a summary of the project plan
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps summarize project plans for events.
Create a clear, concise summary of the project plan that highlights:
1. Key tasks and milestones
2. Critical path and timeline
3. Risk management approach
4. Overall status and next steps

The summary should be professional and easy to understand."""),
            HumanMessage(content=f"""Project plan: {state['project_plan']}

Create a concise summary of this project plan.""")
        ])
        
        # Generate summary using the LLM
        chain = prompt | llm
        result = chain.invoke({})
        
        # Initialize db_event_id variable
        db_event_id = None
        
        # Save tasks to database
        try:
            from app.db.session import SessionLocal
            from app.db.models_updated import Event, Task
            
            db = SessionLocal()
            
            # Create a new event with an auto-generated integer ID
            event = Event(
                title=state["event_details"].get("title", "New Event"),
                event_type=state["event_details"].get("event_type", "Unknown"),
                description=state["event_details"].get("description", ""),
                start_date=state["event_details"].get("timeline_start"),
                end_date=state["event_details"].get("timeline_end"),
                budget=state["event_details"].get("budget"),
                attendee_count=state["event_details"].get("attendee_count", 0),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            
            # Get the auto-generated integer ID
            db_event_id = event.id
            
            # Store both IDs in the project plan for reference
            # The UUID is for display in the UI, the integer ID is for database operations
            state["project_plan"]["display_id"] = event_id
            state["project_plan"]["db_event_id"] = db_event_id
            
            # Add tasks to database using the integer event ID
            for task_data in state["tasks"]:
                task = Task(
                    event_id=db_event_id,  # Use the integer ID for database relations
                    title=task_data["name"],
                    description=task_data["description"],
                    status=task_data["status"],
                    assigned_agent=task_data["assigned_to"],
                    due_date=task_data.get("end_date"),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(task)
            
            db.commit()
            
            # Log the tasks for debugging
            print(f"Added {len(state['tasks'])} tasks for event ID {db_event_id}")
            tasks_in_db = db.query(Task).filter(Task.event_id == db_event_id).all()
            print(f"Found {len(tasks_in_db)} tasks in database for event ID {db_event_id}")
            
            # Add project plan to messages with the database event ID
            state["messages"].append({
                "role": "assistant",
                "content": f"I've generated a comprehensive project plan for the event:\n\nEvent ID: {db_event_id}\n\n{result.content}\n\nThe project plan includes a detailed timeline, task assignments, milestones, and risk management strategies. Would you like me to make any adjustments to this plan?"
            })
        except Exception as e:
            print(f"Error saving tasks to database: {e}")
            
            # If there was an error, still add the message but with the UUID instead
            state["messages"].append({
                "role": "assistant",
                "content": f"I've generated a comprehensive project plan for the event:\n\nEvent ID: {event_id}\n\n{result.content}\n\nThe project plan includes a detailed timeline, task assignments, milestones, and risk management strategies. Would you like me to make any adjustments to this plan?"
            })
        
        # Update phase and next steps
        state["current_phase"] = "plan_generation"
        state["next_steps"] = ["finalize_plan"]
        
        return state
    
    def generate_response(state: ProjectManagementStateDict) -> ProjectManagementStateDict:
        """
        Generate a response to the user or coordinator agent.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create the project management prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=PROJECT_MANAGEMENT_SYSTEM_PROMPT.format(
                current_phase=state["current_phase"],
                event_details=state["event_details"],
                tasks=state["tasks"],
                milestones=state["milestones"],
                risks=state["risks"],
                timeline=state["timeline"],
                project_plan=state["project_plan"],
                next_steps=state["next_steps"]
            )),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Generate response using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Add the response to messages
        new_message = {
            "role": "assistant",
            "content": result.content
        }
        state["messages"].append(new_message)
        
        return state
    
    # Create the graph
    workflow = StateGraph(ProjectManagementStateDict)
    
    # Add nodes
    workflow.add_node("analyze_requirements", analyze_requirements)
    workflow.add_node("manage_tasks", manage_tasks)
    workflow.add_node("manage_milestones", manage_milestones)
    workflow.add_node("manage_risks", manage_risks)
    workflow.add_node("generate_timeline", generate_timeline)
    workflow.add_node("generate_project_plan", generate_project_plan)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("tools", tool_node)
    
    # Add edges
    workflow.add_edge("analyze_requirements", "manage_tasks")
    workflow.add_edge("manage_tasks", "manage_milestones")
    workflow.add_edge("manage_milestones", "manage_risks")
    workflow.add_edge("manage_risks", "generate_timeline")
    workflow.add_edge("generate_timeline", "generate_project_plan")
    workflow.add_edge("generate_project_plan", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Set the entry point
    workflow.set_entry_point("analyze_requirements")
    
    return workflow.compile()


def create_initial_state() -> ProjectManagementStateDict:
    """
    Create the initial state for the project management agent.
    
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
            "timeline_end": None,
            "budget": None,
            "location": None
        },
        "tasks": [],
        "milestones": [],
        "risks": [],
        "timeline": None,
        "project_plan": None,
        "current_phase": "requirements_analysis",
        "next_steps": ["analyze_requirements"]
    }
