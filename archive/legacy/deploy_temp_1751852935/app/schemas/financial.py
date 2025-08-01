from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BudgetCategory(BaseModel):
    """Budget category model."""
    
    name: str = Field(..., description="Name of the budget category")
    amount: float = Field(..., description="Amount allocated to this category")
    description: Optional[str] = Field(None, description="Description of this budget category")
    subcategories: Optional[List[Dict[str, Any]]] = Field(None, description="Subcategories within this category")


class Budget(BaseModel):
    """Budget model."""
    
    total_amount: float = Field(..., description="Total budget amount")
    categories: List[BudgetCategory] = Field(..., description="Budget categories")
    currency: str = Field("USD", description="Currency of the budget")
    notes: Optional[str] = Field(None, description="Additional notes about the budget")


class Expense(BaseModel):
    """Expense model."""
    
    category: str = Field(..., description="Expense category")
    amount: float = Field(..., description="Expense amount")
    vendor: str = Field(..., description="Vendor or payee")
    description: str = Field(..., description="Description of the expense")
    date: datetime = Field(..., description="Date of the expense")
    payment_status: str = Field("pending", description="Payment status (pending, paid, cancelled)")
    payment_method: Optional[str] = Field(None, description="Payment method")
    receipt_url: Optional[str] = Field(None, description="URL to receipt or invoice")


class Contract(BaseModel):
    """Contract model."""
    
    vendor_name: str = Field(..., description="Name of the vendor or service provider")
    service_type: str = Field(..., description="Type of service provided")
    amount: float = Field(..., description="Contract amount")
    start_date: datetime = Field(..., description="Contract start date")
    end_date: datetime = Field(..., description="Contract end date")
    status: str = Field("draft", description="Contract status (draft, sent, signed, completed, cancelled)")
    terms: Optional[List[str]] = Field(None, description="Contract terms and conditions")
    file_url: Optional[str] = Field(None, description="URL to contract file")


class Payment(BaseModel):
    """Payment model."""
    
    expense_id: str = Field(..., description="ID of the related expense")
    amount: float = Field(..., description="Payment amount")
    date: datetime = Field(..., description="Payment date")
    method: str = Field(..., description="Payment method")
    status: str = Field("pending", description="Payment status (pending, completed, failed)")
    transaction_id: Optional[str] = Field(None, description="Payment transaction ID")
    notes: Optional[str] = Field(None, description="Additional notes about the payment")


class FinancialReport(BaseModel):
    """Financial report model."""
    
    report_type: str = Field(..., description="Type of financial report")
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    total_budget: float = Field(..., description="Total budget")
    total_expenses: float = Field(..., description="Total expenses")
    remaining_budget: float = Field(..., description="Remaining budget")
    expenses_by_category: Dict[str, float] = Field(..., description="Expenses broken down by category")
    pending_payments: float = Field(..., description="Total pending payments")
    generated_at: datetime = Field(..., description="Report generation timestamp")


class FinancialPlan(BaseModel):
    """Financial plan model."""
    
    event_id: str = Field(..., description="ID of the event")
    budget: Budget = Field(..., description="Event budget")
    payment_schedule: List[Dict[str, Any]] = Field(..., description="Payment schedule")
    financial_risks: List[Dict[str, Any]] = Field(..., description="Financial risks and mitigation strategies")
    contingency_fund: float = Field(..., description="Contingency fund amount")
    approval_status: str = Field("pending", description="Approval status of the financial plan")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
