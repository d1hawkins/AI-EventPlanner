#!/usr/bin/env python3
"""
Script to create test users for the SaaS application.
"""

import os
import sys
from sqlalchemy.orm import Session

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import get_db
from app.db.models_updated import User
from app.auth.router import get_password_hash

def create_test_users():
    """Create test users for login testing."""
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Test users to create
        test_users = [
            {
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123"
            },
            {
                "username": "admin",
                "email": "admin@example.com", 
                "password": "admin123"
            },
            {
                "username": "demo",
                "email": "demo@example.com",
                "password": "demo123"
            }
        ]
        
        for user_data in test_users:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.username == user_data["username"]) | 
                (User.email == user_data["email"])
            ).first()
            
            if existing_user:
                print(f"User {user_data['username']} already exists, skipping...")
                continue
            
            # Create new user
            new_user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                is_active=True
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f"Created user: {user_data['username']} ({user_data['email']})")
            print(f"  Password: {user_data['password']}")
        
        print("\nTest users created successfully!")
        print("You can now test login with any of the above credentials.")
        
    except Exception as e:
        print(f"Error creating test users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()
