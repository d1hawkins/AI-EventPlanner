#!/usr/bin/env python3
"""
Script to clear a user's conversations from the database.
This is useful for testing purposes to start with a clean slate.
"""

import argparse
import sys
from sqlalchemy.orm import Session

# Import database models and session
from app.db.base import SessionLocal
from app.db.models import User, Conversation


def get_user_by_identifier(db: Session, identifier: str, id_type: str):
    """
    Find a user by the specified identifier type.
    
    Args:
        db: Database session
        identifier: The identifier value (email, username, or id)
        id_type: The type of identifier ('email', 'username', or 'id')
        
    Returns:
        User object or None if not found
    """
    if id_type == "email":
        return db.query(User).filter(User.email == identifier).first()
    elif id_type == "username":
        return db.query(User).filter(User.username == identifier).first()
    elif id_type == "id":
        try:
            user_id = int(identifier)
            return db.query(User).filter(User.id == user_id).first()
        except ValueError:
            print(f"Error: ID must be an integer, got '{identifier}'")
            return None
    else:
        print(f"Error: Invalid identifier type '{id_type}'")
        return None


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


def main():
    """Main function to parse arguments and clear conversations."""
    parser = argparse.ArgumentParser(description="Clear a user's conversations from the database")
    parser.add_argument("--identifier", required=True, help="User identifier (email, username, or ID)")
    parser.add_argument("--type", required=True, choices=["email", "username", "id"], 
                        help="Type of identifier")
    
    args = parser.parse_args()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Find the user
        user = get_user_by_identifier(db, args.identifier, args.type)
        
        if not user:
            print(f"Error: User not found with {args.type} '{args.identifier}'")
            sys.exit(1)
        
        # Clear conversations
        conversation_count = clear_user_conversations(db, user)
        
        print(f"Success: Deleted {conversation_count} conversations for user {user.username} (ID: {user.id})")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
