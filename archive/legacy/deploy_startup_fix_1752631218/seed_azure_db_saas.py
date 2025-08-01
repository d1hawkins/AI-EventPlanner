#!/usr/bin/env python
"""
Seed Azure Database Script (SaaS Version)

This script seeds the Azure PostgreSQL database with initial data for SaaS models.
"""

import os
import sys
import argparse
import json
from datetime import datetime, timedelta

def test_connection():
    """Test the connection to the PostgreSQL database."""
    try:
        import psycopg2
    except ImportError:
        print("Installing psycopg2-binary...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        import psycopg2
    
    # Use hardcoded connection parameters for Azure PostgreSQL
    host = "ai-event-planner-db.postgres.database.azure.com"
    port = 5432
    dbname = "eventplanner"
    user = "dbadmin@ai-event-planner-db"  # Azure PostgreSQL requires username@hostname format
    password = "VM*admin"
    sslmode = "require"
    
    print(f"Testing connection to PostgreSQL database...")
    print(f"Connection details:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Database: {dbname}")
    print(f"  Username: {user}")
    print(f"  Password: {'*' * len(password)}")
    
    try:
        # Try to connect to the database
        print("Connecting to database...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            sslmode=sslmode
        )
        
        # Test the connection
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"Connected to PostgreSQL: {version[0]}")
        
        conn.close()
        print("✅ Connection test successful.")
        return True
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def seed_database(args):
    """Seed the database with initial data."""
    print("Seeding database with SaaS data...")
    
    # Set up the database connection
    host = "ai-event-planner-db.postgres.database.azure.com"
    port = 5432
    dbname = "eventplanner"
    user = "dbadmin@ai-event-planner-db"
    password = "VM*admin"
    sslmode = "require"
    
    # Set the DATABASE_URL environment variable
    os.environ["DATABASE_URL"] = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    
    # Import the SQLAlchemy models and create the tables
    try:
        # Add the project root to the Python path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sys.path.insert(0, project_root)
        
        # Import the SQLAlchemy models and session
        from sqlalchemy.orm import Session
        from app.db.base import engine
        from app.db.models import User
        
        # Import SaaS models
        try:
            # Import models directly from SQLAlchemy to avoid relationship issues
            from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Table, Text, JSON
            from app.db.base import Base
            
            # Define simplified models without relationships
            class SubscriptionPlan(Base):
                __tablename__ = "subscription_plans"
                __table_args__ = {'extend_existing': True}
                
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
            
            class Organization(Base):
                __tablename__ = "organizations"
                __table_args__ = {'extend_existing': True}
                
                id = Column(Integer, primary_key=True, index=True)
                name = Column(String(255), nullable=False)
                slug = Column(String(50), unique=True, nullable=False)
                plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
                stripe_customer_id = Column(String(255), nullable=True)
                stripe_subscription_id = Column(String(255), nullable=True)
                subscription_status = Column(String(50), default="inactive")
                max_users = Column(Integer, default=5)
                max_events = Column(Integer, default=10)
                features = Column(Text, default='{"basic": true, "advanced": false, "premium": false}')
                created_at = Column(DateTime, default=datetime.utcnow)
                updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            
            class OrganizationUser(Base):
                __tablename__ = "organization_users"
                __table_args__ = {'extend_existing': True}
                
                organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)
                user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
                role = Column(String(50), nullable=False)  # admin, manager, user
                is_primary = Column(Boolean, default=False)
                created_at = Column(DateTime, default=datetime.utcnow)
                updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            
            class SubscriptionInvoice(Base):
                __tablename__ = "subscription_invoices"
                __table_args__ = {'extend_existing': True}
                
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
            
            has_saas_models = True
        except ImportError as e:
            has_saas_models = False
            print(f"Error importing SQLAlchemy: {e}")
            print("Cannot seed SaaS data.")
            return False
        
        # Create a session
        session = Session(engine)
        
        # Check if there are already subscription plans in the database
        existing_plans = session.query(SubscriptionPlan).count()
        if existing_plans > 0 and not args.force:
            print(f"Database already has {existing_plans} subscription plans. Skipping seeding.")
            print("Use --force to seed the database anyway.")
            session.close()
            return True
        elif existing_plans > 0 and args.force:
            print(f"Database already has {existing_plans} subscription plans. Forcing seeding...")
            print("Deleting existing SaaS data...")
            
            # Delete existing data in reverse order of dependencies
            session.query(OrganizationUser).delete()
            session.query(Organization).delete()
            session.query(SubscriptionPlan).delete()
            session.query(SubscriptionInvoice).delete()
            session.commit()
            print("Existing SaaS data deleted.")
        
        # Get existing users
        admin_user = session.query(User).filter(User.username == "admin").first()
        test_user = session.query(User).filter(User.username == "testuser").first()
        
        if not admin_user or not test_user:
            print("Error: Required users not found in the database.")
            print("Please run seed_azure_db_basic.py first to create the basic data.")
            session.close()
            return False
        
        # Create sample subscription plans
        print("Creating sample subscription plans...")
        basic_plan = SubscriptionPlan(
            name="Basic",
            stripe_price_id="price_basic",
            description="Basic plan with limited features",
            price=999,  # $9.99
            interval="month",
            max_users=5,
            max_events=10,
            features=json.dumps({"basic": True, "advanced": False, "premium": False}),
            is_active=True
        )
        
        premium_plan = SubscriptionPlan(
            name="Premium",
            stripe_price_id="price_premium",
            description="Premium plan with all features",
            price=2999,  # $29.99
            interval="month",
            max_users=20,
            max_events=50,
            features=json.dumps({"basic": True, "advanced": True, "premium": True}),
            is_active=True
        )
        
        session.add_all([basic_plan, premium_plan])
        session.commit()
        print(f"Created {session.query(SubscriptionPlan).count()} subscription plans.")
        
        # Create sample organizations
        print("Creating sample organizations...")
        org1 = Organization(
            name="Acme Inc.",
            slug="acme",
            plan_id=basic_plan.id,
            subscription_status="active",
            max_users=5,
            max_events=10,
            features=json.dumps({"basic": True, "advanced": False, "premium": False})
        )
        
        org2 = Organization(
            name="XYZ Corp",
            slug="xyz",
            plan_id=premium_plan.id,
            subscription_status="active",
            max_users=20,
            max_events=50,
            features=json.dumps({"basic": True, "advanced": True, "premium": True})
        )
        
        session.add_all([org1, org2])
        session.commit()
        print(f"Created {session.query(Organization).count()} organizations.")
        
        # Create organization users
        print("Creating organization users...")
        org_user1 = OrganizationUser(
            organization_id=org1.id,
            user_id=admin_user.id,
            role="admin",
            is_primary=True
        )
        
        org_user2 = OrganizationUser(
            organization_id=org2.id,
            user_id=test_user.id,
            role="admin",
            is_primary=True
        )
        
        session.add_all([org_user1, org_user2])
        session.commit()
        print(f"Created {session.query(OrganizationUser).count()} organization users.")
        
        session.close()
        print("✅ SaaS database seeded successfully.")
        return True
    except ImportError as e:
        print(f"Error importing SQLAlchemy models: {e}")
        print("Make sure you're running this script from the project root directory.")
        return False
    except Exception as e:
        print(f"Error seeding database: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Seed Azure Database Script (SaaS Version)")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("--force", action="store_true", help="Force seeding even if data exists")
    
    args = parser.parse_args()
    
    # Test the connection
    if not test_connection():
        return 1
    
    # Seed the database
    if not seed_database(args):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
