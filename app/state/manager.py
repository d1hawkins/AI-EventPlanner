import json
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from app.db.models import AgentState, Conversation


class StateManager:
    """
    Manager for persisting and retrieving agent state.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the state manager.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def get_state(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the agent state for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Agent state as a dictionary, or None if not found
        """
        agent_state = self.db.query(AgentState).filter(
            AgentState.conversation_id == conversation_id
        ).first()
        
        if not agent_state:
            return None
        
        return json.loads(agent_state.state_data)
    
    async def save_state(self, conversation_id: int, state_data: Dict[str, Any]) -> AgentState:
        """
        Save the agent state for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            state_data: Agent state as a dictionary
            
        Returns:
            Updated AgentState object
        """
        # Check if conversation exists
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise ValueError(f"Conversation with ID {conversation_id} not found")
        
        # Check if agent state exists
        agent_state = self.db.query(AgentState).filter(
            AgentState.conversation_id == conversation_id
        ).first()
        
        # Ensure proper JSON formatting for messages
        if "messages" in state_data and isinstance(state_data["messages"], list):
            # Make sure each message has the required fields
            for i, msg in enumerate(state_data["messages"]):
                if isinstance(msg, dict):
                    if "role" not in msg:
                        msg["role"] = "user"
                    if "content" not in msg:
                        msg["content"] = ""
                    
            # Print the messages for debugging
            print(f"Saving state with {len(state_data['messages'])} messages")
            for msg in state_data["messages"]:
                if msg.get("role") == "assistant":
                    print(f"Assistant message: {msg.get('content')[:50]}...")
        
        if agent_state:
            # Update existing state
            agent_state.state_data = json.dumps(state_data)
        else:
            # Create new state
            agent_state = AgentState(
                conversation_id=conversation_id,
                state_data=json.dumps(state_data)
            )
            self.db.add(agent_state)
        
        self.db.commit()
        self.db.refresh(agent_state)
        
        return agent_state
