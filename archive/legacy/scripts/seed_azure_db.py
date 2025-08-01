#!/usr/bin/env python
"""
Seed Azure PostgreSQL Database Script

This script seeds the Azure PostgreSQL database with initial data required for the SaaS application:
1. Subscription plans (free, professional, enterprise)
2. Admin user
3. Default organization (optional)

The script is idempotent and can be run multiple times without duplicating data.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("seed_azure_db")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def load_azure_env():
    """Load environment variables from .env.azure file."""
    logger.info("Loading environment variables from .env.azure...")
    if not os.path.exists(".env.azure"):
        logger.error("Error: .env.azure file not found.")
        return False
    
    load_dotenv(".env.azure")
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        logger.error("Error: DATABASE_URL not found in .env.azure file.")
        return False
    
    logger.info("✅ Loaded environment variables from .env.azure")
    return True

def get_db_connection():
    """Create a database connection."""
    try:
        # Get the DATABASE_URL from environment
        database_url = os.getenv("DATABASE_URL")
        
        # Create SQLAlchemy engine
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )
        
        # Create sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        
        return engine, SessionLocal
    except SQLAlchemyError as e:
        logger.error(f"Error connecting to database: {e}")
        return None, None

def check_if_table_exists(engine, table_name):
    """Check if a table exists in the database."""
    try:
        # Use SQLAlchemy's inspect to check if table exists (works for both SQLite and PostgreSQL)
        inspector = inspect(engine)
        exists = table_name in inspector.get_table_names()
        return exists
    except SQLAlchemyError as e:
        logger.error(f"Error checking if table exists: {e}")
        return False

def seed_subscription_plans(session):
    """Seed subscription plans."""
    logger.info("Seeding subscription plans...")
    
    # Check if subscription plans already exist
    result = session.execute(text("SELECT COUNT(*) FROM subscription_plans"))
    count = result.scalar()
    
    if count > 0:
        logger.info("Subscription plans already exist, skipping...")
        return True
    
    try:
        # Free plan
        session.execute(
            text("""
                INSERT INTO subscription_plans (
                    name, stripe_price_id, description, price, interval, 
                    max_users, max_events, features, is_active, created_at, updated_at
                ) VALUES (
                    'Free', 'price_free', 'Basic plan with limited features', 0, 'month',
                    5, 10, :features, true, :created_at, :updated_at
                )
            """),
            {
                "features": json.dumps({
                    "basic": True,
                    "advanced": False,
                    "premium": False,
                    "max_events": 5,
                    "max_users": 2,
                    "advanced_recommendations": False,
                    "custom_templates": False,
                    "priority_support": False,
                    "analytics_dashboard": False
                }),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        
        # Professional plan
        session.execute(
            text("""
                INSERT INTO subscription_plans (
                    name, stripe_price_id, description, price, interval, 
                    max_users, max_events, features, is_active, created_at, updated_at
                ) VALUES (
                    'Professional', 'price_professional', 'Advanced plan with more features', 2999, 'month',
                    20, 50, :features, true, :created_at, :updated_at
                )
            """),
            {
                "features": json.dumps({
                    "basic": True,
                    "advanced": True,
                    "premium": False,
                    "max_events": 20,
                    "max_users": 10,
                    "advanced_recommendations": True,
                    "custom_templates": True,
                    "priority_support": False,
                    "analytics_dashboard": True
                }),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        
        # Enterprise plan
        session.execute(
            text("""
                INSERT INTO subscription_plans (
                    name, stripe_price_id, description, price, interval, 
                    max_users, max_events, features, is_active, created_at, updated_at
                ) VALUES (
                    'Enterprise', 'price_enterprise', 'Premium plan with all features', 9999, 'month',
                    -1, -1, :features, true, :created_at, :updated_at
                )
            """),
            {
                "features": json.dumps({
                    "basic": True,
                    "advanced": True,
                    "premium": True,
                    "max_events": -1,
                    "max_users": -1,
                    "advanced_recommendations": True,
                    "custom_templates": True,
                    "priority_support": True,
                    "analytics_dashboard": True
                }),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        
        session.commit()
        logger.info("✅ Subscription plans seeded successfully")
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error seeding subscription plans: {e}")
        return False

def seed_admin_user(session, email, username, password):
    """Seed admin user."""
    logger.info(f"Seeding admin user: {username}...")
    
    # Check if user already exists
    result = session.execute(text("SELECT COUNT(*) FROM users WHERE email = :email"), {"email": email})
    count = result.scalar()
    
    if count > 0:
        logger.info("Admin user already exists, skipping...")
        return True
    
    try:
        # Hash the password
        hashed_password = pwd_context.hash(password)
        
        # Insert admin user
        session.execute(
            text("""
                INSERT INTO users (
                    email, username, hashed_password, is_active, created_at
                ) VALUES (
                    :email, :username, :hashed_password, true, :created_at
                )
            """),
            {
                "email": email,
                "username": username,
                "hashed_password": hashed_password,
                "created_at": datetime.utcnow()
            }
        )
        
        session.commit()
        logger.info("✅ Admin user seeded successfully")
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error seeding admin user: {e}")
        return False

def seed_default_organization(session, name, slug, admin_email):
    """Seed default organization."""
    logger.info(f"Seeding default organization: {name}...")
    
    # Check if organization already exists
    result = session.execute(text("SELECT COUNT(*) FROM organizations WHERE slug = :slug"), {"slug": slug})
    count = result.scalar()
    
    if count > 0:
        logger.info("Default organization already exists, skipping...")
        return True
    
    try:
        # Get the free plan ID
        result = session.execute(text("SELECT id FROM subscription_plans WHERE name = 'Free'"))
        plan_id = result.scalar()
        
        if not plan_id:
            logger.error("Free plan not found")
            return False
        
        # Get the admin user ID
        result = session.execute(text("SELECT id FROM users WHERE email = :email"), {"email": admin_email})
        user_id = result.scalar()
        
        if not user_id:
            logger.error(f"Admin user with email {admin_email} not found")
            return False
        
        # Insert organization
        session.execute(
            text("""
                INSERT INTO organizations (
                    name, slug, plan_id, subscription_status, max_users, max_events, 
                    features, created_at, updated_at
                ) VALUES (
                    :name, :slug, :plan_id, 'active', 5, 10, 
                    :features, :created_at, :updated_at
                ) RETURNING id
            """),
            {
                "name": name,
                "slug": slug,
                "plan_id": str(plan_id),
                "features": json.dumps({
                    "basic": True,
                    "advanced": False,
                    "premium": False
                }),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        
        # Get the organization ID
        result = session.execute(text("SELECT id FROM organizations WHERE slug = :slug"), {"slug": slug})
        org_id = result.scalar()
        
        # Add admin user to organization
        session.execute(
            text("""
                INSERT INTO organization_users (
                    organization_id, user_id, role, is_primary, created_at, updated_at
                ) VALUES (
                    :organization_id, :user_id, 'admin', true, :created_at, :updated_at
                )
            """),
            {
                "organization_id": org_id,
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        
        session.commit()
        logger.info("✅ Default organization seeded successfully")
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error seeding default organization: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Seed Azure PostgreSQL Database Script")
    parser.add_argument("--admin-email", default="admin@example.com", help="Admin user email")
    parser.add_argument("--admin-username", default="admin", help="Admin username")
    parser.add_argument("--admin-password", default="password123", help="Admin password")
    parser.add_argument("--org-name", default="Default Organization", help="Default organization name")
    parser.add_argument("--org-slug", default="default", help="Default organization slug")
    parser.add_argument("--skip-org", action="store_true", help="Skip creating default organization")
    
    args = parser.parse_args()
    
    # Load environment variables
    if not load_azure_env():
        return 1
    
    # Get database connection
    engine, SessionLocal = get_db_connection()
    if not engine or not SessionLocal:
        return 1
    
    # Check if tables exist
    if not check_if_table_exists(engine, "subscription_plans"):
        logger.error("Tables don't exist. Please run migrations first.")
        return 1
    
    # Create a session
    session = SessionLocal()
    
    try:
        # Seed subscription plans
        if not seed_subscription_plans(session):
            return 1
        
        # Seed admin user
        if not seed_admin_user(session, args.admin_email, args.admin_username, args.admin_password):
            return 1
        
        # Seed default organization (optional)
        if not args.skip_org:
            if not seed_default_organization(session, args.org_name, args.org_slug, args.admin_email):
                return 1
        
        logger.info("Database seeding completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    finally:
        session.close()

if __name__ == "__main__":
    sys.exit(main())
