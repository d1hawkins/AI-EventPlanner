#!/usr/bin/env python3
"""
Script to create subscription plans in the database.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.abspath("."))

# Load environment variables
load_dotenv()

# Import the SubscriptionPlan model
from app.db.models_updated import SubscriptionPlan

def create_subscription_plans():
    """Create subscription plans in the database."""
    print("Creating subscription plans...")
    
    # Get database URL from environment variable
    database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    # Create engine and session
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if plans already exist
        existing_plans = db.query(SubscriptionPlan).all()
        if existing_plans:
            print(f"Subscription plans already exist ({len(existing_plans)} plans).")
            return
        
        # Create subscription plans
        plans = [
            SubscriptionPlan(
                name="Free",
                stripe_price_id="price_free",
                description="Basic plan with limited features",
                price=0,
                interval="month",
                max_users=3,
                max_events=5,
                features={"basic": True, "advanced": False, "premium": False},
                is_active=True
            ),
            SubscriptionPlan(
                name="Professional",
                stripe_price_id="price_professional",
                description="Professional plan with advanced features",
                price=2999,  # $29.99
                interval="month",
                max_users=10,
                max_events=20,
                features={"basic": True, "advanced": True, "premium": False},
                is_active=True
            ),
            SubscriptionPlan(
                name="Enterprise",
                stripe_price_id="price_enterprise",
                description="Enterprise plan with all features",
                price=9999,  # $99.99
                interval="month",
                max_users=50,
                max_events=100,
                features={"basic": True, "advanced": True, "premium": True},
                is_active=True
            )
        ]
        
        db.add_all(plans)
        db.commit()
        
        print(f"Created {len(plans)} subscription plans successfully!")
    
    except Exception as e:
        print(f"Error creating subscription plans: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    create_subscription_plans()
