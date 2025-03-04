#!/usr/bin/env python3
"""
Script to clear conversations from the database.
This is useful for testing purposes to start with a clean slate.

This script provides both command-line functionality and importable functions.
"""

import sys
from sqlalchemy.orm import Session

# Import database models and session
from app.db.base import SessionLocal
from app.db.models import User, Conversation


def get_user_by_email(db: Session, email: str):
    """
    Find a user by email.
    
    Args:
        db: Database session
        email: User's email
        
    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    """
    Find a user by username.
    
    Args:
        db: Database session
        username: User's username
        
    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    """
    Find a user by ID.
    
    Args:
        db: Database session
        user_id: User's ID
        
    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.id == user_id).first()


def clear_user_conversations(db: Session, user):
    """
    Delete all conversations for a user.
    
    Args:
        db: Database session
        user: User object
        
    Returns:
        Number of conversations deleted
    """
    # Get count of conversations before deletion
    conversation_count = db.query(Conversation).filter(Conversation.user_id == user.id).count()
    
    # Delete all conversations for the user
    # This will cascade delete related messages, agent_state, events, tasks, and stakeholders
    # due to the SQLAlchemy cascade settings
    db.query(Conversation).filter(Conversation.user_id == user.id).delete()
    
    # Commit the changes
    db.commit()
    
    return conversation_count


def clear_all_conversations(db: Session):
    """
    Delete all conversations for all users.
    
    Args:
        db: Database session
        
    Returns:
        Number of conversations deleted
    """
    # Get count of conversations before deletion
    conversation_count = db.query(Conversation).count()
    
    # Delete all conversations
    # This will cascade delete related messages, agent_state, events, tasks, and stakeholders
    # due to the SQLAlchemy cascade settings
    db.query(Conversation).delete()
    
    # Commit the changes
    db.commit()
    
    return conversation_count


def clear_by_email(email: str):
    """
    Clear conversations for a user identified by email.
    
    Args:
        email: User's email
        
    Returns:
        Tuple of (success, message)
    """
    db = SessionLocal()
    try:
        user = get_user_by_email(db, email)
        if not user:
            return False, f"User not found with email '{email}'"
        
        count = clear_user_conversations(db, user)
        return True, f"Deleted {count} conversations for user {user.username} (ID: {user.id})"
    finally:
        db.close()


def clear_by_username(username: str):
    """
    Clear conversations for a user identified by username.
    
    Args:
        username: User's username
        
    Returns:
        Tuple of (success, message)
    """
    db = SessionLocal()
    try:
        user = get_user_by_username(db, username)
        if not user:
            return False, f"User not found with username '{username}'"
        
        count = clear_user_conversations(db, user)
        return True, f"Deleted {count} conversations for user {user.username} (ID: {user.id})"
    finally:
        db.close()


def clear_by_id(user_id: int):
    """
    Clear conversations for a user identified by ID.
    
    Args:
        user_id: User's ID
        
    Returns:
        Tuple of (success, message)
    """
    db = SessionLocal()
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            return False, f"User not found with ID '{user_id}'"
        
        count = clear_user_conversations(db, user)
        return True, f"Deleted {count} conversations for user {user.username} (ID: {user.id})"
    finally:
        db.close()


def clear_all():
    """
    Clear all conversations for all users.
    
    Returns:
        Tuple of (success, message)
    """
    db = SessionLocal()
    try:
        count = clear_all_conversations(db)
        return True, f"Deleted {count} conversations for all users"
    finally:
        db.close()


if __name__ == "__main__":
    # Simple interactive mode when run directly
    print("Conversation Cleanup Utility")
    print("----------------------------")
    print("1. Clear conversations for a specific user")
    print("2. Clear all conversations")
    print("3. Exit")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        print("\nIdentify user by:")
        print("1. Email")
        print("2. Username")
        print("3. ID")
        
        id_choice = input("Enter your choice (1-3): ")
        
        if id_choice == "1":
            email = input("Enter user email: ")
            success, message = clear_by_email(email)
        elif id_choice == "2":
            username = input("Enter username: ")
            success, message = clear_by_username(username)
        elif id_choice == "3":
            try:
                user_id = int(input("Enter user ID: "))
                success, message = clear_by_id(user_id)
            except ValueError:
                success, message = False, "Error: ID must be an integer"
        else:
            success, message = False, "Invalid choice"
    
    elif choice == "2":
        confirm = input("Are you sure you want to clear ALL conversations? (y/n): ")
        if confirm.lower() == "y":
            success, message = clear_all()
        else:
            success, message = False, "Operation cancelled"
    
    elif choice == "3":
        success, message = True, "Exiting"
    
    else:
        success, message = False, "Invalid choice"
    
    # Print result
    print(f"\n{'SUCCESS' if success else 'ERROR'}: {message}")
    
    if not success:
        sys.exit(1)
