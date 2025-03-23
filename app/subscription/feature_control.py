"""
Subscription feature control for agent capabilities.

This module provides functionality to check if an organization has access
to specific agent features based on their subscription plan.
"""

from typing import Dict, Any, List, Optional
import json
from sqlalchemy.orm import Session

from app.db.models_saas import Organization, SubscriptionPlan


class FeatureNotAvailableError(Exception):
    """Exception raised when a feature is not available for the current subscription plan."""
    pass


class SubscriptionFeatureControl:
    """
    Subscription feature control for agent capabilities.
    
    This class provides functionality to check if an organization has access
    to specific agent features based on their subscription plan.
    """
    
    # Agent tiers configuration
    AGENT_TIERS = {
        "free": ["coordinator", "resource_planning"],
        "professional": [
            "coordinator", "resource_planning", "financial", 
            "stakeholder_management", "marketing_communications", 
            "project_management"
        ],
        "enterprise": [
            "coordinator", "resource_planning", "financial", 
            "stakeholder_management", "marketing_communications", 
            "project_management", "analytics", "compliance_security"
        ]
    }
    
    # Feature tiers configuration
    FEATURE_TIERS = {
        "free": {
            "max_events": 5,
            "max_users": 2,
            "advanced_recommendations": False,
            "custom_templates": False,
            "priority_support": False,
            "analytics_dashboard": False
        },
        "professional": {
            "max_events": 20,
            "max_users": 10,
            "advanced_recommendations": True,
            "custom_templates": True,
            "priority_support": False,
            "analytics_dashboard": True
        },
        "enterprise": {
            "max_events": -1,  # Unlimited
            "max_users": -1,   # Unlimited
            "advanced_recommendations": True,
            "custom_templates": True,
            "priority_support": True,
            "analytics_dashboard": True
        }
    }
    
    def __init__(self, db: Session, organization_id: Optional[int] = None):
        """
        Initialize the subscription feature control.
        
        Args:
            db: Database session
            organization_id: The organization ID
        """
        self.db = db
        self.organization_id = organization_id
        self._organization = None
        self._subscription_plan = None
        self._features = None
    
    @property
    def organization(self) -> Optional[Organization]:
        """Get the organization."""
        if self._organization is None and self.organization_id:
            self._organization = self.db.query(Organization).filter(
                Organization.id == self.organization_id
            ).first()
        return self._organization
    
    @property
    def subscription_plan(self) -> Optional[SubscriptionPlan]:
        """Get the subscription plan."""
        if self._subscription_plan is None and self.organization:
            self._subscription_plan = self.db.query(SubscriptionPlan).filter(
                SubscriptionPlan.stripe_price_id == self.organization.plan_id
            ).first()
        return self._subscription_plan
    
    @property
    def features(self) -> Dict[str, Any]:
        """Get the features for the current subscription plan."""
        if self._features is None:
            if self.organization and self.organization.features:
                try:
                    self._features = json.loads(self.organization.features)
                except (json.JSONDecodeError, TypeError):
                    self._features = {}
            else:
                self._features = {}
        return self._features
    
    @property
    def plan_tier(self) -> str:
        """Get the plan tier for the current subscription."""
        if not self.subscription_plan:
            return "free"
        
        plan_name = self.subscription_plan.name.lower()
        if "enterprise" in plan_name:
            return "enterprise"
        elif "professional" in plan_name or "premium" in plan_name:
            return "professional"
        else:
            return "free"
    
    def can_access_agent(self, agent_type: str) -> bool:
        """
        Check if the organization can access a specific agent type.
        
        Args:
            agent_type: The agent type to check
            
        Returns:
            True if the organization can access the agent, False otherwise
        """
        if not self.organization_id:
            # Default to coordinator only if no organization context
            return agent_type == "coordinator"
        
        # Check subscription status
        if self.organization and self.organization.subscription_status != "active":
            # Only allow coordinator for inactive subscriptions
            return agent_type == "coordinator"
        
        # Get available agents for the current plan tier
        available_agents = self.AGENT_TIERS.get(self.plan_tier, [])
        
        return agent_type in available_agents
    
    def can_access_feature(self, feature_name: str) -> bool:
        """
        Check if the organization can access a specific feature.
        
        Args:
            feature_name: The feature name to check
            
        Returns:
            True if the organization can access the feature, False otherwise
        """
        if not self.organization_id:
            # Default to basic features only if no organization context
            return feature_name in self.FEATURE_TIERS["free"]
        
        # Check subscription status
        if self.organization and self.organization.subscription_status != "active":
            # Only allow basic features for inactive subscriptions
            return feature_name in self.FEATURE_TIERS["free"] and self.FEATURE_TIERS["free"].get(feature_name, False)
        
        # Get available features for the current plan tier
        available_features = self.FEATURE_TIERS.get(self.plan_tier, {})
        
        # Check if the feature exists and is enabled
        return feature_name in available_features and available_features.get(feature_name, False)
    
    def check_usage_limits(self, resource_type: str, current_count: int) -> bool:
        """
        Check if the organization is within usage limits for a specific resource.
        
        Args:
            resource_type: The resource type to check (e.g., "events", "users")
            current_count: The current count of the resource
            
        Returns:
            True if the organization is within limits, False otherwise
        """
        if not self.organization_id:
            # Default to free tier limits if no organization context
            max_limit = self.FEATURE_TIERS["free"].get(f"max_{resource_type}", 0)
            return current_count <= max_limit
        
        # Check subscription status
        if self.organization and self.organization.subscription_status != "active":
            # Use free tier limits for inactive subscriptions
            max_limit = self.FEATURE_TIERS["free"].get(f"max_{resource_type}", 0)
            return current_count <= max_limit
        
        # Get the limit from the organization or plan tier
        if resource_type == "users" and self.organization:
            max_limit = self.organization.max_users
        elif resource_type == "events" and self.organization:
            max_limit = self.organization.max_events
        else:
            # Get from plan tier
            max_limit = self.FEATURE_TIERS.get(self.plan_tier, {}).get(f"max_{resource_type}", 0)
        
        # -1 means unlimited
        if max_limit == -1:
            return True
        
        return current_count <= max_limit
    
    def require_agent_access(self, agent_type: str) -> None:
        """
        Require access to a specific agent type, raising an exception if not available.
        
        Args:
            agent_type: The agent type to check
            
        Raises:
            FeatureNotAvailableError: If the agent is not available for the current subscription
        """
        if not self.can_access_agent(agent_type):
            plan_name = self.subscription_plan.name if self.subscription_plan else "Free"
            raise FeatureNotAvailableError(
                f"The {agent_type} agent is not available on your current {plan_name} plan. "
                f"Please upgrade to access this feature."
            )
    
    def require_feature_access(self, feature_name: str) -> None:
        """
        Require access to a specific feature, raising an exception if not available.
        
        Args:
            feature_name: The feature name to check
            
        Raises:
            FeatureNotAvailableError: If the feature is not available for the current subscription
        """
        if not self.can_access_feature(feature_name):
            plan_name = self.subscription_plan.name if self.subscription_plan else "Free"
            raise FeatureNotAvailableError(
                f"The {feature_name} feature is not available on your current {plan_name} plan. "
                f"Please upgrade to access this feature."
            )
    
    def require_within_limits(self, resource_type: str, current_count: int) -> None:
        """
        Require the organization to be within usage limits, raising an exception if not.
        
        Args:
            resource_type: The resource type to check (e.g., "events", "users")
            current_count: The current count of the resource
            
        Raises:
            FeatureNotAvailableError: If the organization is not within limits
        """
        if not self.check_usage_limits(resource_type, current_count):
            plan_name = self.subscription_plan.name if self.subscription_plan else "Free"
            
            # Get the limit
            if resource_type == "users" and self.organization:
                max_limit = self.organization.max_users
            elif resource_type == "events" and self.organization:
                max_limit = self.organization.max_events
            else:
                max_limit = self.FEATURE_TIERS.get(self.plan_tier, {}).get(f"max_{resource_type}", 0)
            
            raise FeatureNotAvailableError(
                f"You have reached the maximum number of {resource_type} ({max_limit}) "
                f"allowed on your current {plan_name} plan. Please upgrade to add more {resource_type}."
            )


def get_feature_control(db: Session, organization_id: Optional[int] = None) -> SubscriptionFeatureControl:
    """
    Get a subscription feature control instance.
    
    Args:
        db: Database session
        organization_id: The organization ID
        
    Returns:
        SubscriptionFeatureControl instance
    """
    return SubscriptionFeatureControl(db=db, organization_id=organization_id)
