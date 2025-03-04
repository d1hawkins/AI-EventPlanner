from typing import Dict, List, Any, TypedDict, Literal, Optional
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.utils.llm_factory import get_llm
from app.tools.financial_tools import (
    BudgetAllocationTool, 
    PaymentTrackingTool, 
    ContractGenerationTool, 
    FinancialReportingTool,
    FinancialPlanGenerationTool
)


# Define the state schema for the Financial Agent
class FinancialStateDict(TypedDict):
    """State for the financial agent."""
    
    messages: List[Dict[str, str]]
    event_details: Dict[str, Any]
    budget: Dict[str, Any]
    expenses: List[Dict[str, Any]]
    contracts: List[Dict[str, Any]]
    payments: List[Dict[str, Any]]
    current_phase: str
    next_steps: List[str]
    financial_plan: Optional[Dict[str, Any]]


# Define the system prompt for the Financial Agent
FINANCIAL_SYSTEM_PROMPT = """You are the Financial Agent for an event planning system. Your role is to:

1. Manage budget allocation and tracking
2. Process payments and handle financial transactions
3. Generate and manage contracts
4. Provide financial reports and analysis
5. Ensure financial compliance and efficiency

Your primary responsibilities include:

Budget Management:
- Budget allocation across categories
- Expense tracking
- Financial forecasting
- Budget adjustments

Payment Processing:
- Invoice management
- Payment scheduling
- Refund handling
- Dispute resolution

Contract Management:
- Contract generation
- Term negotiation
- Signature collection
- Compliance verification

Your current state:
Current phase: {current_phase}
Event details: {event_details}
Budget: {budget}
Expenses: {expenses}
Contracts: {contracts}
Payments: {payments}
Next steps: {next_steps}

Follow these guidelines:
1. Analyze the event requirements to understand the financial needs
2. Create detailed budget allocations based on event type, size, and requirements
3. Track all expenses and payments
4. Generate contracts for vendors and service providers
5. Provide regular financial reports and updates
6. Identify financial risks and propose mitigation strategies

Respond to the coordinator agent or user in a helpful, professional manner. Ask clarifying questions when needed to gather complete financial requirements.
"""


def create_financial_graph():
    """
    Create the financial agent graph.
    
    Returns:
        Compiled LangGraph for the financial agent
    """
    # Initialize the LLM
    llm = get_llm(temperature=0.2)
    
    # Initialize tools
    tools = [
        BudgetAllocationTool(),
        PaymentTrackingTool(),
        ContractGenerationTool(),
        FinancialReportingTool(),
        FinancialPlanGenerationTool()
    ]
    
    # Create the tool node
    tool_node = ToolNode(tools)
    
    # Define the nodes
    def analyze_budget_requirements(state: FinancialStateDict) -> FinancialStateDict:
        """
        Analyze event requirements to determine budget needs.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Get the last message
        last_message = state["messages"][-1]["content"] if state["messages"] else ""
        
        # Create a prompt for the LLM to analyze budget requirements
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps analyze event financial requirements.
Based on the event details and conversation, extract key information about:
1. Budget constraints and expectations
2. Financial priorities
3. Payment timelines
4. Contract requirements
5. Financial reporting needs

Provide a structured analysis of the financial requirements for this event."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}

Analyze these event details and the conversation to determine the financial requirements for this event. Focus on budget constraints, financial priorities, and payment timelines.""")
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
        state["current_phase"] = "budget_analysis"
        state["next_steps"] = ["allocate_budget", "track_expenses", "manage_contracts"]
        
        return state
    
    def allocate_budget(state: FinancialStateDict) -> FinancialStateDict:
        """
        Allocate budget across different categories.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to extract budget allocation criteria
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps extract budget allocation criteria from event details and conversation.
Extract the following information:
1. Event type
2. Total budget amount
3. Attendee count
4. Event duration in days
5. Location
6. Special requirements

Return the extracted information in a structured format."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}

Extract the budget allocation criteria from these event details and the conversation. If any information is missing, make reasonable assumptions based on the available data.""")
        ])
        
        # Extract budget allocation criteria using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the BudgetAllocationTool to allocate budget
        budget_allocation_tool = BudgetAllocationTool()
        
        # Extract parameters from the event details and LLM result
        event_type = state["event_details"].get("event_type", "conference")
        total_budget = state["event_details"].get("budget", 50000.0)
        attendee_count = state["event_details"].get("attendee_count", 100)
        duration_days = 1
        
        # Try to extract duration from timeline
        if "timeline_start" in state["event_details"] and "timeline_end" in state["event_details"]:
            try:
                start_date = datetime.strptime(state["event_details"]["timeline_start"], "%Y-%m-%d")
                end_date = datetime.strptime(state["event_details"]["timeline_end"], "%Y-%m-%d")
                duration_days = (end_date - start_date).days + 1
            except (ValueError, TypeError):
                duration_days = 1
        
        location = state["event_details"].get("location", "Unknown")
        
        # Allocate budget
        budget_results = budget_allocation_tool._run(
            event_type=event_type,
            total_budget=float(total_budget),
            attendee_count=int(attendee_count),
            duration_days=int(duration_days),
            location=location
        )
        
        # Update state with budget
        state["budget"] = budget_results.get("budget", {})
        
        # Add budget allocation to messages
        budget_summary = "Budget Allocation:\n"
        for category in state["budget"].get("categories", []):
            budget_summary += f"- {category['name']}: ${category['amount']:.2f} ({category['amount']/state['budget']['total_amount']*100:.1f}%)\n"
            if category.get("subcategories"):
                for subcategory in category["subcategories"]:
                    budget_summary += f"  * {subcategory['name']}: ${subcategory['amount']:.2f}\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"I've allocated the budget for this event based on the requirements:\n\n{budget_summary}\n\nTotal Budget: ${state['budget']['total_amount']:.2f}\nContingency Fund: ${budget_results.get('contingency_fund', 0):.2f}\n\nWould you like to make any adjustments to this allocation?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "budget_allocation"
        state["next_steps"] = ["track_expenses", "manage_contracts", "generate_financial_plan"]
        
        return state
    
    def track_expenses(state: FinancialStateDict) -> FinancialStateDict:
        """
        Track expenses and payments.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to extract expense information
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps extract expense information from conversation.
Extract the following information:
1. Expense type
2. Amount
3. Vendor
4. Description
5. Due date
6. Payment status
7. Payment method

Return the extracted information in a structured format."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Budget: {state['budget']}

Extract expense information from the conversation. If there are no specific expenses mentioned, respond with 'No specific expenses found in the conversation.'""")
        ])
        
        # Extract expense information using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Check if specific expenses were found
        if "No specific expenses found" in result.content:
            # Create sample expenses based on budget categories
            if "expenses" not in state or not state["expenses"]:
                state["expenses"] = []
                
                # Get budget categories
                categories = state["budget"].get("categories", [])
                
                # Create a sample expense for each category
                for category in categories:
                    # Use the PaymentTrackingTool to create an expense
                    payment_tracking_tool = PaymentTrackingTool()
                    
                    # Create a sample expense
                    expense_result = payment_tracking_tool._run(
                        expense_type=category["name"],
                        amount=category["amount"] * 0.5,  # Use 50% of the budget as a sample expense
                        vendor=f"{category['name']} Provider",
                        description=f"{category['name']} for event",
                        due_date=(datetime.now().strftime("%Y-%m-%d")),
                        payment_status="pending"
                    )
                    
                    # Add the expense to the state
                    state["expenses"].append(expense_result["expense"])
            
            # Add expense tracking to messages
            expense_summary = "Current Expenses:\n"
            total_expenses = sum(expense["amount"] for expense in state["expenses"])
            for expense in state["expenses"]:
                expense_summary += f"- {expense['category']}: ${expense['amount']:.2f} - {expense['vendor']} ({expense['payment_status']})\n"
            
            state["messages"].append({
                "role": "assistant",
                "content": f"I've tracked the following expenses for this event:\n\n{expense_summary}\n\nTotal Expenses: ${total_expenses:.2f}\nRemaining Budget: ${state['budget']['total_amount'] - total_expenses:.2f}\n\nWould you like to add or modify any expenses?"
            })
        else:
            # Use the PaymentTrackingTool to track the expense
            payment_tracking_tool = PaymentTrackingTool()
            
            # Extract expense information from the LLM result
            # In a real implementation, this would parse the LLM output more robustly
            # For now, we'll use some default values
            expense_type = "Venue"
            amount = 5000.0
            vendor = "Sample Vendor"
            description = "Sample expense"
            due_date = datetime.now().strftime("%Y-%m-%d")
            payment_status = "pending"
            
            # Track the expense
            expense_result = payment_tracking_tool._run(
                expense_type=expense_type,
                amount=amount,
                vendor=vendor,
                description=description,
                due_date=due_date,
                payment_status=payment_status
            )
            
            # Add the expense to the state
            if "expenses" not in state:
                state["expenses"] = []
            state["expenses"].append(expense_result["expense"])
            
            # Add expense tracking to messages
            state["messages"].append({
                "role": "assistant",
                "content": f"I've tracked the following expense:\n\n- {expense_type}: ${amount:.2f} - {vendor} ({payment_status})\n\nThe expense has been added to the tracking system."
            })
        
        # Update phase and next steps
        state["current_phase"] = "expense_tracking"
        state["next_steps"] = ["manage_contracts", "generate_financial_report", "generate_financial_plan"]
        
        return state
    
    def manage_contracts(state: FinancialStateDict) -> FinancialStateDict:
        """
        Manage vendor and service provider contracts.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to extract contract information
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps extract contract information from conversation.
Extract the following information:
1. Vendor name
2. Service type
3. Contract amount
4. Start date
5. End date
6. Contract terms

Return the extracted information in a structured format."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Budget: {state['budget']}
Expenses: {state['expenses']}

Extract contract information from the conversation. If there are no specific contracts mentioned, respond with 'No specific contracts found in the conversation.'""")
        ])
        
        # Extract contract information using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Check if specific contracts were found
        if "No specific contracts found" in result.content:
            # Create sample contracts based on expenses
            if "contracts" not in state or not state["contracts"]:
                state["contracts"] = []
                
                # Get expenses
                expenses = state["expenses"]
                
                # Create a sample contract for each expense
                for expense in expenses:
                    # Use the ContractGenerationTool to create a contract
                    contract_generation_tool = ContractGenerationTool()
                    
                    # Get event timeline
                    start_date = state["event_details"].get("timeline_start", datetime.now().strftime("%Y-%m-%d"))
                    end_date = state["event_details"].get("timeline_end", (datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"))
                    
                    # Create a sample contract
                    contract_result = contract_generation_tool._run(
                        vendor_name=expense["vendor"],
                        service_type=expense["category"],
                        amount=expense["amount"],
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    # Add the contract to the state
                    state["contracts"].append(contract_result["contract"])
            
            # Add contract management to messages
            contract_summary = "Current Contracts:\n"
            for contract in state["contracts"]:
                contract_summary += f"- {contract['vendor_name']}: {contract['service_type']} - ${contract['amount']:.2f} ({contract['status']})\n"
            
            state["messages"].append({
                "role": "assistant",
                "content": f"I've generated the following contracts for this event:\n\n{contract_summary}\n\nWould you like to view or modify any of these contracts?"
            })
        else:
            # Use the ContractGenerationTool to generate the contract
            contract_generation_tool = ContractGenerationTool()
            
            # Extract contract information from the LLM result
            # In a real implementation, this would parse the LLM output more robustly
            # For now, we'll use some default values
            vendor_name = "Sample Vendor"
            service_type = "Venue"
            amount = 5000.0
            start_date = datetime.now().strftime("%Y-%m-%d")
            end_date = (datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Generate the contract
            contract_result = contract_generation_tool._run(
                vendor_name=vendor_name,
                service_type=service_type,
                amount=amount,
                start_date=start_date,
                end_date=end_date
            )
            
            # Add the contract to the state
            if "contracts" not in state:
                state["contracts"] = []
            state["contracts"].append(contract_result["contract"])
            
            # Add contract generation to messages
            state["messages"].append({
                "role": "assistant",
                "content": f"I've generated a contract for {vendor_name} for {service_type} services:\n\n{contract_result['contract_text']}\n\nThe contract has been added to the system."
            })
        
        # Update phase and next steps
        state["current_phase"] = "contract_management"
        state["next_steps"] = ["generate_financial_report", "generate_financial_plan"]
        
        return state
    
    def generate_financial_report(state: FinancialStateDict) -> FinancialStateDict:
        """
        Generate financial reports.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to determine report type
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps determine what type of financial report is needed.
Based on the conversation, determine what type of financial report is needed:
1. Budget report
2. Expense report
3. Summary report

Return the report type."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Budget: {state['budget']}
Expenses: {state['expenses']}
Contracts: {state['contracts']}

Determine what type of financial report is needed based on the conversation.""")
        ])
        
        # Determine report type using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Extract report type from the LLM result
        report_type = "summary"
        if "budget" in result.content.lower():
            report_type = "budget"
        elif "expense" in result.content.lower():
            report_type = "expenses"
        
        # Use the FinancialReportingTool to generate the report
        financial_reporting_tool = FinancialReportingTool()
        
        # Generate the report
        report_result = financial_reporting_tool._run(
            report_type=report_type,
            budget=state["budget"],
            expenses=state["expenses"]
        )
        
        # Add the report to messages
        state["messages"].append({
            "role": "assistant",
            "content": f"I've generated a {report_type} report for this event:\n\n{report_result['summary']}\n\nWould you like any other financial reports or information?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "financial_reporting"
        state["next_steps"] = ["generate_financial_plan"]
        
        return state
    
    def generate_financial_plan(state: FinancialStateDict) -> FinancialStateDict:
        """
        Generate a comprehensive financial plan.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Use the FinancialPlanGenerationTool to generate a financial plan
        financial_plan_tool = FinancialPlanGenerationTool()
        
        # Generate a unique event ID
        import uuid
        event_id = str(uuid.uuid4())
        
        # Generate the financial plan
        plan_result = financial_plan_tool._run(
            event_id=event_id,
            event_details=state["event_details"],
            budget=state["budget"],
            expenses=state["expenses"],
            contracts=state["contracts"]
        )
        
        # Update state with financial plan
        state["financial_plan"] = plan_result.get("financial_plan", {})
        
        # Add the financial plan to messages
        state["messages"].append({
            "role": "assistant",
            "content": f"I've generated a comprehensive financial plan for this event:\n\n{plan_result['summary']}\n\nThis plan includes budget allocation, payment schedule, and financial risk management strategies. Would you like to make any adjustments to this plan?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "plan_generation"
        state["next_steps"] = ["finalize_plan"]
        
        return state
    
    def generate_response(state: FinancialStateDict) -> FinancialStateDict:
        """
        Generate a response to the user or coordinator agent.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create the financial prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=FINANCIAL_SYSTEM_PROMPT.format(
                current_phase=state["current_phase"],
                event_details=state["event_details"],
                budget=state["budget"],
                expenses=state["expenses"],
                contracts=state["contracts"],
                payments=state["payments"],
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
    workflow = StateGraph(FinancialStateDict)
    
    # Add nodes
    workflow.add_node("analyze_budget_requirements", analyze_budget_requirements)
    workflow.add_node("allocate_budget", allocate_budget)
    workflow.add_node("track_expenses", track_expenses)
    workflow.add_node("manage_contracts", manage_contracts)
    workflow.add_node("generate_financial_report", generate_financial_report)
    workflow.add_node("generate_financial_plan", generate_financial_plan)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("tools", tool_node)
    
    # Add edges
    workflow.add_edge("analyze_budget_requirements", "allocate_budget")
    workflow.add_edge("allocate_budget", "track_expenses")
    workflow.add_edge("track_expenses", "manage_contracts")
    workflow.add_edge("manage_contracts", "generate_financial_report")
    workflow.add_edge("generate_financial_report", "generate_financial_plan")
    workflow.add_edge("generate_financial_plan", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Set the entry point
    workflow.set_entry_point("analyze_budget_requirements")
    
    return workflow.compile()


def create_initial_state() -> FinancialStateDict:
    """
    Create the initial state for the financial agent.
    
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
        "budget": {},
        "expenses": [],
        "contracts": [],
        "payments": [],
        "current_phase": "initial_assessment",
        "next_steps": ["analyze_budget_requirements"],
        "financial_plan": None
    }
