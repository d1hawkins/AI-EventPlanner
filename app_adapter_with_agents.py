# This file exists to provide the 'app' object that Azure is looking for
# It creates a simple WSGI app that serves static files from the saas directory
# and routes API requests to the appropriate handlers
# This version also integrates with the real agent implementation

import os
import mimetypes
import json
import sys
import importlib
import traceback
from datetime import datetime

# Add the current directory and parent directories to the path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.dirname(current_dir))
sys.path.insert(0, os.path.join(current_dir, 'app'))

# Add wwwroot directory to path for Azure deployment
wwwroot_dir = '/home/site/wwwroot'
if os.path.exists(wwwroot_dir):
    sys.path.insert(0, wwwroot_dir)
    sys.path.insert(0, os.path.join(wwwroot_dir, 'app'))

# Define variables for agent functions
get_agent_response = None
get_conversation_history = None
list_conversations = None
delete_conversation = None
get_agent_factory = None
get_db = None
get_tenant_id = None
REAL_AGENTS_AVAILABLE = False

# Try to import the agent router functions
try:
    # Try all possible import paths
    import_paths = [
        # Direct import
        {
            'router': 'agents.agent_router',
            'factory': 'agents.agent_factory',
            'session': 'db.session',
            'tenant': 'middleware.tenant'
        },
        # With app prefix
        {
            'router': 'app.agents.agent_router',
            'factory': 'app.agents.agent_factory',
            'session': 'app.db.session',
            'tenant': 'app.middleware.tenant'
        },
        # From wwwroot
        {
            'router': 'app_adapter.app.agents.agent_router',
            'factory': 'app_adapter.app.agents.agent_factory',
            'session': 'app_adapter.app.db.session',
            'tenant': 'app_adapter.app.middleware.tenant'
        }
    ]
    
    imported = False
    for path in import_paths:
        try:
            router_module = __import__(path['router'], fromlist=['get_agent_response', 'get_conversation_history', 'list_conversations', 'delete_conversation'])
            factory_module = __import__(path['factory'], fromlist=['get_agent_factory'])
            session_module = __import__(path['session'], fromlist=['get_db'])
            tenant_module = __import__(path['tenant'], fromlist=['get_tenant_id'])
            
            # Get the functions from the modules
            get_agent_response = getattr(router_module, 'get_agent_response')
            get_conversation_history = getattr(router_module, 'get_conversation_history')
            list_conversations = getattr(router_module, 'list_conversations')
            delete_conversation = getattr(router_module, 'delete_conversation')
            get_agent_factory = getattr(factory_module, 'get_agent_factory')
            get_db = getattr(session_module, 'get_db')
            get_tenant_id = getattr(tenant_module, 'get_tenant_id')
            
            # Import Session class
            from sqlalchemy.orm import Session
            
            REAL_AGENTS_AVAILABLE = True
            print(f"Successfully imported real agent implementation using path: {path['router']}")
            imported = True
            break
        except ImportError as e:
            print(f"Import failed for path {path['router']}: {str(e)}")
            continue
    
    if not imported:
        raise ImportError("Could not import agent modules from any known path")
            
except ImportError as e:
    REAL_AGENTS_AVAILABLE = False
    print(f"Failed to import real agent implementation: {str(e)}")
    traceback.print_exc()

def app(environ, start_response):
    """
    Simple WSGI application that serves static files from the saas directory
    and routes API requests to the appropriate handlers.
    """
    # Get the requested path
    path_info = environ.get('PATH_INFO', '/')
    
    # Route API requests
    if path_info.startswith('/api/') or path_info.startswith('/auth/') or path_info.startswith('/subscription/'):
        # For agent-related endpoints, try to use the real implementation if available
        if REAL_AGENTS_AVAILABLE and path_info.startswith('/api/agents/'):
            try:
                # Handle agent-related endpoints
                if path_info == '/api/agents/available':
                    # Get available agents
                    # Create a database session
                    db = next(get_db())
                    
                    # Get tenant ID from request
                    organization_id = get_tenant_id(environ) if environ else None
                    
                    # Get agent factory with tenant context
                    agent_factory = get_agent_factory(db=db, organization_id=organization_id)
                    
                    # Get available agents
                    from app.agents.api_router import AGENT_METADATA, SUBSCRIPTION_TIERS
                    
                    # Default to enterprise tier to make all agents available
                    subscription_tier = "enterprise"
                    tier_level = SUBSCRIPTION_TIERS.get(subscription_tier, 2)
                    
                    # Build list of agents with availability information
                    agents = []
                    for agent_type, metadata in AGENT_METADATA.items():
                        agent_tier = metadata["subscription_tier"]
                        agent_tier_level = SUBSCRIPTION_TIERS.get(agent_tier, 0)
                        
                        # Check if agent is available for current subscription
                        available = tier_level >= agent_tier_level
                        
                        agents.append({
                            "agent_type": agent_type,
                            "name": metadata["name"],
                            "description": metadata["description"],
                            "icon": metadata["icon"],
                            "available": available,
                            "subscription_tier": agent_tier
                        })
                    
                    # Prepare response
                    response_data = {
                        "agents": agents,
                        "organization_id": organization_id,
                        "subscription_tier": subscription_tier
                    }
                    
                    # Convert to JSON
                    response_json = json.dumps(response_data).encode('utf-8')
                    
                    # Send the response
                    status = '200 OK'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
                elif path_info.startswith('/api/agents/conversations/') and environ.get('REQUEST_METHOD') == 'GET':
                    # Get conversation history
                    conversation_id = path_info.split('/')[-1]
                    
                    # Create a database session
                    db = next(get_db())
                    
                    # Get tenant ID from request
                    organization_id = get_tenant_id(environ) if environ else None
                    
                    # Get conversation history
                    result = get_conversation_history(
                        conversation_id=conversation_id,
                        request=None,
                        db=db,
                        current_user_id=1  # Default user ID
                    )
                    
                    # Convert to JSON
                    response_json = json.dumps(result).encode('utf-8')
                    
                    # Send the response
                    status = '200 OK'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
                elif path_info == '/api/agents/conversations' and environ.get('REQUEST_METHOD') == 'GET':
                    # List conversations
                    # Create a database session
                    db = next(get_db())
                    
                    # Get tenant ID from request
                    organization_id = get_tenant_id(environ) if environ else None
                    
                    # List conversations
                    result = list_conversations(
                        limit=100,
                        offset=0,
                        request=None,
                        db=db,
                        current_user_id=1  # Default user ID
                    )
                    
                    # Convert to JSON
                    response_json = json.dumps(result).encode('utf-8')
                    
                    # Send the response
                    status = '200 OK'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
                elif path_info.startswith('/api/agents/conversations/') and environ.get('REQUEST_METHOD') == 'DELETE':
                    # Delete conversation
                    conversation_id = path_info.split('/')[-1]
                    
                    # Create a database session
                    db = next(get_db())
                    
                    # Get tenant ID from request
                    organization_id = get_tenant_id(environ) if environ else None
                    
                    # Delete conversation
                    result = delete_conversation(
                        conversation_id=conversation_id,
                        request=None,
                        db=db,
                        current_user_id=1  # Default user ID
                    )
                    
                    # Convert to JSON
                    response_json = json.dumps(result).encode('utf-8')
                    
                    # Send the response
                    status = '200 OK'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
                elif path_info == '/api/agents/message' and environ.get('REQUEST_METHOD') == 'POST':
                    # Get the request body
                    try:
                        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
                    except (ValueError):
                        request_body_size = 0
                        
                    request_body = environ['wsgi.input'].read(request_body_size)
                    
                    # Parse the request body
                    try:
                        request_data = json.loads(request_body)
                        agent_type = request_data.get('agent_type', 'coordinator')
                        message = request_data.get('message', '')
                        conversation_id = request_data.get('conversation_id')
                    except:
                        agent_type = 'coordinator'
                        message = ''
                        conversation_id = None
                    
                    # Create a database session
                    db = next(get_db())
                    
                    # Get agent response
                    result = get_agent_response(
                        agent_type=agent_type,
                        message=message,
                        conversation_id=conversation_id,
                        request=None,
                        db=db,
                        current_user_id=1  # Default user ID
                    )
                    
                    # Convert to JSON
                    response_json = json.dumps(result).encode('utf-8')
                    
                    # Send the response
                    status = '200 OK'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
                elif path_info == '/api/agents/analytics' and environ.get('REQUEST_METHOD') == 'GET':
                    # Mock response for analytics
                    response_data = {
                        "total_conversations": 0,
                        "conversations_by_agent": [],
                        "messages_by_agent": [],
                        "conversations_by_date": [],
                        "feedback": {
                            "total_count": 0,
                            "average_rating": 0,
                            "distribution": [],
                            "by_agent": []
                        },
                        "organization_id": None
                    }
                    
                    # Convert to JSON
                    response_json = json.dumps(response_data).encode('utf-8')
                    
                    # Send the response
                    status = '200 OK'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
                else:
                    # Default API response for agent endpoints
                    response_data = {"message": "Agent API endpoint not implemented"}
                    response_json = json.dumps(response_data).encode('utf-8')
                    
                    status = '404 Not Found'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
            except Exception as e:
                # Log the error
                print(f"Error in agent endpoint: {str(e)}")
                traceback.print_exc()
                
                # Fall back to mock responses
                print("Falling back to mock responses")
                
                # Continue with mock responses below
        
        # For now, return a mock response for API requests
        if path_info == '/api/agents/available':
            # Mock response for available agents
            response_data = {
                "agents": [
                    {
                        "agent_type": "coordinator",
                        "name": "Event Coordinator",
                        "description": "Orchestrates the event planning process and delegates tasks to specialized agents",
                        "icon": "bi-diagram-3",
                        "available": True,
                        "subscription_tier": "free"
                    },
                    {
                        "agent_type": "resource_planning",
                        "name": "Resource Planner",
                        "description": "Plans and manages resources needed for your event",
                        "icon": "bi-calendar-check",
                        "available": True,
                        "subscription_tier": "free"
                    },
                    {
                        "agent_type": "financial",
                        "name": "Financial Advisor",
                        "description": "Handles budgeting, cost estimation, and financial planning",
                        "icon": "bi-cash-coin",
                        "available": True,
                        "subscription_tier": "professional"
                    },
                    {
                        "agent_type": "stakeholder_management",
                        "name": "Stakeholder Manager",
                        "description": "Manages communication and relationships with event stakeholders",
                        "icon": "bi-people",
                        "available": True,
                        "subscription_tier": "professional"
                    },
                    {
                        "agent_type": "marketing_communications",
                        "name": "Marketing Specialist",
                        "description": "Creates marketing strategies and communication plans",
                        "icon": "bi-megaphone",
                        "available": True,
                        "subscription_tier": "professional"
                    },
                    {
                        "agent_type": "project_management",
                        "name": "Project Manager",
                        "description": "Manages timelines, tasks, and overall project execution",
                        "icon": "bi-kanban",
                        "available": True,
                        "subscription_tier": "professional"
                    },
                    {
                        "agent_type": "analytics",
                        "name": "Analytics Expert",
                        "description": "Analyzes event data and provides insights for improvement",
                        "icon": "bi-graph-up",
                        "available": True,
                        "subscription_tier": "enterprise"
                    },
                    {
                        "agent_type": "compliance_security",
                        "name": "Compliance & Security Specialist",
                        "description": "Ensures event compliance with regulations and security requirements",
                        "icon": "bi-shield-check",
                        "available": True,
                        "subscription_tier": "enterprise"
                    }
                ],
                "organization_id": None,
                "subscription_tier": "enterprise"  # Set to enterprise to make all agents available
            }
            
            # Convert to JSON
            response_json = json.dumps(response_data).encode('utf-8')
            
            # Send the response
            status = '200 OK'
            headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
            start_response(status, headers)
            return [response_json]
        elif path_info.startswith('/api/agents/conversations'):
            # Mock response for conversations
            response_data = {
                "conversations": [],
                "total": 0,
                "limit": 100,
                "offset": 0,
                "organization_id": None
            }
            
            # Convert to JSON
            response_json = json.dumps(response_data).encode('utf-8')
            
            # Send the response
            status = '200 OK'
            headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
            start_response(status, headers)
            return [response_json]
        elif path_info == '/api/agents/analytics':
            # Mock response for analytics
            response_data = {
                "total_conversations": 0,
                "conversations_by_agent": [],
                "messages_by_agent": [],
                "conversations_by_date": [],
                "feedback": {
                    "total_count": 0,
                    "average_rating": 0,
                    "distribution": [],
                    "by_agent": []
                },
                "organization_id": None
            }
            
            # Convert to JSON
            response_json = json.dumps(response_data).encode('utf-8')
            
            # Send the response
            status = '200 OK'
            headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
            start_response(status, headers)
            return [response_json]
        elif path_info == '/api/agents/message' and environ.get('REQUEST_METHOD') == 'POST':
            # Get the request body
            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            except (ValueError):
                request_body_size = 0
                
            request_body = environ['wsgi.input'].read(request_body_size)
            
            # Parse the request body
            try:
                request_data = json.loads(request_body)
                agent_type = request_data.get('agent_type', 'coordinator')
                message = request_data.get('message', '')
                conversation_id = request_data.get('conversation_id', 'new_conversation_id')
            except:
                agent_type = 'coordinator'
                message = ''
                conversation_id = 'new_conversation_id'
            
            # Mock response for agent message
            response_data = {
                "response": f"This is a mock response from the {agent_type} agent. You said: {message}",
                "conversation_id": conversation_id,
                "agent_type": agent_type,
                "organization_id": None
            }
            
            # Convert to JSON
            response_json = json.dumps(response_data).encode('utf-8')
            
            # Send the response
            status = '200 OK'
            headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
            start_response(status, headers)
            return [response_json]
        else:
            # Default API response
            response_data = {"message": "API endpoint not implemented"}
            response_json = json.dumps(response_data).encode('utf-8')
            
            status = '404 Not Found'
            headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
            start_response(status, headers)
            return [response_json]
    elif path_info == '/health':
        # Health check endpoint
        response_data = {
            "status": "healthy",
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "real_agents_available": REAL_AGENTS_AVAILABLE
        }
        
        # Convert to JSON
        response_json = json.dumps(response_data).encode('utf-8')
        
        # Send the response
        status = '200 OK'
        headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
        start_response(status, headers)
        return [response_json]
    else:
        # Serve static files
        # Default to index.html for root or /saas/ paths
        if path_info == '/' or path_info == '/saas/' or path_info == '/saas':
            path_info = '/index.html'
        elif path_info.startswith('/saas/'):
            # Remove the /saas/ prefix
            path_info = path_info[6:]
        
        # Construct the file path
        file_path = os.path.join(os.path.dirname(__file__), 'app', 'web', 'static', 'saas', path_info.lstrip('/'))
        
        # Check if the file exists
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # Determine the content type
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            # Read the file
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Send the response
            status = '200 OK'
            headers = [('Content-type', content_type), ('Content-Length', str(len(file_content)))]
            start_response(status, headers)
            return [file_content]
        else:
            # File not found, serve the index.html file for SPA routing
            index_path = os.path.join(os.path.dirname(__file__), 'app', 'web', 'static', 'saas', 'index.html')
            
            if os.path.exists(index_path):
                with open(index_path, 'rb') as f:
                    index_content = f.read()
                
                status = '200 OK'
                headers = [('Content-type', 'text/html'), ('Content-Length', str(len(index_content)))]
                start_response(status, headers)
                return [index_content]
            else:
                # If index.html doesn't exist, return a 404
                status = '404 Not Found'
                response = b'File not found'
                headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(response)))]
                start_response(status, headers)
                return [response]
