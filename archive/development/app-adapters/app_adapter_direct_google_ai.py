#!/usr/bin/env python3
"""
Direct Google AI Integration Adapter - Nuclear Option
This adapter completely bypasses complex imports and directly uses Google AI.
"""

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional
import traceback

# Try to import FastAPI - this should always work since it's in requirements.txt
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    print("✅ FastAPI imported successfully")
except ImportError as e:
    print(f"❌ Failed to import FastAPI: {e}")
    raise

# Try to import Google AI - this is our main dependency
try:
    import google.generativeai as genai
    print("✅ Google AI imported successfully")
    GOOGLE_AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Google AI not available: {e}")
    GOOGLE_AI_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(title="AI Event Planner - Direct Google AI", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class AgentMessageRequest(BaseModel):
    agent_type: str
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[int] = None
    organization_id: Optional[int] = None

class AgentMessageResponse(BaseModel):
    response: str
    agent_type: str
    conversation_id: Optional[str] = None
    timestamp: str
    status: str
    source: str

# Configure Google AI if available
if GOOGLE_AI_AVAILABLE:
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        print(f"✅ Google AI configured with API key: {api_key[:8]}...")
    else:
        print("⚠️ GOOGLE_API_KEY not found in environment")
        GOOGLE_AI_AVAILABLE = False

async def get_google_ai_response(agent_type: str, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """Get response directly from Google AI."""
    
    if not GOOGLE_AI_AVAILABLE:
        return {
            "response": f"Google AI not available. I'm the {agent_type} agent and I received: '{message}'. How can I help with event planning?",
            "agent_type": agent_type,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "status": "fallback",
            "source": "direct_fallback"
        }
    
    try:
        # Create the model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create agent-specific prompts
        if agent_type.lower() == "coordinator":
            prompt = f"""You are an AI Event Planning Coordinator. You help users plan and coordinate events professionally and efficiently.

User message: {message}

Please provide a helpful, detailed response about event planning. Include specific suggestions, considerations, and next steps where appropriate. Be professional but friendly."""

        elif agent_type.lower() == "financial":
            prompt = f"""You are an AI Financial Planning Agent for events. You help with budgeting, cost estimation, and financial planning for events.

User message: {message}

Please provide detailed financial advice, budget considerations, cost estimates, and money-saving tips for event planning."""

        elif agent_type.lower() == "marketing":
            prompt = f"""You are an AI Marketing Agent for events. You help with promotion, marketing strategies, and audience engagement for events.

User message: {message}

Please provide marketing strategies, promotional ideas, social media tips, and audience engagement suggestions for events."""

        elif agent_type.lower() == "stakeholder":
            prompt = f"""You are an AI Stakeholder Management Agent for events. You help manage relationships with vendors, sponsors, partners, and other stakeholders.

User message: {message}

Please provide advice on stakeholder management, vendor relationships, partnership strategies, and communication approaches."""

        else:
            prompt = f"""You are an AI assistant specializing in {agent_type} for event planning. 

User message: {message}

Please provide helpful, professional advice related to {agent_type} in the context of event planning."""

        # Generate response
        response = model.generate_content(prompt)
        
        return {
            "response": response.text,
            "agent_type": agent_type,
            "conversation_id": conversation_id or f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "source": "direct_google_ai"
        }
        
    except Exception as e:
        print(f"❌ Google AI error: {e}")
        traceback.print_exc()
        
        # Fallback response
        return {
            "response": f"I'm the {agent_type} agent. I received your message: '{message}'. I'm experiencing some technical difficulties, but I'm here to help with event planning. Could you please rephrase your question?",
            "agent_type": agent_type,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "status": "error_fallback",
            "source": "direct_error_fallback"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "google_ai_available": GOOGLE_AI_AVAILABLE,
        "api_key_configured": bool(os.getenv('GOOGLE_API_KEY')),
        "version": "direct_google_ai_v1.0"
    }

@app.get("/api/agents/available")
async def get_available_agents():
    """Get list of available agents."""
    return {
        "agents": [
            {
                "type": "coordinator",
                "name": "Event Coordinator",
                "description": "Main event planning coordination",
                "status": "active"
            },
            {
                "type": "financial",
                "name": "Financial Planner",
                "description": "Budget and cost management",
                "status": "active"
            },
            {
                "type": "marketing",
                "name": "Marketing Specialist",
                "description": "Event promotion and marketing",
                "status": "active"
            },
            {
                "type": "stakeholder",
                "name": "Stakeholder Manager",
                "description": "Vendor and partner management",
                "status": "active"
            }
        ],
        "total_agents": 4,
        "real_agents_enabled": GOOGLE_AI_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/agents/message", response_model=AgentMessageResponse)
async def send_agent_message(request: AgentMessageRequest):
    """Send message to an agent and get response."""
    
    print(f"🔥 DIRECT GOOGLE AI: Received message for {request.agent_type}: {request.message}")
    
    try:
        # Get response directly from Google AI
        response_data = await get_google_ai_response(
            agent_type=request.agent_type,
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        print(f"✅ DIRECT GOOGLE AI: Generated response from {response_data['source']}")
        
        return AgentMessageResponse(**response_data)
        
    except Exception as e:
        print(f"❌ DIRECT GOOGLE AI: Error processing message: {e}")
        traceback.print_exc()
        
        # Ultimate fallback
        return AgentMessageResponse(
            response=f"I'm the {request.agent_type} agent. I received your message: '{request.message}'. I'm experiencing technical difficulties but I'm here to help with event planning.",
            agent_type=request.agent_type,
            conversation_id=request.conversation_id,
            timestamp=datetime.now().isoformat(),
            status="ultimate_fallback",
            source="direct_ultimate_fallback"
        )

@app.get("/api/agents/conversations")
async def list_conversations():
    """List conversations (simplified for direct implementation)."""
    return {
        "conversations": [],
        "total": 0,
        "message": "Conversation history not implemented in direct mode"
    }

@app.get("/api/agents/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """Get conversation history (simplified for direct implementation)."""
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "total": 0,
        "message": "Conversation history not implemented in direct mode"
    }

@app.delete("/api/agents/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation (simplified for direct implementation)."""
    return {
        "conversation_id": conversation_id,
        "status": "deleted",
        "message": "Conversation deletion not implemented in direct mode"
    }

# Static file serving for the web interface
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Event Planner - Direct Google AI Integration",
        "version": "1.0.0",
        "google_ai_available": GOOGLE_AI_AVAILABLE,
        "endpoints": {
            "health": "/health",
            "agents": "/api/agents/available",
            "message": "/api/agents/message",
            "conversations": "/api/agents/conversations"
        }
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    print(f"❌ Global exception: {exc}")
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Direct Google AI Adapter...")
    print(f"Google AI Available: {GOOGLE_AI_AVAILABLE}")
    print(f"API Key Configured: {bool(os.getenv('GOOGLE_API_KEY'))}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
