#!/usr/bin/env python3
"""
Conversational Azure adapter with full agent functionality - ASGI Compatible
This version uses the real conversational coordinator graph
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add paths for Azure deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.dirname(current_dir))

# Azure wwwroot path
wwwroot_dir = '/home/site/wwwroot'
if os.path.exists(wwwroot_dir):
    sys.path.insert(0, wwwroot_dir)

print("🚀 Starting conversational agent adapter (ASGI)...")

# Environment configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU')
USE_REAL_AGENTS = os.getenv('USE_REAL_AGENTS', 'true').lower() == 'true'
CONVERSATION_MODE = os.getenv('CONVERSATION_MODE', 'enabled').lower() == 'enabled'
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'google')
GOOGLE_MODEL = os.getenv('GOOGLE_MODEL', 'gemini-2.0-flash')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import conversational coordinator
try:
    from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state
    from app.utils.question_manager import QuestionManager
    from app.utils.recommendation_engine import RecommendationEngine
    from app.utils.conversation_memory import ConversationMemory
    CONVERSATIONAL_AVAILABLE = True
    logger.info("✅ Conversational coordinator imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import conversational coordinator: {e}")
    CONVERSATIONAL_AVAILABLE = False

# Global coordinator graph
coordinator_graph = None
question_manager = None
recommendation_engine = None
conversation_memory = None

if CONVERSATIONAL_AVAILABLE:
    try:
        coordinator_graph = create_coordinator_graph()
        question_manager = QuestionManager()
        recommendation_engine = RecommendationEngine()
        conversation_memory = ConversationMemory()
        logger.info("✅ Conversational coordinator graph created")
    except Exception as e:
        logger.error(f"❌ Failed to create coordinator graph: {e}")
        coordinator_graph = None

# FastAPI app
app = FastAPI(title="AI Event Planner - Conversational SaaS", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AgentMessage(BaseModel):
    agent_type: str
    message: str
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    response: str
    conversation_id: str
    agent_type: str
    conversation_stage: Optional[str] = None
    current_question_focus: Optional[str] = None
    recommendations: Optional[List[str]] = None
    using_real_agent: bool
    using_conversational_flow: bool
    timestamp: str
    error: Optional[str] = None

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
    logger.info("✅ Static files mounted")
except Exception as e:
    logger.warning(f"⚠️ Could not mount static files: {e}")

async def get_conversational_response(agent_type: str, message: str, conversation_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get response using the conversational coordinator graph"""
    try:
        if not coordinator_graph:
            raise Exception("Coordinator graph not available")
        
        # Create or load conversation state
        state = create_initial_state()
        
        # Add context if provided
        if context:
            state.update(context)
        
        # Add user message to state
        state["messages"].append({
            "role": "user",
            "content": message
        })
        
        # Set conversation stage for discovery
        if not state.get("conversation_stage"):
            state["conversation_stage"] = "discovery"
        
        # Run the coordinator graph
        result = await asyncio.to_thread(coordinator_graph.invoke, state)
        
        # Extract the last assistant message
        assistant_messages = [msg for msg in result["messages"] if msg["role"] == "assistant"]
        if assistant_messages:
            response_text = assistant_messages[-1]["content"]
        else:
            response_text = "I'm here to help you plan your event. Could you tell me more about what you have in mind?"
        
        # Get recommendations if available
        recommendations = []
        if recommendation_engine:
            try:
                recommendations = recommendation_engine.get_recommendations(
                    conversation_stage=result.get("conversation_stage", "discovery"),
                    user_message=message,
                    context=result
                )
            except Exception as e:
                logger.warning(f"Could not get recommendations: {e}")
        
        return {
            "response": response_text,
            "conversation_id": conversation_id or f"conv_{agent_type}_{int(datetime.now().timestamp())}",
            "agent_type": agent_type,
            "conversation_stage": result.get("conversation_stage", "discovery"),
            "current_question_focus": result.get("current_question_focus"),
            "recommendations": recommendations,
            "using_real_agent": True,
            "using_conversational_flow": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error in conversational response: {e}")
        # Fallback to simple response
        return {
            "response": f"I'm the {agent_type} agent. I encountered an issue but I'm here to help with your event planning. Could you please rephrase your question?",
            "conversation_id": conversation_id or f"conv_{agent_type}_fallback",
            "agent_type": agent_type,
            "using_real_agent": False,
            "using_conversational_flow": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "real_agents_available": CONVERSATIONAL_AVAILABLE and coordinator_graph is not None,
        "conversation_mode": CONVERSATION_MODE,
        "llm_provider": LLM_PROVIDER,
        "google_model": GOOGLE_MODEL,
        "using_conversational_flow": CONVERSATIONAL_AVAILABLE,
        "components": {
            "coordinator_graph": coordinator_graph is not None,
            "question_manager": question_manager is not None,
            "recommendation_engine": recommendation_engine is not None,
            "conversation_memory": conversation_memory is not None
        }
    }

# Agent message endpoint
@app.post("/api/agents/message", response_model=AgentResponse)
async def send_agent_message(message: AgentMessage):
    """Send message to agent and get conversational response"""
    try:
        response_data = await get_conversational_response(
            agent_type=message.agent_type,
            message=message.message,
            conversation_id=message.conversation_id,
            context=message.context
        )
        return AgentResponse(**response_data)
    except Exception as e:
        logger.error(f"Error in agent message endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Available agents endpoint
@app.get("/api/agents/available")
async def get_available_agents():
    """Get list of available agents"""
    agents = [
        {
            "id": "coordinator",
            "name": "Event Coordinator",
            "description": "Main coordinator for event planning with conversational flow",
            "capabilities": ["event_planning", "coordination", "recommendations", "conversation_flow"],
            "conversational": True
        },
        {
            "id": "financial",
            "name": "Financial Planner",
            "description": "Budget planning and financial analysis",
            "capabilities": ["budget_planning", "cost_analysis", "financial_recommendations"],
            "conversational": True
        },
        {
            "id": "marketing",
            "name": "Marketing Specialist",
            "description": "Marketing strategy and promotion planning",
            "capabilities": ["marketing_strategy", "promotion_planning", "audience_analysis"],
            "conversational": True
        }
    ]
    
    return {
        "agents": agents,
        "total_count": len(agents),
        "conversational_mode": CONVERSATION_MODE,
        "real_agents_active": CONVERSATIONAL_AVAILABLE
    }

# Events API endpoints
@app.get("/api/events")
async def get_events():
    """Get events (mock data for now)"""
    return {
        "events": [],
        "total_count": 0,
        "message": "Events API is available"
    }

@app.post("/api/events")
async def create_event(event_data: dict):
    """Create new event"""
    return {
        "message": "Event creation endpoint is available",
        "event_data": event_data
    }

# Static file routes for SaaS pages
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main page"""
    try:
        return FileResponse("app/web/static/saas/index.html")
    except:
        return HTMLResponse("<h1>AI Event Planner - Conversational SaaS</h1><p>Welcome to the conversational event planning platform!</p>")

@app.get("/dashboard.html", response_class=HTMLResponse)
async def dashboard():
    """Serve dashboard page"""
    try:
        return FileResponse("app/web/static/saas/dashboard.html")
    except:
        return HTMLResponse("<h1>Dashboard</h1><p>Dashboard page not found</p>")

@app.get("/agents.html", response_class=HTMLResponse)
async def agents():
    """Serve agents page"""
    try:
        return FileResponse("app/web/static/saas/agents.html")
    except:
        return HTMLResponse("<h1>AI Agents</h1><p>Conversational AI agents for event planning</p>")

@app.get("/events.html", response_class=HTMLResponse)
async def events():
    """Serve events page"""
    try:
        return FileResponse("app/web/static/saas/events.html")
    except:
        return HTMLResponse("<h1>Events</h1><p>Event management page</p>")

@app.get("/login.html", response_class=HTMLResponse)
async def login():
    """Serve login page"""
    try:
        return FileResponse("app/web/static/saas/login.html")
    except:
        return HTMLResponse("<h1>Login</h1><p>Login page</p>")

@app.get("/signup.html", response_class=HTMLResponse)
async def signup():
    """Serve signup page"""
    try:
        return FileResponse("app/web/static/saas/signup.html")
    except:
        return HTMLResponse("<h1>Sign Up</h1><p>Sign up page</p>")

# Test conversational flow endpoint
@app.post("/api/test/conversation")
async def test_conversation():
    """Test conversational flow"""
    try:
        test_response = await get_conversational_response(
            agent_type="coordinator",
            message="I want to plan a corporate event"
        )
        return {
            "test_status": "success",
            "conversational_flow_working": test_response.get("using_conversational_flow", False),
            "response": test_response
        }
    except Exception as e:
        return {
            "test_status": "failed",
            "error": str(e),
            "conversational_flow_working": False
        }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": f"Path {request.url.path} not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )

# Main execution
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"🚀 Starting Conversational AI Event Planner on port {port}")
    logger.info(f"📊 Configuration:")
    logger.info(f"   - Real Agents: {USE_REAL_AGENTS}")
    logger.info(f"   - Conversation Mode: {CONVERSATION_MODE}")
    logger.info(f"   - LLM Provider: {LLM_PROVIDER}")
    logger.info(f"   - Google Model: {GOOGLE_MODEL}")
    logger.info(f"   - Conversational Available: {CONVERSATIONAL_AVAILABLE}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
