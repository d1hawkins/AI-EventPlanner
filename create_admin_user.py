#!/usr/bin/env python3
"""
Script to create an admin user in the database.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.abspath("."))

# Load environment variables
load_dotenv()

# Import the User model
from app.db.models import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """Create an admin user in the database."""
    print("Creating admin user...")
    
    # Get database URL from environment variable
    database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    # Create engine and session
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.username == "admin@example.com").first()
        if existing_user:
            print("Admin user already exists.")
            return
        
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            username="admin@example.com",
            hashed_password=pwd_context.hash("password123"),
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("Admin user created successfully!")
    
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
