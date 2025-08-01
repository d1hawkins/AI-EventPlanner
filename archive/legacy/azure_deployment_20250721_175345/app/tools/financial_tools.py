from typing import Dict, Any, List, Optional, Type
from datetime import datetime, timedelta
import uuid
import json

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.schemas.financial import Budget, BudgetCategory, Expense, Contract, Payment, FinancialReport, FinancialPlan


class BudgetAllocationInput(BaseModel):
    """Input schema for the budget allocation tool."""
    
    event_type: str = Field(..., description="Type of event (e.g., conference, wedding, corporate)")
    total_budget: float = Field(..., description="Total budget amount")
    attendee_count: int = Field(..., description="Expected number of attendees")
    duration_days: int = Field(..., description="Duration of the event in days")
    location: Optional[str] = Field(None, description="Event location")
    special_requirements: Optional[List[str]] = Field(None, description="Special requirements for the event")


class BudgetAllocationTool(BaseTool):
    """Tool for allocating budget across different categories."""
    
    name: str = "budget_allocation_tool"
    description: str = "Allocate budget across different event categories"
    args_schema: Type[BudgetAllocationInput] = BudgetAllocationInput
    
    def _run(self, event_type: str, total_budget: float, 
             attendee_count: int, duration_days: int,
             location: Optional[str] = None,
             special_requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the budget allocation tool.
        
        Args:
            event_type: Type of event
            total_budget: Total budget amount
            attendee_count: Expected number of attendees
            duration_days: Duration of the event in days
            location: Event location
            special_requirements: Special requirements for the event
            
        Returns:
            Dictionary with budget allocation
        """
        # In a real implementation, this would use algorithms to determine optimal budget allocation
        # For now, we'll return mock data based on the input parameters
        
        # Default allocation percentages based on event type
        allocation_percentages = {}
        
        if event_type.lower() in ["conference", "corporate", "meeting"]:
            allocation_percentages = {
                "Venue": 0.30,
                "Catering": 0.25,
                "AV Equipment": 0.15,
                "Marketing": 0.10,
                "Speakers": 0.10,
                "Staff": 0.05,
                "Miscellaneous": 0.05
            }
        elif event_type.lower() in ["wedding", "gala", "social"]:
            allocation_percentages = {
                "Venue": 0.40,
                "Catering": 0.30,
                "Decoration": 0.10,
                "Entertainment": 0.10,
                "Photography": 0.05,
                "Miscellaneous": 0.05
            }
        else:
            # Generic allocation for other event types
            allocation_percentages = {
                "Venue": 0.35,
                "Catering": 0.25,
                "Equipment": 0.15,
                "Marketing": 0.10,
                "Staff": 0.10,
                "Miscellaneous": 0.05
            }
        
        # Adjust percentages based on attendee count
        if attendee_count > 500:
            # For large events, increase venue and catering percentages
            allocation_percentages["Venue"] += 0.05
            allocation_percentages["Catering"] += 0.05
            # Decrease other categories to maintain total of 1.0
            for category in allocation_percentages:
                if category not in ["Venue", "Catering"]:
                    allocation_percentages[category] -= 0.02
        
        # Adjust percentages based on duration
        if duration_days > 3:
            # For longer events, increase staff and miscellaneous percentages
            allocation_percentages["Staff"] = allocation_percentages.get("Staff", 0) + 0.05
            allocation_percentages["Miscellaneous"] = allocation_percentages.get("Miscellaneous", 0) + 0.05
            # Decrease other categories to maintain total of 1.0
            for category in allocation_percentages:
                if category not in ["Staff", "Miscellaneous"]:
                    allocation_percentages[category] -= 0.02
        
        # Adjust for special requirements
        if special_requirements:
            for req in special_requirements:
                req_lower = req.lower()
                if "luxury" in req_lower or "premium" in req_lower:
                    # Increase venue and catering for luxury events
                    allocation_percentages["Venue"] += 0.05
                    allocation_percentages["Catering"] += 0.05
                    # Decrease other categories
                    for category in allocation_percentages:
                        if category not in ["Venue", "Catering"]:
                            allocation_percentages[category] -= 0.02
                elif "technology" in req_lower or "tech" in req_lower:
                    # Increase AV Equipment for tech-focused events
                    av_category = "AV Equipment" if "AV Equipment" in allocation_percentages else "Equipment"
                    allocation_percentages[av_category] += 0.10
                    # Decrease other categories
                    for category in allocation_percentages:
                        if category != av_category:
                            allocation_percentages[category] -= 0.02
        
        # Normalize percentages to ensure they sum to 1.0
        total_percentage = sum(allocation_percentages.values())
        for category in allocation_percentages:
            allocation_percentages[category] /= total_percentage
        
        # Calculate actual amounts based on percentages
        budget_categories = []
        for category, percentage in allocation_percentages.items():
            amount = round(total_budget * percentage, 2)
            budget_categories.append({
                "name": category,
                "amount": amount,
                "description": f"Budget for {category.lower()}",
                "subcategories": []
            })
        
        # Add subcategories for some main categories
        for category in budget_categories:
            if category["name"] == "Venue":
                category["subcategories"] = [
                    {"name": "Rental Fee", "amount": round(category["amount"] * 0.8, 2)},
                    {"name": "Setup/Cleanup", "amount": round(category["amount"] * 0.1, 2)},
                    {"name": "Insurance", "amount": round(category["amount"] * 0.1, 2)}
                ]
            elif category["name"] == "Catering":
                category["subcategories"] = [
                    {"name": "Food", "amount": round(category["amount"] * 0.7, 2)},
                    {"name": "Beverages", "amount": round(category["amount"] * 0.2, 2)},
                    {"name": "Service Staff", "amount": round(category["amount"] * 0.1, 2)}
                ]
            elif category["name"] in ["AV Equipment", "Equipment"]:
                category["subcategories"] = [
                    {"name": "Rental", "amount": round(category["amount"] * 0.6, 2)},
                    {"name": "Setup/Operation", "amount": round(category["amount"] * 0.3, 2)},
                    {"name": "Contingency", "amount": round(category["amount"] * 0.1, 2)}
                ]
        
        # Create a Budget object
        budget = Budget(
            total_amount=total_budget,
            categories=[BudgetCategory(**category) for category in budget_categories],
            currency="USD",
            notes=f"Budget for {event_type} event with {attendee_count} attendees over {duration_days} days"
        )
        
        # Add a contingency fund (5% of total budget)
        contingency_fund = round(total_budget * 0.05, 2)
        
        return {
            "budget": budget.dict(),
            "allocation_percentages": allocation_percentages,
            "contingency_fund": contingency_fund,
            "allocation_criteria": {
                "event_type": event_type,
                "total_budget": total_budget,
                "attendee_count": attendee_count,
                "duration_days": duration_days,
                "location": location,
                "special_requirements": special_requirements
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class PaymentTrackingInput(BaseModel):
    """Input schema for the payment tracking tool."""
    
    expense_type: str = Field(..., description="Type of expense (e.g., venue, catering, equipment)")
    amount: float = Field(..., description="Expense amount")
    vendor: str = Field(..., description="Vendor or payee")
    description: str = Field(..., description="Description of the expense")
    due_date: str = Field(..., description="Due date for the payment (YYYY-MM-DD)")
    payment_status: str = Field("pending", description="Payment status (pending, paid, cancelled)")
    payment_method: Optional[str] = Field(None, description="Payment method")


class PaymentTrackingTool(BaseTool):
    """Tool for tracking payments and expenses."""
    
    name: str = "payment_tracking_tool"
    description: str = "Track payments and expenses for the event"
    args_schema: Type[PaymentTrackingInput] = PaymentTrackingInput
    
    def _run(self, expense_type: str, amount: float, 
             vendor: str, description: str, due_date: str,
             payment_status: str = "pending",
             payment_method: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the payment tracking tool.
        
        Args:
            expense_type: Type of expense
            amount: Expense amount
            vendor: Vendor or payee
            description: Description of the expense
            due_date: Due date for the payment
            payment_status: Payment status
            payment_method: Payment method
            
        Returns:
            Dictionary with expense and payment details
        """
        # In a real implementation, this would store the expense and payment in a database
        # For now, we'll return mock data
        
        # Generate a unique ID for the expense
        expense_id = str(uuid.uuid4())
        
        # Parse the due date
        try:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            # If date parsing fails, use current date + 30 days
            due_date_obj = datetime.now() + timedelta(days=30)
        
        # Create an Expense object
        expense = Expense(
            category=expense_type,
            amount=amount,
            vendor=vendor,
            description=description,
            date=due_date_obj,
            payment_status=payment_status,
            payment_method=payment_method
        )
        
        # Create a Payment object if the expense is paid
        payment = None
        if payment_status.lower() == "paid":
            payment = Payment(
                expense_id=expense_id,
                amount=amount,
                date=datetime.now(),
                method=payment_method or "Unknown",
                status="completed",
                transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
                notes=f"Payment for {description}"
            )
        
        return {
            "expense_id": expense_id,
            "expense": expense.dict(),
            "payment": payment.dict() if payment else None,
            "tracking_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "tracked"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class ContractGenerationInput(BaseModel):
    """Input schema for the contract generation tool."""
    
    vendor_name: str = Field(..., description="Name of the vendor or service provider")
    service_type: str = Field(..., description="Type of service provided")
    amount: float = Field(..., description="Contract amount")
    start_date: str = Field(..., description="Contract start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Contract end date (YYYY-MM-DD)")
    terms: Optional[List[str]] = Field(None, description="Contract terms and conditions")


class ContractGenerationTool(BaseTool):
    """Tool for generating contracts for vendors and service providers."""
    
    name: str = "contract_generation_tool"
    description: str = "Generate contracts for vendors and service providers"
    args_schema: Type[ContractGenerationInput] = ContractGenerationInput
    
    def _run(self, vendor_name: str, service_type: str,
             amount: float, start_date: str, end_date: str,
             terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the contract generation tool.
        
        Args:
            vendor_name: Name of the vendor or service provider
            service_type: Type of service provided
            amount: Contract amount
            start_date: Contract start date
            end_date: Contract end date
            terms: Contract terms and conditions
            
        Returns:
            Dictionary with contract details
        """
        # In a real implementation, this would generate a contract document
        # For now, we'll return mock data
        
        # Parse the dates
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            # If date parsing fails, use current date and current date + 30 days
            start_date_obj = datetime.now()
            end_date_obj = datetime.now() + timedelta(days=30)
        
        # Default terms if none provided
        if not terms:
            terms = [
                "Payment due within 30 days of invoice",
                "Cancellation requires 14 days notice",
                "Vendor must provide proof of insurance",
                "All deliverables must meet agreed specifications",
                "Any disputes will be resolved through arbitration"
            ]
        
        # Add service-specific terms
        if service_type.lower() == "catering":
            terms.extend([
                "Final headcount must be provided 7 days before event",
                "Dietary restrictions must be communicated in advance",
                "Vendor responsible for cleanup after service"
            ])
        elif service_type.lower() in ["av", "audio visual", "equipment"]:
            terms.extend([
                "Equipment must be set up and tested 2 hours before event",
                "Technician must be available throughout the event",
                "Backup equipment must be available on-site"
            ])
        elif service_type.lower() == "venue":
            terms.extend([
                "Access to venue provided 4 hours before event for setup",
                "All decorations must be removed after event",
                "Noise restrictions apply after 10:00 PM"
            ])
        
        # Generate a contract ID
        contract_id = f"CTR-{uuid.uuid4().hex[:8].upper()}"
        
        # Create a Contract object
        contract = Contract(
            vendor_name=vendor_name,
            service_type=service_type,
            amount=amount,
            start_date=start_date_obj,
            end_date=end_date_obj,
            status="draft",
            terms=terms
        )
        
        # Generate a mock contract text
        contract_text = f"""
SERVICE CONTRACT

Contract ID: {contract_id}
Date: {datetime.now().strftime("%Y-%m-%d")}

BETWEEN:
Client: Event Organizer
AND
Vendor: {vendor_name}

SERVICE DETAILS:
Service Type: {service_type}
Contract Amount: ${amount:.2f}
Service Period: {start_date} to {end_date}

TERMS AND CONDITIONS:
{chr(10).join([f"- {term}" for term in terms])}

SIGNATURES:

________________________                    ________________________
Client Signature                            Vendor Signature

________________________                    ________________________
Date                                        Date
"""
        
        return {
            "contract_id": contract_id,
            "contract": contract.dict(),
            "contract_text": contract_text,
            "generation_details": {
                "created_at": datetime.now().isoformat(),
                "status": "draft",
                "next_steps": "Review contract and send to vendor for signature"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class FinancialReportingInput(BaseModel):
    """Input schema for the financial reporting tool."""
    
    report_type: str = Field(..., description="Type of financial report (e.g., budget, expenses, summary)")
    start_date: Optional[str] = Field(None, description="Report start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Report end date (YYYY-MM-DD)")
    budget: Optional[Dict[str, Any]] = Field(None, description="Budget information")
    expenses: Optional[List[Dict[str, Any]]] = Field(None, description="Expense information")


class FinancialReportingTool(BaseTool):
    """Tool for generating financial reports."""
    
    name: str = "financial_reporting_tool"
    description: str = "Generate financial reports for the event"
    args_schema: Type[FinancialReportingInput] = FinancialReportingInput
    
    def _run(self, report_type: str, 
             start_date: Optional[str] = None,
             end_date: Optional[str] = None,
             budget: Optional[Dict[str, Any]] = None,
             expenses: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Run the financial reporting tool.
        
        Args:
            report_type: Type of financial report
            start_date: Report start date
            end_date: Report end date
            budget: Budget information
            expenses: Expense information
            
        Returns:
            Dictionary with financial report
        """
        # In a real implementation, this would generate a report based on actual data
        # For now, we'll return mock data
        
        # Parse the dates
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now() - timedelta(days=30)
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
        except ValueError:
            # If date parsing fails, use default dates
            start_date_obj = datetime.now() - timedelta(days=30)
            end_date_obj = datetime.now()
        
        # Create mock budget if not provided
        if not budget:
            budget = {
                "total_amount": 50000.0,
                "categories": [
                    {"name": "Venue", "amount": 15000.0},
                    {"name": "Catering", "amount": 12500.0},
                    {"name": "AV Equipment", "amount": 7500.0},
                    {"name": "Marketing", "amount": 5000.0},
                    {"name": "Speakers", "amount": 5000.0},
                    {"name": "Staff", "amount": 2500.0},
                    {"name": "Miscellaneous", "amount": 2500.0}
                ]
            }
        
        # Create mock expenses if not provided
        if not expenses:
            expenses = [
                {
                    "category": "Venue",
                    "amount": 15000.0,
                    "vendor": "Convention Center",
                    "description": "Venue rental for main event",
                    "date": (end_date_obj - timedelta(days=15)).isoformat(),
                    "payment_status": "paid"
                },
                {
                    "category": "Catering",
                    "amount": 10000.0,
                    "vendor": "Gourmet Catering",
                    "description": "Food and beverages for attendees",
                    "date": (end_date_obj - timedelta(days=10)).isoformat(),
                    "payment_status": "paid"
                },
                {
                    "category": "AV Equipment",
                    "amount": 7000.0,
                    "vendor": "Tech Solutions",
                    "description": "Audio-visual equipment rental",
                    "date": (end_date_obj - timedelta(days=5)).isoformat(),
                    "payment_status": "paid"
                },
                {
                    "category": "Marketing",
                    "amount": 4500.0,
                    "vendor": "Marketing Agency",
                    "description": "Digital marketing campaign",
                    "date": (end_date_obj - timedelta(days=20)).isoformat(),
                    "payment_status": "paid"
                },
                {
                    "category": "Speakers",
                    "amount": 4000.0,
                    "vendor": "Speaker Bureau",
                    "description": "Speaker fees and travel",
                    "date": (end_date_obj - timedelta(days=2)).isoformat(),
                    "payment_status": "pending"
                }
            ]
        
        # Calculate total expenses
        total_expenses = sum(expense["amount"] for expense in expenses)
        
        # Calculate expenses by category
        expenses_by_category = {}
        for expense in expenses:
            category = expense["category"]
            amount = expense["amount"]
            if category in expenses_by_category:
                expenses_by_category[category] += amount
            else:
                expenses_by_category[category] = amount
        
        # Calculate remaining budget
        total_budget = budget["total_amount"]
        remaining_budget = total_budget - total_expenses
        
        # Calculate pending payments
        pending_payments = sum(expense["amount"] for expense in expenses if expense["payment_status"] == "pending")
        
        # Create a FinancialReport object
        report = FinancialReport(
            report_type=report_type,
            start_date=start_date_obj,
            end_date=end_date_obj,
            total_budget=total_budget,
            total_expenses=total_expenses,
            remaining_budget=remaining_budget,
            expenses_by_category=expenses_by_category,
            pending_payments=pending_payments,
            generated_at=datetime.now()
        )
        
        # Generate a report summary based on report type
        summary = ""
        if report_type.lower() == "budget":
            summary = f"""
Budget Report ({start_date_obj.strftime("%Y-%m-%d")} to {end_date_obj.strftime("%Y-%m-%d")})

Total Budget: ${total_budget:.2f}
Allocated Budget:
{chr(10).join([f"- {category['name']}: ${category['amount']:.2f}" for category in budget["categories"]])}

Budget Status:
- Total Expenses: ${total_expenses:.2f} ({(total_expenses/total_budget*100):.1f}% of budget)
- Remaining Budget: ${remaining_budget:.2f} ({(remaining_budget/total_budget*100):.1f}% of budget)
- Pending Payments: ${pending_payments:.2f}
"""
        elif report_type.lower() == "expenses":
            summary = f"""
Expense Report ({start_date_obj.strftime("%Y-%m-%d")} to {end_date_obj.strftime("%Y-%m-%d")})

Total Expenses: ${total_expenses:.2f}

Expenses by Category:
{chr(10).join([f"- {category}: ${amount:.2f} ({(amount/total_expenses*100):.1f}%)" for category, amount in expenses_by_category.items()])}

Recent Expenses:
{chr(10).join([f"- {expense['date'][:10]}: {expense['description']} - ${expense['amount']:.2f} ({expense['payment_status']})" for expense in sorted(expenses, key=lambda x: x['date'], reverse=True)[:5]])}

Payment Status:
- Paid: ${sum(expense['amount'] for expense in expenses if expense['payment_status'] == 'paid'):.2f}
- Pending: ${pending_payments:.2f}
"""
        else:  # summary report
            summary = f"""
Financial Summary ({start_date_obj.strftime("%Y-%m-%d")} to {end_date_obj.strftime("%Y-%m-%d")})

Budget Overview:
- Total Budget: ${total_budget:.2f}
- Total Expenses: ${total_expenses:.2f} ({(total_expenses/total_budget*100):.1f}% of budget)
- Remaining Budget: ${remaining_budget:.2f} ({(remaining_budget/total_budget*100):.1f}% of budget)

Top Expense Categories:
{chr(10).join([f"- {category}: ${amount:.2f} ({(amount/total_expenses*100):.1f}%)" for category, amount in sorted(expenses_by_category.items(), key=lambda x: x[1], reverse=True)[:3]])}

Financial Status:
- Pending Payments: ${pending_payments:.2f}
- Budget Variance: ${total_budget - total_expenses:.2f} ({((total_budget - total_expenses)/total_budget*100):.1f}%)

Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        return {
            "report": report.dict(),
            "summary": summary,
            "charts": {
                "budget_vs_expenses": {
                    "type": "pie",
                    "data": {
                        "labels": ["Expenses", "Remaining"],
                        "values": [total_expenses, remaining_budget]
                    }
                },
                "expenses_by_category": {
                    "type": "bar",
                    "data": {
                        "labels": list(expenses_by_category.keys()),
                        "values": list(expenses_by_category.values())
                    }
                }
            },
            "reporting_details": {
                "generated_at": datetime.now().isoformat(),
                "report_period": f"{start_date_obj.strftime('%Y-%m-%d')} to {end_date_obj.strftime('%Y-%m-%d')}",
                "report_type": report_type
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class FinancialPlanGenerationInput(BaseModel):
    """Input schema for the financial plan generation tool."""
    
    event_id: str = Field(..., description="ID of the event")
    event_details: Dict[str, Any] = Field(..., description="Event details")
    budget: Dict[str, Any] = Field(..., description="Budget information")
    expenses: Optional[List[Dict[str, Any]]] = Field(None, description="Expense information")
    contracts: Optional[List[Dict[str, Any]]] = Field(None, description="Contract information")


class FinancialPlanGenerationTool(BaseTool):
    """Tool for generating a comprehensive financial plan."""
    
    name: str = "financial_plan_generation_tool"
    description: str = "Generate a comprehensive financial plan for an event"
    args_schema: Type[FinancialPlanGenerationInput] = FinancialPlanGenerationInput
    
    def _run(self, event_id: str, event_details: Dict[str, Any],
             budget: Dict[str, Any],
             expenses: Optional[List[Dict[str, Any]]] = None,
             contracts: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Run the financial plan generation tool.
        
        Args:
            event_id: ID of the event
            event_details: Event details
            budget: Budget information
            expenses: Expense information
            contracts: Contract information
            
        Returns:
            Dictionary with financial plan
        """
        # In a real implementation, this would generate an optimized financial plan
        # For now, we'll create a structured plan based on the input parameters
        
        # Create a Budget object
        budget_obj = Budget(**budget)
        
        # Create a payment schedule based on the budget
        payment_schedule = []
        
        # Get event start date
        event_start = None
        if "timeline_start" in event_details and event_details["timeline_start"]:
            try:
                event_start = datetime.strptime(event_details["timeline_start"], "%Y-%m-%d")
            except ValueError:
                event_start = datetime.now() + timedelta(days=90)
        else:
            event_start = datetime.now() + timedelta(days=90)
        
        # Create payment milestones
        milestones = [
            {"name": "Initial Deposit", "percentage": 0.25, "days_before": 90},
            {"name": "Second Payment", "percentage": 0.25, "days_before": 60},
            {"name": "Third Payment", "percentage": 0.25, "days_before": 30},
            {"name": "Final Payment", "percentage": 0.25, "days_before": 7}
        ]
        
        # Generate payment schedule
        for milestone in milestones:
            payment_date = event_start - timedelta(days=milestone["days_before"])
            payment_schedule.append({
                "name": milestone["name"],
                "amount": round(budget_obj.total_amount * milestone["percentage"], 2),
                "due_date": payment_date.strftime("%Y-%m-%d"),
                "status": "pending"
            })
        
        # Define financial risks and mitigation strategies
        financial_risks = [
            {
                "risk": "Budget overrun",
                "impact": "high",
                "probability": "medium",
                "mitigation": "Maintain a contingency fund of 10% of the total budget"
            },
            {
                "risk": "Vendor price increases",
                "impact": "medium",
                "probability": "medium",
                "mitigation": "Lock in prices with contracts and include price guarantee clauses"
            },
            {
                "risk": "Unexpected expenses",
                "impact": "medium",
                "probability": "high",
                "mitigation": "Regular budget reviews and approval process for any unplanned expenses"
            },
            {
                "risk": "Low attendance/revenue",
                "impact": "high",
                "probability": "low",
                "mitigation": "Conservative revenue projections and early bird ticket sales"
            },
            {
                "risk": "Currency fluctuations",
                "impact": "low",
                "probability": "low",
                "mitigation": "Use fixed exchange rates in contracts with international vendors"
            }
        ]
        
        # Calculate contingency fund (10% of total budget)
        contingency_fund = round(budget_obj.total_amount * 0.10, 2)
        
        # Create a FinancialPlan object
        financial_plan = FinancialPlan(
            event_id=event_id,
            budget=budget_obj,
            payment_schedule=payment_schedule,
            financial_risks=financial_risks,
            contingency_fund=contingency_fund,
            approval_status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Generate a financial plan summary
        summary = f"""
Financial Plan for {event_details.get('title', 'Event')}

Budget Summary:
- Total Budget: ${budget_obj.total_amount:.2f}
- Contingency Fund: ${contingency_fund:.2f} (10% of total budget)

Budget Allocation:
{chr(10).join([f"- {category.name}: ${category.amount:.2f} ({category.amount/budget_obj.total_amount*100:.1f}%)" for category in budget_obj.categories])}

Payment Schedule:
{chr(10).join([f"- {payment['name']}: ${payment['amount']:.2f} (Due: {payment['due_date']})" for payment in payment_schedule])}

Financial Risks:
{chr(10).join([f"- {risk['risk']} (Impact: {risk['impact']}, Probability: {risk['probability']})" for risk in financial_risks])}

This financial plan was generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        return {
            "financial_plan": financial_plan.dict(),
            "summary": summary,
            "payment_schedule": payment_schedule,
            "financial_risks": financial_risks,
            "contingency_fund": contingency_fund,
            "generation_details": {
                "created_at": datetime.now().isoformat(),
                "status": "draft",
                "next_steps": "Review financial plan and submit for approval"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)
