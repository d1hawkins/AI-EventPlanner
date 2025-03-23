from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class OrganizationBase(BaseModel):
    """Base schema for organization data."""
    name: str
    slug: str
    plan_id: str = "free"
    max_users: int = 5
    max_events: int = 10
    features: Dict[str, bool] = Field(default_factory=lambda: {"basic": True, "advanced": False, "premium": False})


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""
    pass


class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""
    id: int
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    subscription_status: str = "inactive"
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class OrganizationUserBase(BaseModel):
    """Base schema for organization user data."""
    email: str
    role: str = "user"  # admin, manager, user


class OrganizationUserCreate(OrganizationUserBase):
    """Schema for adding a user to an organization."""
    pass


class OrganizationUserResponse(BaseModel):
    """Schema for organization user response."""
    organization_id: int
    user_id: int
    email: str
    role: str
    is_primary: bool

    class Config:
        orm_mode = True


class SubscriptionPlanBase(BaseModel):
    """Base schema for subscription plan data."""
    name: str
    stripe_price_id: Optional[str] = None
    description: Optional[str] = None
    price: int  # Price in cents
    interval: str = "month"  # month, year
    max_users: int = 5
    max_events: int = 10
    features: Dict[str, bool] = Field(default_factory=lambda: {"basic": True, "advanced": False, "premium": False})


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Schema for creating a subscription plan."""
    pass


class SubscriptionPlanResponse(SubscriptionPlanBase):
    """Schema for subscription plan response."""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription."""
    plan_id: int


class SubscriptionResponse(BaseModel):
    """Schema for subscription response."""
    subscription_id: str
    status: str
    current_period_end: datetime
    client_secret: str


class SubscriptionInvoiceBase(BaseModel):
    """Base schema for subscription invoice data."""
    organization_id: int
    stripe_invoice_id: Optional[str] = None
    amount: int  # Amount in cents
    status: str = "pending"  # pending, paid, failed
    invoice_date: datetime
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None


class SubscriptionInvoiceCreate(SubscriptionInvoiceBase):
    """Schema for creating a subscription invoice."""
    pass


class SubscriptionInvoiceResponse(SubscriptionInvoiceBase):
    """Schema for subscription invoice response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
