from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Table, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Organization(Base):
    """
    Organization/Tenant model for multi-tenancy.
    """
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    plan_id = Column(String(50), nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    subscription_status = Column(String(50), default="inactive")
    max_users = Column(Integer, default=5)
    max_events = Column(Integer, default=10)
    features = Column(Text, default='{"basic": true, "advanced": false, "premium": false}')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("OrganizationUser", back_populates="organization")
    events = relationship("Event", back_populates="organization")
    conversations = relationship("Conversation", back_populates="organization")


class OrganizationUser(Base):
    """
    Association table for users and organizations with role information.
    """
    __tablename__ = "organization_users"
    
    organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String(50), nullable=False)  # admin, manager, user
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    user = relationship("User", back_populates="organizations")


class SubscriptionPlan(Base):
    """
    Subscription plan model.
    """
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    stripe_price_id = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Price in cents
    interval = Column(String(20), default="month")  # month, year
    max_users = Column(Integer, default=5)
    max_events = Column(Integer, default=10)
    features = Column(Text, default='{"basic": true, "advanced": false, "premium": false}')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SubscriptionInvoice(Base):
    """
    Subscription invoice model.
    """
    __tablename__ = "subscription_invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    stripe_invoice_id = Column(String(255), nullable=True)
    amount = Column(Integer, nullable=False)  # Amount in cents
    status = Column(String(50), default="pending")  # pending, paid, failed
    invoice_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    paid_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization")
