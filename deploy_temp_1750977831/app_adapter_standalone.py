#!/usr/bin/env python3
"""
Standalone Azure adapter with embedded agent functionality
This version includes all necessary agent code inline to avoid import issues
"""

import os
import mimetypes
import json
import sys
import traceback
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add paths for Azure deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.dirname(current_dir))

# Azure wwwroot path
wwwroot_dir = '/home/site/wwwroot'
if os.path.exists(wwwroot_dir):
    sys.path.insert(0, wwwroot_dir)

print("🚀 Starting standalone agent adapter...")
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path[:3]}...")

# Environment configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU')
USE_REAL_AGENTS = os.getenv('USE_REAL_AGENTS', 'true').lower() == 'true'
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'google')
GOOGLE_MODEL = os.getenv('GOOGLE_MODEL', 'gemini-2.0-flash')

print(f"USE_REAL_AGENTS: {USE_REAL_AGENTS}")
print(f"LLM_PROVIDER: {LLM_PROVIDER}")
print(f"GOOGLE_MODEL: {GOOGLE_MODEL}")

# Global variables for agent functionality
REAL_AGENTS_AVAILABLE = False
agent_responses = {}

# Embedded agent functionality
class StandaloneAgentFactory:
    """Embedded agent factory to avoid import issues"""
    
    def __init__(self):
        self.google_client = None
        self._initialize_google_client()
    
    def _initialize_google_client(self):
        """Initialize Google Generative AI client"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            self.google_client = genai.GenerativeModel(GOOGLE_MODEL)
            print("✅ Google Generative AI client initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Google client: {e}")
            return False
    
    async def get_agent_response(self, agent_type: str, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get response from the specified agent"""
        try:
            if not self.google_client:
                raise Exception("Google client not initialized")
            
            # Agent-specific prompts
            agent_prompts = {
                "coordinator": "You are an Event Coordinator AI. Help plan and coordinate events efficiently. Provide detailed, actionable advice.",
                "resource_planning": "You are a Resource Planning AI. Help identify, allocate, and manage resources for events.",
                "financial": "You are a Financial Planning AI. Help with budgeting, cost estimation, and financial planning for events.",
                "stakeholder_management": "You are a Stakeholder Management AI. Help identify, engage, and communicate with event stakeholders.",
                "marketing_communications": "You are a Marketing Communications AI. Help promote events and create effective communication materials.",
                "project_management": "You are a Project Management AI. Help plan, execute, and track events as projects.",
                "analytics": "You are an Analytics AI. Help collect, analyze, and interpret event-related data.",
                "compliance_security": "You are a Compliance & Security AI. Ensure events meet legal requirements and security standards."
            }
            
            system_prompt = agent_prompts.get(agent_type, agent_prompts["coordinator"])
            full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
            
            # Generate response using Google Gemini
            response = await asyncio.to_thread(
                self.google_client.generate_content,
                full_prompt
            )
            
            agent_response = response.text if response.text else "I'm here to help with your event planning needs."
            
            # Generate conversation ID if not provided
            if not conversation_id:
                conversation_id = f"conv_{agent_type}_{int(datetime.now().timestamp())}"
            
            return {
                "response": agent_response,
                "conversation_id": conversation_id,
                "agent_type": agent_type,
                "organization_id": None,
                "using_real_agent": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error in agent response: {e}")
            traceback.print_exc()
            
            # Fallback response
            return {
                "response": f"I'm the {agent_type} agent. I encountered an issue but I'm here to help with your event planning. Could you please rephrase your question?",
                "conversation_id": conversation_id or f"conv_{agent_type}_fallback",
                "agent_type": agent_type,
                "organization_id": None,
                "using_real_agent": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Initialize the standalone agent factory
try:
    agent_factory = StandaloneAgentFactory()
    REAL_AGENTS_AVAILABLE = True
    print("✅ Standalone agent factory initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize agent factory: {e}")
    agent_factory = None
    REAL_AGENTS_AVAILABLE = False

def app(environ, start_response):
    """
    WSGI application with embedded agent functionality
    """
    path_info = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    print(f"Request: {method} {path_info}")
    
    # Health check endpoint
    if path_info == '/health':
        response_data = {
            "status": "healthy",
            "version": "standalone_v1",
            "real_agents_available": REAL_AGENTS_AVAILABLE,
            "google_api_configured": bool(GOOGLE_API_KEY),
            "environment": {
                "USE_REAL_AGENTS": USE_REAL_AGENTS,
                "LLM_PROVIDER": LLM_PROVIDER,
                "GOOGLE_MODEL": GOOGLE_MODEL
            },
            "timestamp": datetime.now().isoformat()
        }
        
        response_json = json.dumps(response_data, indent=2).encode('utf-8')
        status = '200 OK'
        headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
        start_response(status, headers)
        return [response_json]
    
    # Agent message endpoint
    elif path_info == '/api/agents/message' and method == 'POST':
        try:
            # Get request body
            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            except ValueError:
                request_body_size = 0
            
            request_body = environ['wsgi.input'].read(request_body_size)
            
            # Parse request
            try:
                request_data = json.loads(request_body)
                agent_type = request_data.get('agent_type', 'coordinator')
                message = request_data.get('message', '')
                conversation_id = request_data.get('conversation_id')
            except:
                agent_type = 'coordinator'
                message = 'Hello'
                conversation_id = None
            
            print(f"Agent request: {agent_type} - {message[:50]}...")
            
            # Get agent response
            if REAL_AGENTS_AVAILABLE and agent_factory:
                # Use real agent
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        agent_factory.get_agent_response(agent_type, message, conversation_id)
                    )
                    print("✅ Real agent response generated")
                finally:
                    loop.close()
            else:
                # Fallback mock response
                result = {
                    "response": f"Mock response from {agent_type} agent: {message}",
                    "conversation_id": conversation_id or f"mock_conv_{int(datetime.now().timestamp())}",
                    "agent_type": agent_type,
                    "organization_id": None,
                    "using_real_agent": False,
                    "timestamp": datetime.now().isoformat()
                }
                print("⚠️ Using mock agent response")
            
            response_json = json.dumps(result).encode('utf-8')
            status = '200 OK'
            headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
            start_response(status, headers)
            return [response_json]
            
        except Exception as e:
            print(f"❌ Error in agent message endpoint: {e}")
            traceback.print_exc()
            
            error_response = {
                "error": "Internal server error",
                "message": str(e),
                "using_real_agent": False,
                "timestamp": datetime.now().isoformat()
            }
            
            response_json = json.dumps(error_response).encode('utf-8')
            status = '500 Internal Server Error'
            headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
            start_response(status, headers)
            return [response_json]
    
    # Available agents endpoint
    elif path_info == '/api/agents/available' and method == 'GET':
        response_data = {
            "agents": [
                {
                    "agent_type": "coordinator",
                    "name": "Event Coordinator",
                    "description": "Orchestrates the entire event planning process and delegates tasks to specialized agents.",
                    "icon": "bi-diagram-3",
                    "subscription_tier": "free",
                    "available": True
                },
                {
                    "agent_type": "resource_planning",
                    "name": "Resource Planner",
                    "description": "Helps you identify, allocate, and manage resources needed for your event.",
                    "icon": "bi-boxes",
                    "subscription_tier": "free",
                    "available": True
                },
                {
                    "agent_type": "financial",
                    "name": "Financial Advisor",
                    "description": "Handles budgeting, cost estimation, and financial planning for your event.",
                    "icon": "bi-calculator",
                    "subscription_tier": "professional",
                    "available": True
                },
                {
                    "agent_type": "stakeholder_management",
                    "name": "Stakeholder Manager",
                    "description": "Helps you identify, engage, and communicate with event stakeholders.",
                    "icon": "bi-people",
                    "subscription_tier": "professional",
                    "available": True
                },
                {
                    "agent_type": "marketing_communications",
                    "name": "Marketing Specialist",
                    "description": "Helps you promote your event and create effective communication materials.",
                    "icon": "bi-megaphone",
                    "subscription_tier": "professional",
                    "available": True
                },
                {
                    "agent_type": "project_management",
                    "name": "Project Manager",
                    "description": "Helps you plan, execute, and track your event as a project.",
                    "icon": "bi-kanban",
                    "subscription_tier": "professional",
                    "available": True
                },
                {
                    "agent_type": "analytics",
                    "name": "Analytics Expert",
                    "description": "Helps you collect, analyze, and interpret data related to your event.",
                    "icon": "bi-graph-up",
                    "subscription_tier": "enterprise",
                    "available": True
                },
                {
                    "agent_type": "compliance_security",
                    "name": "Compliance & Security Specialist",
                    "description": "Ensures your event meets legal requirements and security standards.",
                    "icon": "bi-shield-check",
                    "subscription_tier": "enterprise",
                    "available": True
                }
            ],
            "subscription_tier": "professional",
            "using_real_agent": REAL_AGENTS_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        }
        
        response_json = json.dumps(response_data).encode('utf-8')
        status = '200 OK'
        headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
        start_response(status, headers)
        return [response_json]
    
    # Conversations endpoint
    elif path_info == '/api/agents/conversations' and method == 'GET':
        response_data = {
            "conversations": [
                {
                    "conversation_id": "conv_1",
                    "agent_type": "coordinator",
                    "preview": "I need help planning a corporate conference...",
                    "timestamp": "2025-06-26T18:30:00Z"
                },
                {
                    "conversation_id": "conv_2",
                    "agent_type": "financial",
                    "preview": "What's the budget for catering?",
                    "timestamp": "2025-06-26T17:45:00Z"
                }
            ],
            "using_real_agent": REAL_AGENTS_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        }
        
        response_json = json.dumps(response_data).encode('utf-8')
        status = '200 OK'
        headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
        start_response(status, headers)
        return [response_json]
    
    # Events endpoint
    elif path_info == '/api/events' and method == 'GET':
        response_data = {
            "events": [
                {
                    "id": 1,
                    "title": "Tech Conference 2025",
                    "description": "Annual technology conference",
                    "date": "2025-09-15"
                },
                {
                    "id": 2,
                    "title": "Company Retreat",
                    "description": "Team building retreat",
                    "date": "2025-08-20"
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        response_json = json.dumps(response_data).encode('utf-8')
        status = '200 OK'
        headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
        start_response(status, headers)
        return [response_json]
    
    # Static file serving
    else:
        # Default to index.html for root or /saas/ paths
        if path_info == '/' or path_info == '/saas/' or path_info == '/saas':
            path_info = '/index.html'
        elif path_info.startswith('/saas/'):
            path_info = path_info[6:]
        
        # Try to serve static files from app/web/static/saas
        file_path = os.path.join(current_dir, 'app', 'web', 'static', 'saas', path_info.lstrip('/'))
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            status = '200 OK'
            headers = [('Content-type', content_type), ('Content-Length', str(len(file_content)))]
            start_response(status, headers)
            return [file_content]
        else:
            # Serve a simple HTML page if static files not found
            html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Event Planner</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .status { padding: 20px; border-radius: 8px; margin: 20px 0; }
        .success { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .info { background-color: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
    </style>
</head>
<body>
    <h1>🤖 AI Event Planner</h1>
    <div class="status success">
        <h3>✅ Application Status: Running</h3>
        <p>Real Agents: <strong>""" + ("Enabled" if REAL_AGENTS_AVAILABLE else "Disabled") + """</strong></p>
        <p>LLM Provider: <strong>""" + LLM_PROVIDER + """</strong></p>
        <p>Model: <strong>""" + GOOGLE_MODEL + """</strong></p>
    </div>
    <div class="status info">
        <h3>🔗 API Endpoints</h3>
        <ul>
            <li><a href="/health">/health</a> - Health check</li>
            <li><a href="/api/agents/available">/api/agents/available</a> - Available agents</li>
            <li><a href="/api/agents/conversations">/api/agents/conversations</a> - Conversations</li>
            <li><a href="/api/events">/api/events</a> - Events</li>
        </ul>
    </div>
    <div class="status info">
        <h3>🧪 Test Agent</h3>
        <p>Send a POST request to <code>/api/agents/message</code> with:</p>
        <pre>{"agent_type": "coordinator", "message": "Hello, help me plan an event"}</pre>
    </div>
</body>
</html>
            """
            
            html_bytes = html_content.encode('utf-8')
            status = '200 OK'
            headers = [('Content-type', 'text/html'), ('Content-Length', str(len(html_bytes)))]
            start_response(status, headers)
            return [html_bytes]

if __name__ == "__main__":
    print("🚀 Starting standalone agent server...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
