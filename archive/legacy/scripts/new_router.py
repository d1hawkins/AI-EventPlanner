from datetime import datetime
import json
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, Conversation, Message, AgentState
from app.auth.dependencies import get_current_user
from app.schemas.event import ConversationCreate, Conversation as ConversationSchema, ConversationMessage
from app.state.manager import StateManager
from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post("/conversations", response_model=ConversationSchema)
async def create_conversation(
    conversation_in: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new conversation.
    
    Args:
        conversation_in: Conversation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created conversation
    """
    # Create a new conversation
    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_in.title,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    # Initialize agent state
    state_manager = StateManager(db)
    initial_state = create_initial_state()
    await state_manager.save_state(conversation.id, initial_state)
    
    return conversation


@router.get("/conversations", response_model=List[ConversationSchema])
async def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all conversations for the current user.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of conversations
    """
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).all()
    
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationSchema)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a conversation by ID.
    
    Args:
        conversation_id: ID of the conversation
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Conversation
        
    Raises:
        HTTPException: If conversation not found or not owned by user
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a conversation.
    
    Args:
        conversation_id: ID of the conversation
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If conversation not found or not owned by user
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    db.delete(conversation)
    db.commit()
    
    return None


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for chat.
    
    Args:
        websocket: WebSocket connection
        conversation_id: ID of the conversation
        token: Authentication token
        db: Database session
    """
    await websocket.accept()
    
    try:
        # Verify token and get user
        from app.auth.dependencies import get_current_user
        from fastapi import Request
        
        # Create a mock request with the token
        mock_request = Request({"type": "http"})
        mock_request._headers = {"authorization": f"Bearer {token}"}
        
        # Get the current user
        user = await get_current_user(db, token)
        
        # Verify user has access to this conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        ).first()
        
        if not conversation:
            await websocket.send_text(json.dumps({
                "error": "Conversation not found or access denied"
            }))
            await websocket.close()
            return
        
        # Initialize state manager and coordinator graph
        state_manager = StateManager(db)
        coordinator_graph = create_coordinator_graph()
        
        # Get current state or create initial state
        current_state = await state_manager.get_state(conversation_id)
        if not current_state:
            current_state = create_initial_state()
        
        # Load existing messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp).all()
        
        # Add existing messages to state
        current_state["messages"] = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Send existing messages to client
        for message in messages:
            await websocket.send_text(json.dumps({
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp.isoformat()
            }))
        
        # Main WebSocket loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Save user message to database
            message = Message(
                conversation_id=conversation_id,
                role="user",
                content=message_data["content"],
                timestamp=datetime.utcnow()
            )
            db.add(message)
            db.commit()
            
            # Update state with new message
            current_state["messages"].append({
                "role": "user",
                "content": message_data["content"]
            })
            
            # Run the coordinator graph
            result = coordinator_graph.invoke(current_state)
            
            # Save the updated state
            await state_manager.save_state(conversation_id, result)
            
            # Extract the response
            assistant_messages = [
                msg for msg in result["messages"]
                if msg["role"] == "assistant" and msg not in current_state["messages"]
            ]
            
            # Save assistant messages to database and send to client
            for assistant_message in assistant_messages:
                # Save to database
                db_message = Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=assistant_message["content"],
                    timestamp=datetime.utcnow()
                )
                db.add(db_message)
                db.commit()
                
                # Send to client
                await websocket.send_text(json.dumps({
                    "role": "assistant",
                    "content": assistant_message["content"],
                    "timestamp": db_message.timestamp.isoformat()
                }))
            
            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            db.commit()
            
    except WebSocketDisconnect:
        print(f"Client disconnected from conversation {conversation_id}")
    except Exception as e:
        print(f"Error in WebSocket: {str(e)}")
        await websocket.close()
