"""
Test script for agent state persistence.

This script creates a conversation with an agent, sends a message,
and then retrieves the conversation state to verify persistence.

Usage:
    python test_agent_persistence.py [conversation_id]

If a conversation_id is provided, the script will load that conversation.
Otherwise, it will create a new conversation.
"""

import sys
import json
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.session import get_db
from app.agents.agent_factory import get_agent_factory
from app.state.tenant_aware_manager import get_tenant_aware_state_manager


def get_db_session():
    """Get a database session."""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


def create_new_conversation(db: Session):
    """Create a new conversation with an agent and send a test message."""
    # Create agent factory
    agent_factory = get_agent_factory(db=db)
    
    # Create a new conversation ID
    import uuid
    conversation_id = str(uuid.uuid4())
    
    print(f"\n=== Creating new conversation: {conversation_id} ===\n")
    
    # Create a coordinator agent
    agent = agent_factory.create_agent(
        agent_type="coordinator",
        conversation_id=conversation_id
    )
    
    # Send a test message
    test_message = "Hello, I'm testing the persistence of agent state. Can you remember this message?"
    print(f"Sending message: '{test_message}'")
    
    # Add the message to the state
    state = agent["state"]
    if "messages" not in state:
        state["messages"] = []
    
    # Add the user message
    state["messages"].append({
        "role": "user",
        "content": test_message
    })
    
    # Run the agent graph
    result = agent["graph"].invoke(state)
    
    # Update the state
    agent_factory.state_manager.update_conversation_state(conversation_id, result)
    
    # Force a sync to the database
    agent_factory.state_manager.force_sync()
    
    # Extract the assistant's response
    assistant_messages = [
        msg for msg in result.get("messages", [])
        if msg.get("role") == "assistant" and not msg.get("ephemeral", False)
    ]
    
    # Get the last assistant message
    if assistant_messages:
        last_message = assistant_messages[-1]["content"]
        print(f"\nAgent response: '{last_message}'\n")
    
    print(f"Conversation created and synced to database.")
    print(f"Conversation ID: {conversation_id}")
    print(f"Use this ID to test persistence after restarting the application:")
    print(f"python test_agent_persistence.py {conversation_id}")
    
    return conversation_id


def load_existing_conversation(db: Session, conversation_id: str):
    """Load an existing conversation and display its messages."""
    # Get state manager
    state_manager = get_tenant_aware_state_manager(db=db)
    
    print(f"\n=== Loading existing conversation: {conversation_id} ===\n")
    
    # Get the conversation state
    state = state_manager.get_conversation_state(conversation_id)
    
    if not state:
        print(f"No conversation found with ID: {conversation_id}")
        return
    
    # Display the messages
    messages = state.get("messages", [])
    if not messages:
        print("No messages found in this conversation.")
        return
    
    print(f"Found {len(messages)} messages in the conversation:\n")
    
    for i, message in enumerate(messages):
        role = message.get("role", "unknown")
        content = message.get("content", "")
        
        if role == "user":
            print(f"User: {content}")
        elif role == "assistant":
            print(f"Agent: {content}")
        elif role == "system":
            print(f"System: {content}")
        else:
            print(f"{role.capitalize()}: {content}")
        
        # Add a separator between messages
        if i < len(messages) - 1:
            print("-" * 50)
    
    print("\nConversation loaded successfully.")
    print("This demonstrates that the state was persisted to the database.")


def main():
    """Main function."""
    # Get database session
    db = next(get_db())
    
    try:
        # Check if a conversation ID was provided
        if len(sys.argv) > 1:
            conversation_id = sys.argv[1]
            load_existing_conversation(db, conversation_id)
        else:
            create_new_conversation(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
