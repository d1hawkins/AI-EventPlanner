from typing import Dict, Any, List, Tuple, Optional, Annotated, TypedDict, Literal
import json
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.utils.llm_factory import get_llm


# Define the state schema
class ComplianceSecurityState(TypedDict):
    """State for the Compliance & Security Agent."""
    
    event_details: Dict[str, Any]
    messages: List[Dict[str, Any]]
    current_phase: str
    next_steps: List[str]
    compliance_requirements: List[Dict[str, Any]]
    security_protocols: List[Dict[str, Any]]
    data_protection_measures: List[Dict[str, Any]]
    compliance_audits: List[Dict[str, Any]]
    incident_response_plans: List[Dict[str, Any]]
    compliance_reports: List[Dict[str, Any]]
    regulatory_updates: List[Dict[str, Any]]


def create_initial_state() -> ComplianceSecurityState:
    """Create the initial state for the Compliance & Security Agent."""
    
    return {
        "event_details": {
            "event_type": "",
            "title": "",
            "description": "",
            "attendee_count": 0,
            "scale": "",
            "timeline_start": "",
            "timeline_end": "",
            "budget": 0,
            "location": ""
        },
        "messages": [],
        "current_phase": "analyze_requirements",
        "next_steps": [
            "Analyze compliance requirements",
            "Plan security measures",
            "Implement data protection"
        ],
        "compliance_requirements": [],
        "security_protocols": [],
        "data_protection_measures": [],
        "compliance_audits": [],
        "incident_response_plans": [],
        "compliance_reports": [],
        "regulatory_updates": []
    }


def analyze_requirements(state: ComplianceSecurityState) -> ComplianceSecurityState:
    """
    Analyze event details to determine compliance requirements.
    
    Args:
        state: Current state
        
    Returns:
        Updated state
    """
    # Get the LLM
    llm = get_llm()
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are the Compliance & Security Agent, responsible for ensuring regulatory compliance and security for events.
        
Your task is to analyze the event details and determine the compliance requirements that apply to this event.

Consider the following factors:
1. Event type and scale
2. Location and applicable jurisdictions
3. Attendee count and demographics
4. Data collection and processing activities
5. Security considerations

Provide a comprehensive analysis of the compliance requirements for this event."""),
        MessagesPlaceholder(variable_name="messages"),
        HumanMessage(content="""Based on the event details, analyze the compliance requirements that apply to this event.

Event Details:
{event_details}

Provide your analysis in the following format:
1. Applicable regulations
2. Key compliance requirements
3. Priority compliance actions
4. Recommended security measures
5. Data protection considerations""")
    ])
    
    # Create the chain
    chain = prompt | llm | StrOutputParser()
    
    # Run the chain
    response = chain.invoke({
        "messages": [m for m in state["messages"] if not m.get("ephemeral", False)],
        "event_details": json.dumps(state["event_details"], indent=2)
    })
    
    # Update the state
    new_state = state.copy()
    new_state["messages"].append({
        "role": "assistant",
        "content": response
    })
    new_state["current_phase"] = "track_requirements"
    
    # Extract compliance requirements from the response
    # In a real implementation, this would parse the response to extract structured data
    # For now, we'll just add a mock requirement
    new_state["compliance_requirements"].append({
        "name": "Data Protection Compliance",
        "description": "Ensure compliance with data protection regulations applicable to the event",
        "category": "data_protection",
        "jurisdiction": "global",
        "applicable_event_types": ["all"],
        "documentation_needed": [
            "Privacy Policy",
            "Data Processing Agreement",
            "Consent Forms"
        ],
        "verification_steps": [
            "Review data collection processes",
            "Verify consent mechanisms",
            "Audit data storage and security"
        ],
        "status": "not_started"
    })
    
    return new_state


def track_requirements(state: ComplianceSecurityState) -> ComplianceSecurityState:
    """
    Track and manage compliance requirements.
    
    Args:
        state: Current state
        
    Returns:
        Updated state
    """
    # Get the LLM
    llm = get_llm()
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are the Compliance & Security Agent, responsible for ensuring regulatory compliance and security for events.
        
Your task is to track and manage compliance requirements for this event.

For each requirement, you should:
1. Document the requirement details
2. Identify necessary documentation
3. Define verification steps
4. Assign a status

Provide a comprehensive tracking of compliance requirements for this event."""),
        MessagesPlaceholder(variable_name="messages"),
        HumanMessage(content="""Based on the compliance analysis, track and manage the compliance requirements for this event.

Event Details:
{event_details}

Current Requirements:
{requirements}

Provide your tracking in the following format:
1. Requirement details
2. Documentation needed
3. Verification steps
4. Current status
5. Next actions""")
    ])
    
    # Create the chain
    chain = prompt | llm | StrOutputParser()
    
    # Run the chain
    response = chain.invoke({
        "messages": [m for m in state["messages"] if not m.get("ephemeral", False)],
        "event_details": json.dumps(state["event_details"], indent=2),
        "requirements": json.dumps(state["compliance_requirements"], indent=2)
    })
    
    # Update the state
    new_state = state.copy()
    new_state["messages"].append({
        "role": "assistant",
        "content": response
    })
    new_state["current_phase"] = "plan_security"
    
    return new_state


def plan_security(state: ComplianceSecurityState) -> ComplianceSecurityState:
    """
    Plan security measures for the event.
    
    Args:
        state: Current state
        
    Returns:
        Updated state
    """
    # Get the LLM
    llm = create_llm()
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are the Compliance & Security Agent, responsible for ensuring regulatory compliance and security for events.
        
Your task is to plan security measures for this event.

Consider the following factors:
1. Event type, scale, and venue
2. Attendee count and demographics
3. High-profile attendees or speakers
4. Potential security threats
5. Access control requirements

Provide a comprehensive security plan for this event."""),
        MessagesPlaceholder(variable_name="messages"),
        HumanMessage(content="""Based on the event details, plan security measures for this event.

Event Details:
{event_details}

Provide your security plan in the following format:
1. Security risk assessment
2. Physical security measures
3. Access control protocols
4. Security staffing requirements
5. Emergency response procedures""")
    ])
    
    # Create the chain
    chain = prompt | llm | StrOutputParser()
    
    # Run the chain
    response = chain.invoke({
        "messages": [m for m in state["messages"] if not m.get("ephemeral", False)],
        "event_details": json.dumps(state["event_details"], indent=2)
    })
    
    # Update the state
    new_state = state.copy()
    new_state["messages"].append({
        "role": "assistant",
        "content": response
    })
    new_state["current_phase"] = "implement_data_protection"
    
    # Extract security protocols from the response
    # In a real implementation, this would parse the response to extract structured data
    # For now, we'll just add a mock protocol
    new_state["security_protocols"].append({
        "name": "Access Control Protocol",
        "description": "Protocol for controlling access to the event and restricted areas",
        "category": "access_control",
        "risk_level": "medium",
        "implementation_steps": [
            "Define access zones",
            "Implement badge system",
            "Train security personnel"
        ],
        "verification_method": "Test access control system before event",
        "status": "not_implemented"
    })
    
    return new_state


def implement_data_protection(state: ComplianceSecurityState) -> ComplianceSecurityState:
    """
    Implement data protection measures.
    
    Args:
        state: Current state
        
    Returns:
        Updated state
    """
    # Get the LLM
    llm = create_llm()
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are the Compliance & Security Agent, responsible for ensuring regulatory compliance and security for events.
        
Your task is to implement data protection measures for this event.

Consider the following factors:
1. Types of data collected
2. Data processing activities
3. Applicable data protection regulations
4. Data security requirements
5. Data subject rights

Provide a comprehensive data protection plan for this event."""),
        MessagesPlaceholder(variable_name="messages"),
        HumanMessage(content="""Based on the event details, implement data protection measures for this event.

Event Details:
{event_details}

Provide your data protection plan in the following format:
1. Data inventory and classification
2. Legal basis for processing
3. Privacy notice and consent mechanisms
4. Data security measures
5. Data subject rights procedures""")
    ])
    
    # Create the chain
    chain = prompt | llm | StrOutputParser()
    
    # Run the chain
    response = chain.invoke({
        "messages": [m for m in state["messages"] if not m.get("ephemeral", False)],
        "event_details": json.dumps(state["event_details"], indent=2)
    })
    
    # Update the state
    new_state = state.copy()
    new_state["messages"].append({
        "role": "assistant",
        "content": response
    })
    new_state["current_phase"] = "conduct_audit"
    
    # Extract data protection measures from the response
    # In a real implementation, this would parse the response to extract structured data
    # For now, we'll just add a mock measure
    new_state["data_protection_measures"].append({
        "name": "Privacy Notice Implementation",
        "description": "Implementation of clear privacy notice for attendees",
        "data_types_covered": ["personal data", "contact information"],
        "applicable_regulations": ["GDPR", "CCPA"],
        "implementation_steps": [
            "Draft privacy notice",
            "Review with legal team",
            "Make accessible to attendees"
        ],
        "status": "not_implemented"
    })
    
    return new_state


def conduct_audit(state: ComplianceSecurityState) -> ComplianceSecurityState:
    """
    Conduct a compliance audit.
    
    Args:
        state: Current state
        
    Returns:
        Updated state
    """
    # Get the LLM
    llm = create_llm()
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are the Compliance & Security Agent, responsible for ensuring regulatory compliance and security for events.
        
Your task is to conduct a compliance audit for this event.

Consider the following factors:
1. Compliance requirements
2. Security protocols
3. Data protection measures
4. Documentation and evidence
5. Gaps and remediation

Provide a comprehensive compliance audit for this event."""),
        MessagesPlaceholder(variable_name="messages"),
        HumanMessage(content="""Based on the event details and compliance measures, conduct a compliance audit for this event.

Event Details:
{event_details}

Compliance Requirements:
{requirements}

Security Protocols:
{protocols}

Data Protection Measures:
{measures}

Provide your audit in the following format:
1. Audit scope and objectives
2. Compliance assessment
3. Security assessment
4. Data protection assessment
5. Findings and recommendations""")
    ])
    
    # Create the chain
    chain = prompt | llm | StrOutputParser()
    
    # Run the chain
    response = chain.invoke({
        "messages": [m for m in state["messages"] if not m.get("ephemeral", False)],
        "event_details": json.dumps(state["event_details"], indent=2),
        "requirements": json.dumps(state["compliance_requirements"], indent=2),
        "protocols": json.dumps(state["security_protocols"], indent=2),
        "measures": json.dumps(state["data_protection_measures"], indent=2)
    })
    
    # Update the state
    new_state = state.copy()
    new_state["messages"].append({
        "role": "assistant",
        "content": response
    })
    new_state["current_phase"] = "plan_incident_response"
    
    # Extract audit results from the response
    # In a real implementation, this would parse the response to extract structured data
    # For now, we'll just add a mock audit
    new_state["compliance_audits"].append({
        "name": "Pre-Event Compliance Audit",
        "description": "Comprehensive audit of compliance measures before the event",
        "requirements_checked": ["Data Protection Compliance"],
        "findings": [
            {
                "requirement": "Data Protection Compliance",
                "status": "partially_compliant",
                "details": "Privacy notice implemented but consent mechanisms need improvement"
            }
        ],
        "recommendations": [
            "Improve consent collection mechanisms",
            "Enhance data security measures",
            "Document data processing activities"
        ],
        "completion_date": datetime.now().isoformat(),
        "status": "completed"
    })
    
    return new_state


def plan_incident_response(state: ComplianceSecurityState) -> ComplianceSecurityState:
    """
    Plan incident response procedures.
    
    Args:
        state: Current state
        
    Returns:
        Updated state
    """
    # Get the LLM
    llm = create_llm()
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are the Compliance & Security Agent, responsible for ensuring regulatory compliance and security for events.
        
Your task is to plan incident response procedures for this event.

Consider the following factors:
1. Potential incident types
2. Response team structure
3. Communication protocols
4. Escalation procedures
5. Post-incident activities

Provide a comprehensive incident response plan for this event."""),
        MessagesPlaceholder(variable_name="messages"),
        HumanMessage(content="""Based on the event details and security assessment, plan incident response procedures for this event.

Event Details:
{event_details}

Security Protocols:
{protocols}

Provide your incident response plan in the following format:
1. Incident types and severity levels
2. Response team roles and responsibilities
3. Incident response procedures
4. Communication protocols
5. Post-incident activities""")
    ])
    
    # Create the chain
    chain = prompt | llm | StrOutputParser()
    
    # Run the chain
    response = chain.invoke({
        "messages": [m for m in state["messages"] if not m.get("ephemeral", False)],
        "event_details": json.dumps(state["event_details"], indent=2),
        "protocols": json.dumps(state["security_protocols"], indent=2)
    })
    
    # Update the state
    new_state = state.copy()
    new_state["messages"].append({
        "role": "assistant",
        "content": response
    })
    new_state["current_phase"] = "generate_report"
    
    # Extract incident response plan from the response
    # In a real implementation, this would parse the response to extract structured data
    # For now, we'll just add a mock plan
    new_state["incident_response_plans"].append({
        "name": "Event Incident Response Plan",
        "description": "Comprehensive plan for responding to incidents during the event",
        "incident_types_covered": ["security breach", "medical emergency", "evacuation"],
        "response_team": [
            {"role": "Incident Commander", "responsibilities": ["Overall coordination", "Decision making"]},
            {"role": "Security Lead", "responsibilities": ["Security response", "Coordination with security personnel"]},
            {"role": "Communications Officer", "responsibilities": ["Internal communications", "External communications"]}
        ],
        "response_procedures": [
            {
                "incident_type": "security_breach",
                "steps": [
                    "Identify and assess the breach",
                    "Secure affected areas",
                    "Notify security team",
                    "Implement containment measures"
                ]
            }
        ],
        "communication_protocol": {
            "internal_channels": ["Radio", "Emergency phone tree"],
            "external_channels": ["Law enforcement", "Emergency services"]
        },
        "status": "draft"
    })
    
    return new_state


def generate_report(state: ComplianceSecurityState) -> ComplianceSecurityState:
    """
    Generate a comprehensive compliance and security report.
    
    Args:
        state: Current state
        
    Returns:
        Updated state
    """
    # Get the LLM
    llm = create_llm()
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are the Compliance & Security Agent, responsible for ensuring regulatory compliance and security for events.
        
Your task is to generate a comprehensive compliance and security report for this event.

The report should include:
1. Executive summary
2. Compliance status
3. Security measures
4. Data protection status
5. Audit findings
6. Incident response readiness
7. Recommendations

Provide a comprehensive report that can be shared with event organizers and stakeholders."""),
        MessagesPlaceholder(variable_name="messages"),
        HumanMessage(content="""Based on all the compliance and security work done, generate a comprehensive report for this event.

Event Details:
{event_details}

Compliance Requirements:
{requirements}

Security Protocols:
{protocols}

Data Protection Measures:
{measures}

Audit Results:
{audits}

Incident Response Plans:
{plans}

Provide your report in a clear, professional format suitable for sharing with event organizers and stakeholders.""")
    ])
    
    # Create the chain
    chain = prompt | llm | StrOutputParser()
    
    # Run the chain
    response = chain.invoke({
        "messages": [m for m in state["messages"] if not m.get("ephemeral", False)],
        "event_details": json.dumps(state["event_details"], indent=2),
        "requirements": json.dumps(state["compliance_requirements"], indent=2),
        "protocols": json.dumps(state["security_protocols"], indent=2),
        "measures": json.dumps(state["data_protection_measures"], indent=2),
        "audits": json.dumps(state["compliance_audits"], indent=2),
        "plans": json.dumps(state["incident_response_plans"], indent=2)
    })
    
    # Update the state
    new_state = state.copy()
    new_state["messages"].append({
        "role": "assistant",
        "content": response
    })
    new_state["current_phase"] = "monitor_updates"
    
    # Extract report from the response
    # In a real implementation, this would parse the response to extract structured data
    # For now, we'll just add a mock report
    new_state["compliance_reports"].append({
        "title": "Event Compliance and Security Report",
        "description": "Comprehensive report on compliance and security measures for the event",
        "event_details": state["event_details"],
        "requirements_summary": {
            "total": len(state["compliance_requirements"]),
            "compliant": 0,
            "partially_compliant": 1,
            "non_compliant": 0
        },
        "security_summary": {
            "total": len(state["security_protocols"]),
            "implemented": 0,
            "partially_implemented": 0,
            "not_implemented": 1
        },
        "data_protection_summary": {
            "total": len(state["data_protection_measures"]),
            "implemented": 0,
            "partially_implemented": 0,
            "not_implemented": 1
        },
        "findings": [
            {
                "area": "Data Protection",
                "status": "partially_compliant",
                "details": "Privacy notice implemented but consent mechanisms need improvement"
            }
        ],
        "recommendations": [
            "Improve consent collection mechanisms",
            "Implement all security protocols before the event",
            "Conduct a final compliance check one week before the event"
        ],
        "risk_assessment": {
            "overall_risk": "medium",
            "highest_risks": ["Data protection compliance", "Access control"]
        },
        "generated_at": datetime.now().isoformat()
    })
    
    return new_state


def monitor_updates(state: ComplianceSecurityState) -> ComplianceSecurityState:
    """
    Monitor regulatory updates.
    
    Args:
        state: Current state
        
    Returns:
        Updated state
    """
    # Get the LLM
    llm = create_llm()
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are the Compliance & Security Agent, responsible for ensuring regulatory compliance and security for events.
        
Your task is to monitor regulatory updates that might affect this event.

Consider the following factors:
1. Applicable jurisdictions
2. Recent regulatory changes
3. Upcoming regulatory changes
4. Impact on event compliance
5. Required actions

Provide a comprehensive monitoring of regulatory updates for this event."""),
        MessagesPlaceholder(variable_name="messages"),
        HumanMessage(content="""Based on the event details and compliance requirements, monitor regulatory updates that might affect this event.

Event Details:
{event_details}

Compliance Requirements:
{requirements}

Provide your monitoring in the following format:
1. Recent regulatory changes
2. Upcoming regulatory changes
3. Impact assessment
4. Required actions
5. Timeline for implementation""")
    ])
    
    # Create the chain
    chain = prompt | llm | StrOutputParser()
    
    # Run the chain
    response = chain.invoke({
        "messages": [m for m in state["messages"] if not m.get("ephemeral", False)],
        "event_details": json.dumps(state["event_details"], indent=2),
        "requirements": json.dumps(state["compliance_requirements"], indent=2)
    })
    
    # Update the state
    new_state = state.copy()
    new_state["messages"].append({
        "role": "assistant",
        "content": response
    })
    new_state["current_phase"] = "generate_response"
    
    # Extract regulatory updates from the response
    # In a real implementation, this would parse the response to extract structured data
    # For now, we'll just add a mock update
    new_state["regulatory_updates"].append({
        "regulation_name": "Data Protection Regulation Update",
        "update_description": "Recent update to data protection requirements for event organizers",
        "effective_date": (datetime.now()).isoformat(),
        "jurisdiction": "global",
        "impact_assessment": {
            "severity": "medium",
            "areas_affected": ["consent mechanisms", "data retention"],
            "implementation_complexity": "moderate",
            "estimated_effort": "1-2 weeks",
            "cost_implications": "low"
        },
        "required_actions": [
            "Update privacy notice to include new required elements",
            "Revise consent forms to meet new standards",
            "Implement shorter data retention periods"
        ],
        "status": "identified"
    })
    
    return new_state


def generate_response(state: ComplianceSecurityState) -> ComplianceSecurityState:
    """
    Generate a response to the user or coordinator agent.
    
    Args:
        state: Current state
        
    Returns:
        Updated state
    """
    # Get the LLM
    llm = create_llm()
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are the Compliance & Security Agent, responsible for ensuring regulatory compliance and security for events.
        
Your task is to generate a helpful response to the user or coordinator agent.

Your response should be:
1. Clear and concise
2. Focused on compliance and security
3. Actionable and practical
4. Professional and reassuring

Provide a response that addresses the user's query or task."""),
        MessagesPlaceholder(variable_name="messages"),
        HumanMessage(content="""Based on all the compliance and security work done, generate a response to the user or coordinator agent.

Current Phase: {current_phase}

Provide a clear, helpful response that addresses the user's query or task.""")
    ])
    
    # Create the chain
    chain = prompt | llm | StrOutputParser()
    
    # Run the chain
    response = chain.invoke({
        "messages": [m for m in state["messages"] if not m.get("ephemeral", False)],
        "current_phase": state["current_phase"]
    })
    
    # Update the state
    new_state = state.copy()
    new_state["messages"].append({
        "role": "assistant",
        "content": response
    })
    
    return new_state


def decide_next_step(state: ComplianceSecurityState) -> str:
    """
    Decide the next step in the workflow.
    
    Args:
        state: Current state
        
    Returns:
        Next step
    """
    # Check if there's an override
    if "override_next" in state:
        next_step = state["override_next"]
        return next_step
    
    # Otherwise, use the current phase to determine the next step
    current_phase = state["current_phase"]
    
    if current_phase == "analyze_requirements":
        return "track_requirements"
    elif current_phase == "track_requirements":
        return "plan_security"
    elif current_phase == "plan_security":
        return "implement_data_protection"
    elif current_phase == "implement_data_protection":
        return "conduct_audit"
    elif current_phase == "conduct_audit":
        return "plan_incident_response"
    elif current_phase == "plan_incident_response":
        return "generate_report"
    elif current_phase == "generate_report":
        return "monitor_updates"
    elif current_phase == "monitor_updates":
        return "generate_response"
    elif current_phase == "generate_response":
        return END
    else:
        return "generate_response"


def create_compliance_security_graph() -> StateGraph:
    """
    Create the Compliance & Security Agent graph.
    
    Returns:
        StateGraph for the Compliance & Security Agent
    """
    # Create the workflow
    workflow = StateGraph(ComplianceSecurityState)
    
    # Add the nodes
    workflow.add_node("analyze_requirements", analyze_requirements)
    workflow.add_node("track_requirements", track_requirements)
    workflow.add_node("plan_security", plan_security)
    workflow.add_node("implement_data_protection", implement_data_protection)
    workflow.add_node("conduct_audit", conduct_audit)
    workflow.add_node("plan_incident_response", plan_incident_response)
    workflow.add_node("generate_report", generate_report)
    workflow.add_node("monitor_updates", monitor_updates)
    workflow.add_node("generate_response", generate_response)
    
    # Set the entry point
    workflow.set_entry_point("analyze_requirements")
    
    # Add the edges
    workflow.add_conditional_edges(
        "analyze_requirements",
        decide_next_step,
        {
            "track_requirements": "track_requirements",
            "plan_security": "plan_security",
            "implement_data_protection": "implement_data_protection",
            "conduct_audit": "conduct_audit",
            "plan_incident_response": "plan_incident_response",
            "generate_report": "generate_report",
            "monitor_updates": "monitor_updates",
            "generate_response": "generate_response",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "track_requirements",
        decide_next_step,
        {
            "plan_security": "plan_security",
            "implement_data_protection": "implement_data_protection",
            "conduct_audit": "conduct_audit",
            "plan_incident_response": "plan_incident_response",
            "generate_report": "generate_report",
            "monitor_updates": "monitor_updates",
            "generate_response": "generate_response",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "plan_security",
        decide_next_step,
        {
            "implement_data_protection": "implement_data_protection",
            "conduct_audit": "conduct_audit",
            "plan_incident_response": "plan_incident_response",
            "generate_report": "generate_report",
            "monitor_updates": "monitor_updates",
            "generate_response": "generate_response",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "implement_data_protection",
        decide_next_step,
        {
            "conduct_audit": "conduct_audit",
            "plan_incident_response": "plan_incident_response",
            "generate_report": "generate_report",
            "monitor_updates": "monitor_updates",
            "generate_response": "generate_response",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "conduct_audit",
        decide_next_step,
        {
            "plan_incident_response": "plan_incident_response",
            "generate_report": "generate_report",
            "monitor_updates": "monitor_updates",
            "generate_response": "generate_response",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "plan_incident_response",
        decide_next_step,
        {
            "generate_report": "generate_report",
            "monitor_updates": "monitor_updates",
            "generate_response": "generate_response",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "generate_report",
        decide_next_step,
        {
            "monitor_updates": "monitor_updates",
            "generate_response": "generate_response",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "monitor_updates",
        decide_next_step,
        {
            "generate_response": "generate_response",
            END: END
        }
    )
    
    workflow.add_edge("generate_response", END)
    
    # Compile the workflow
    return workflow.compile()
