import json
import os
import stripe
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models_updated import User, Organization, OrganizationUser, SubscriptionPlan, SubscriptionInvoice
from app.auth.dependencies import get_current_user
from app.middleware.tenant import get_tenant_id, require_tenant
from app.subscription.schemas import (
    OrganizationCreate, 
    OrganizationResponse, 
    OrganizationUserCreate,
    OrganizationUserResponse,
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionPlanResponse
)

router = APIRouter()

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY", "")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")


# Add a custom response model for Organization that uses features_dict
class OrganizationResponseWithFeatures(OrganizationResponse):
    """Organization response with features as a dictionary."""
    
    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to response model."""
        # Create a copy of the object to avoid modifying the original
        obj_dict = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        # Replace features with features_dict
        obj_dict["features"] = obj.features_dict
        return cls(**obj_dict)


@router.post("/organizations", response_model=OrganizationResponseWithFeatures, status_code=status.HTTP_201_CREATED)
async def create_organization(
    organization_in: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new organization.
    
    Args:
        organization_in: Organization data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created organization
    """
    # Check if slug is already taken
    existing_org = db.query(Organization).filter(Organization.slug == organization_in.slug).first()
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization slug already exists"
        )
    
    # Create organization
    organization = Organization(
        name=organization_in.name,
        slug=organization_in.slug,
        plan_id=organization_in.plan_id,
        max_users=organization_in.max_users,
        max_events=organization_in.max_events,
        features=json.dumps(organization_in.features) if isinstance(organization_in.features, dict) else organization_in.features
    )
    db.add(organization)
    db.flush()
    
    # Add current user as admin
    org_user = OrganizationUser(
        organization_id=organization.id,
        user_id=current_user.id,
        role="admin",
        is_primary=True
    )
    db.add(org_user)
    db.commit()
    db.refresh(organization)
    
    return OrganizationResponseWithFeatures.from_orm(organization)

@router.get("/organizations", response_model=List[OrganizationResponseWithFeatures])
async def list_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List organizations for the current user.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of organizations
    """
    # Get organizations where user is a member
    user_orgs = db.query(OrganizationUser).filter(OrganizationUser.user_id == current_user.id).all()
    org_ids = [org_user.organization_id for org_user in user_orgs]
    
    organizations = db.query(Organization).filter(Organization.id.in_(org_ids)).all()
    
    return [OrganizationResponseWithFeatures.from_orm(org) for org in organizations]


@router.get("/organizations/{organization_id}", response_model=OrganizationResponseWithFeatures)
async def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get organization by ID.
    
    Args:
        organization_id: Organization ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Organization
    """
    # Check if user is a member of the organization
    org_user = db.query(OrganizationUser).filter(
        OrganizationUser.organization_id == organization_id,
        OrganizationUser.user_id == current_user.id
    ).first()
    
    if not org_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return OrganizationResponseWithFeatures.from_orm(organization)


@router.post("/organizations/{organization_id}/users", response_model=OrganizationUserResponse)
async def add_organization_user(
    organization_id: int,
    user_in: OrganizationUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a user to an organization.
    
    Args:
        organization_id: Organization ID
        user_in: User data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created organization user
    """
    # Check if current user is an admin of the organization
    org_user = db.query(OrganizationUser).filter(
        OrganizationUser.organization_id == organization_id,
        OrganizationUser.user_id == current_user.id,
        OrganizationUser.role == "admin"
    ).first()
    
    if not org_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization admins can add users"
        )
    
    # Check if organization exists
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check if user exists
    user = db.query(User).filter(User.email == user_in.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is already a member
    existing_org_user = db.query(OrganizationUser).filter(
        OrganizationUser.organization_id == organization_id,
        OrganizationUser.user_id == user.id
    ).first()
    
    if existing_org_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this organization"
        )
    
    # Check if organization has reached max users
    user_count = db.query(OrganizationUser).filter(
        OrganizationUser.organization_id == organization_id
    ).count()
    
    if user_count >= organization.max_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization has reached maximum number of users"
        )
    
    # Add user to organization
    new_org_user = OrganizationUser(
        organization_id=organization_id,
        user_id=user.id,
        role=user_in.role,
        is_primary=False
    )
    db.add(new_org_user)
    db.commit()
    db.refresh(new_org_user)
    
    return {
        "organization_id": new_org_user.organization_id,
        "user_id": new_org_user.user_id,
        "email": user.email,
        "role": new_org_user.role,
        "is_primary": new_org_user.is_primary
    }


@router.get("/subscription-plans", response_model=List[SubscriptionPlanResponse])
async def list_subscription_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List available subscription plans.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of subscription plans
    """
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    
    return plans


@router.post("/organizations/{organization_id}/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    organization_id: int,
    subscription_in: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a subscription for an organization.
    
    Args:
        organization_id: Organization ID
        subscription_in: Subscription data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Subscription details
    """
    # Check if current user is an admin of the organization
    org_user = db.query(OrganizationUser).filter(
        OrganizationUser.organization_id == organization_id,
        OrganizationUser.user_id == current_user.id,
        OrganizationUser.role == "admin"
    ).first()
    
    if not org_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization admins can manage subscriptions"
        )
    
    # Check if organization exists
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check if plan exists
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == subscription_in.plan_id,
        SubscriptionPlan.is_active == True
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    try:
        # Create or get Stripe customer
        if not organization.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=organization.name,
                metadata={"organization_id": organization.id}
            )
            organization.stripe_customer_id = customer.id
            db.commit()
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=organization.stripe_customer_id,
            items=[{"price": plan.stripe_price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"]
        )
        
        # Update organization
        organization.stripe_subscription_id = subscription.id
        organization.subscription_status = subscription.status
        organization.plan_id = str(plan.id)
        organization.max_users = plan.max_users
        organization.max_events = plan.max_events
        organization.features = json.dumps(plan.features) if isinstance(plan.features, dict) else plan.features
        db.commit()
        
        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
            "client_secret": subscription.latest_invoice.payment_intent.client_secret
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )


@router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    
    Args:
        request: FastAPI request
        db: Database session
        
    Returns:
        Success message
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle subscription events
    if event.type == "customer.subscription.created":
        await handle_subscription_created(event.data.object, db)
    elif event.type == "customer.subscription.updated":
        await handle_subscription_updated(event.data.object, db)
    elif event.type == "customer.subscription.deleted":
        await handle_subscription_deleted(event.data.object, db)
    elif event.type == "invoice.payment_succeeded":
        await handle_invoice_payment_succeeded(event.data.object, db)
    elif event.type == "invoice.payment_failed":
        await handle_invoice_payment_failed(event.data.object, db)
    
    return {"status": "success"}


async def handle_subscription_created(subscription, db: Session):
    """
    Handle subscription created event.
    
    Args:
        subscription: Stripe subscription object
        db: Database session
    """
    customer_id = subscription.customer
    organization = db.query(Organization).filter(
        Organization.stripe_customer_id == customer_id
    ).first()
    
    if organization:
        organization.stripe_subscription_id = subscription.id
        organization.subscription_status = subscription.status
        db.commit()


async def handle_subscription_updated(subscription, db: Session):
    """
    Handle subscription updated event.
    
    Args:
        subscription: Stripe subscription object
        db: Database session
    """
    organization = db.query(Organization).filter(
        Organization.stripe_subscription_id == subscription.id
    ).first()
    
    if organization:
        organization.subscription_status = subscription.status
        db.commit()


async def handle_subscription_deleted(subscription, db: Session):
    """
    Handle subscription deleted event.
    
    Args:
        subscription: Stripe subscription object
        db: Database session
    """
    organization = db.query(Organization).filter(
        Organization.stripe_subscription_id == subscription.id
    ).first()
    
    if organization:
        organization.subscription_status = "canceled"
        db.commit()


async def handle_invoice_payment_succeeded(invoice, db: Session):
    """
    Handle invoice payment succeeded event.
    
    Args:
        invoice: Stripe invoice object
        db: Database session
    """
    customer_id = invoice.customer
    organization = db.query(Organization).filter(
        Organization.stripe_customer_id == customer_id
    ).first()
    
    if organization:
        # Create invoice record
        invoice_record = SubscriptionInvoice(
            organization_id=organization.id,
            stripe_invoice_id=invoice.id,
            amount=invoice.amount_paid,
            status="paid",
            invoice_date=datetime.fromtimestamp(invoice.created),
            paid_date=datetime.fromtimestamp(invoice.status_transitions.paid_at)
        )
        db.add(invoice_record)
        db.commit()


async def handle_invoice_payment_failed(invoice, db: Session):
    """
    Handle invoice payment failed event.
    
    Args:
        invoice: Stripe invoice object
        db: Database session
    """
    customer_id = invoice.customer
    organization = db.query(Organization).filter(
        Organization.stripe_customer_id == customer_id
    ).first()
    
    if organization:
        # Create invoice record
        invoice_record = SubscriptionInvoice(
            organization_id=organization.id,
            stripe_invoice_id=invoice.id,
            amount=invoice.amount_due,
            status="failed",
            invoice_date=datetime.fromtimestamp(invoice.created)
        )
        db.add(invoice_record)
        db.commit()
