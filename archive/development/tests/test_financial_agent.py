import asyncio
import json
from datetime import datetime

from app.graphs.financial_graph import create_financial_graph, create_initial_state
from app.tools.financial_tools import (
    BudgetAllocationTool, 
    PaymentTrackingTool, 
    ContractGenerationTool, 
    FinancialReportingTool,
    FinancialPlanGenerationTool
)
from app.config import OPENAI_API_KEY, LLM_MODEL


async def test_financial_agent():
    """
    Test the Financial Agent's functionality.
    """
    # Check if OpenAI API key is set
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    print(f"Using LLM model: {LLM_MODEL}")
    
    # Create the financial graph
    print("Initializing Financial Agent...")
    financial_graph = create_financial_graph()
    
    # Create initial state with some predefined event details
    state = create_initial_state()
    
    # Add initial system message
    state["messages"].append({
        "role": "system",
        "content": "The conversation has started. The Financial Agent will help manage finances for your event.",
        "ephemeral": True
    })
    
    # Set some event details for testing
    state["event_details"] = {
        "event_type": "conference",
        "title": "Tech Innovation Summit 2025",
        "description": "A conference focused on emerging technologies and innovation",
        "attendee_count": 300,
        "scale": "medium",
        "timeline_start": "2025-06-15",
        "timeline_end": "2025-06-17",
        "budget": 75000,
        "location": "San Francisco"
    }
    
    # Test 1: Budget Allocation
    print("\n=== Test 1: Budget Allocation ===")
    
    # Add a user message to trigger budget allocation
    state["messages"].append({
        "role": "user",
        "content": "I need help allocating the budget for our Tech Innovation Summit. We have a total budget of $75,000 for a 3-day conference with 300 attendees in San Francisco."
    })
    
    # Run the financial graph to allocate budget
    result = financial_graph.invoke(state, {"override_next": "allocate_budget"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nFinancial Agent (Budget Allocation):", assistant_messages[-1]["content"])
    
    # Test 2: Expense Tracking
    print("\n=== Test 2: Expense Tracking ===")
    
    # Add a user message to trigger expense tracking
    result["messages"].append({
        "role": "user",
        "content": "I need to track some expenses for the event. We've already paid $15,000 to the venue and $10,000 for catering."
    })
    
    # Run the financial graph to track expenses
    result = financial_graph.invoke(result, {"override_next": "track_expenses"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nFinancial Agent (Expense Tracking):", assistant_messages[-1]["content"])
    
    # Test 3: Contract Management
    print("\n=== Test 3: Contract Management ===")
    
    # Add a user message to trigger contract management
    result["messages"].append({
        "role": "user",
        "content": "I need to create a contract for our AV provider, Tech Solutions, for $7,000 worth of equipment rental from June 15 to June 17, 2025."
    })
    
    # Run the financial graph to manage contracts
    result = financial_graph.invoke(result, {"override_next": "manage_contracts"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nFinancial Agent (Contract Management):", assistant_messages[-1]["content"])
    
    # Test 4: Financial Reporting
    print("\n=== Test 4: Financial Reporting ===")
    
    # Add a user message to trigger financial reporting
    result["messages"].append({
        "role": "user",
        "content": "Can you generate a financial report for the event so far?"
    })
    
    # Run the financial graph to generate a financial report
    result = financial_graph.invoke(result, {"override_next": "generate_financial_report"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nFinancial Agent (Financial Reporting):", assistant_messages[-1]["content"])
    
    # Test 5: Financial Plan Generation
    print("\n=== Test 5: Financial Plan Generation ===")
    
    # Add a user message to trigger financial plan generation
    result["messages"].append({
        "role": "user",
        "content": "Can you create a comprehensive financial plan for the entire event?"
    })
    
    # Run the financial graph to generate a financial plan
    result = financial_graph.invoke(result, {"override_next": "generate_financial_plan"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nFinancial Agent (Financial Plan):", assistant_messages[-1]["content"])
    
    # Print the final state for debugging
    print("\n=== Final State ===")
    print("Budget:", json.dumps(result["budget"], indent=2) if result["budget"] else "None")
    print("Expenses:", f"{len(result['expenses'])} expenses tracked" if result["expenses"] else "None")
    print("Contracts:", f"{len(result['contracts'])} contracts created" if result["contracts"] else "None")
    print("Financial Plan:", "Created" if result["financial_plan"] else "None")
    
    # Test individual tools directly
    print("\n=== Testing Individual Tools ===")
    
    # Test BudgetAllocationTool
    print("\nTesting BudgetAllocationTool:")
    budget_tool = BudgetAllocationTool()
    budget_result = budget_tool._run(
        event_type="conference",
        total_budget=75000.0,
        attendee_count=300,
        duration_days=3,
        location="San Francisco",
        special_requirements=["technology", "premium"]
    )
    print(f"Budget allocated: ${budget_result['budget']['total_amount']:.2f}")
    print(f"Categories: {len(budget_result['budget']['categories'])}")
    print(f"Contingency fund: ${budget_result['contingency_fund']:.2f}")
    
    # Test PaymentTrackingTool
    print("\nTesting PaymentTrackingTool:")
    payment_tool = PaymentTrackingTool()
    expense_result = payment_tool._run(
        expense_type="Venue",
        amount=15000.0,
        vendor="Convention Center",
        description="Venue rental for main event",
        due_date="2025-05-15",
        payment_status="paid",
        payment_method="Bank Transfer"
    )
    print(f"Expense tracked: ${expense_result['expense']['amount']:.2f} for {expense_result['expense']['category']}")
    print(f"Vendor: {expense_result['expense']['vendor']}")
    print(f"Status: {expense_result['expense']['payment_status']}")
    
    # Test ContractGenerationTool
    print("\nTesting ContractGenerationTool:")
    contract_tool = ContractGenerationTool()
    contract_result = contract_tool._run(
        vendor_name="Tech Solutions",
        service_type="AV Equipment",
        amount=7000.0,
        start_date="2025-06-15",
        end_date="2025-06-17",
        terms=["Equipment must be set up and tested 2 hours before event", "Technician must be available throughout the event"]
    )
    print(f"Contract generated for {contract_result['contract']['vendor_name']}")
    print(f"Service: {contract_result['contract']['service_type']}")
    print(f"Amount: ${contract_result['contract']['amount']:.2f}")
    print(f"Status: {contract_result['contract']['status']}")
    
    # Test FinancialReportingTool
    print("\nTesting FinancialReportingTool:")
    reporting_tool = FinancialReportingTool()
    report_result = reporting_tool._run(
        report_type="summary",
        budget=budget_result["budget"],
        expenses=[expense_result["expense"]]
    )
    print(f"Report type: {report_result['report']['report_type']}")
    print(f"Total budget: ${report_result['report']['total_budget']:.2f}")
    print(f"Total expenses: ${report_result['report']['total_expenses']:.2f}")
    print(f"Remaining budget: ${report_result['report']['remaining_budget']:.2f}")
    
    # Test FinancialPlanGenerationTool
    print("\nTesting FinancialPlanGenerationTool:")
    plan_tool = FinancialPlanGenerationTool()
    plan_result = plan_tool._run(
        event_id="test-event-123",
        event_details=state["event_details"],
        budget=budget_result["budget"],
        expenses=[expense_result["expense"]],
        contracts=[contract_result["contract"]]
    )
    print(f"Financial plan generated with {len(plan_result['financial_plan']['payment_schedule'])} payment milestones")
    print(f"Contingency fund: ${plan_result['contingency_fund']:.2f}")
    print(f"Total cost: ${plan_result['total_cost']:.2f}")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_financial_agent())
