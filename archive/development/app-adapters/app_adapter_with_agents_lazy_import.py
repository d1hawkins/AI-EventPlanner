# This file exists to provide the 'app' object that Azure is looking for
# It creates a simple WSGI app that serves static files from the saas directory
# and routes API requests to the appropriate handlers
# This version uses lazy imports to avoid dependency issues during startup

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
    sys.path.insert(0, os.path.join(wwwroot_dir, 'app', 'agents'))
    sys.path.insert(0, os.path.join(wwwroot_dir, 'app', 'graphs'))
    sys.path.insert(0, os.path.join(wwwroot_dir, 'app', 'tools'))
    sys.path.insert(0, os.path.join(wwwroot_dir, 'app', 'utils'))
    sys.path.insert(0, os.path.join(wwwroot_dir, 'app', 'db'))
    sys.path.insert(0, os.path.join(wwwroot_dir, 'app', 'middleware'))
    sys.path.insert(0, os.path.join(wwwroot_dir, 'app', 'services'))

# Also add local app subdirectories
sys.path.insert(0, os.path.join(current_dir, 'app', 'agents'))
sys.path.insert(0, os.path.join(current_dir, 'app', 'graphs'))
sys.path.insert(0, os.path.join(current_dir, 'app', 'tools'))
sys.path.insert(0, os.path.join(current_dir, 'app', 'utils'))
sys.path.insert(0, os.path.join(current_dir, 'app', 'db'))
sys.path.insert(0, os.path.join(current_dir, 'app', 'middleware'))
sys.path.insert(0, os.path.join(current_dir, 'app', 'services'))

# Print the Python path for debugging
print("Python path:")
for p in sys.path:
    print(f"  {p}")

# Global variables for lazy-loaded agent functions
_agent_functions_cache = None
_real_agents_available = None

def get_agent_functions():
    """Lazy load agent functions only when needed."""
    global _agent_functions_cache, _real_agents_available
    
    if _agent_functions_cache is not None:
        return _agent_functions_cache, _real_agents_available
    
    print("🔄 Lazy loading agent modules...")
    
    # Initialize default values
    get_agent_response = None
    get_conversation_history = None
    list_conversations = None
    delete_conversation = None
    get_agent_factory = None
    get_db = None
    get_tenant_id = None
    real_agents_available = False
    
    try:
        # List all directories in app to help with debugging
        app_dir = os.path.join(current_dir, 'app')
        if os.path.exists(app_dir):
            print("App directory contents:")
            for item in os.listdir(app_dir):
                print(f"  {item}")
        
        # Try all possible import paths
        import_paths = [
            # Direct import with app prefix
            {
                'router': 'app.agents.api_router',
                'factory': 'app.agents.agent_factory',
                'session': 'app.db.session',
                'tenant': 'app.middleware.tenant'
            },
            # Direct module imports (when modules are in sys.path)
            {
                'router': 'api_router',
                'factory': 'agent_factory',
                'session': 'session',
                'tenant': 'tenant'
            },
            # Without app prefix
            {
                'router': 'agents.api_router',
                'factory': 'agents.agent_factory',
                'session': 'db.session',
                'tenant': 'middleware.tenant'
            }
        ]
        
        imported = False
        for path in import_paths:
            try:
                print(f"Trying import path: {path['router']}")
                router_module = importlib.import_module(path['router'])
                factory_module = importlib.import_module(path['factory'])
                session_module = importlib.import_module(path['session'])
                tenant_module = importlib.import_module(path['tenant'])
                
                # Get the functions from the modules
                get_agent_response = getattr(router_module, 'get_agent_response', None)
                get_conversation_history = getattr(router_module, 'get_conversation_history', None)
                list_conversations = getattr(router_module, 'list_conversations', None)
                delete_conversation = getattr(router_module, 'delete_conversation', None)
                get_agent_factory = getattr(factory_module, 'get_agent_factory', None)
                get_db = getattr(session_module, 'get_db', None)
                get_tenant_id = getattr(tenant_module, 'get_tenant_id', None)
                
                # Check if we got all required functions
                if all([get_agent_response, get_agent_factory, get_db]):
                    real_agents_available = True
                    print(f"✅ Successfully imported real agent implementation using path: {path['router']}")
                    imported = True
                    break
                else:
                    print(f"Missing required functions from {path['router']}")
                    continue
                    
            except ImportError as e:
                print(f"Import failed for path {path['router']}: {str(e)}")
                continue
            except Exception as e:
                print(f"Unexpected error for path {path['router']}: {str(e)}")
                continue
        
        if not imported:
            print("⚠️ Could not import agent modules from any known path - will use mock responses")
            real_agents_available = False
                
    except Exception as e:
        real_agents_available = False
        print(f"⚠️ Unexpected error during lazy agent import: {str(e)}")
        print("Will continue with mock responses")
        traceback.print_exc()
    
    # Cache the results
    _agent_functions_cache = {
        'get_agent_response': get_agent_response,
        'get_conversation_history': get_conversation_history,
        'list_conversations': list_conversations,
        'delete_conversation': delete_conversation,
        'get_agent_factory': get_agent_factory,
        'get_db': get_db,
        'get_tenant_id': get_tenant_id
    }
    _real_agents_available = real_agents_available
    
    print(f"🔧 Agent system status: {'REAL AGENTS' if real_agents_available else 'MOCK RESPONSES'}")
    
    return _agent_functions_cache, real_agents_available

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
        if path_info.startswith('/api/agents/'):
            # Lazy load agent functions only when needed
            agent_functions, real_agents_available = get_agent_functions()
            
            if real_agents_available and path_info == '/api/agents/message' and environ.get('REQUEST_METHOD') == 'POST':
                try:
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
                    db = next(agent_functions['get_db']())
                    
                    # Create a mock request object for tenant context
                    class MockRequest:
                        def __init__(self, environ):
                            self.headers = {}
                            # Extract headers from environ
                            for key, value in environ.items():
                                if key.startswith('HTTP_'):
                                    header_name = key[5:].replace('_', '-').lower()
                                    self.headers[header_name] = value
                            
                            # Add tenant headers that the middleware expects
                            self.headers['x-tenant-id'] = '1'
                            self.headers['x-organization-id'] = '1'
                            
                            # Create a state object that mimics FastAPI request.state
                            class MockState:
                                def __init__(self):
                                    self.tenant_id = 1
                                    self.db = None
                            
                            self.state = MockState()
                            self.organization_id = 1
                            self.url = environ.get('REQUEST_URI', '/')
                            self.method = environ.get('REQUEST_METHOD', 'GET')
                            self.path_params = {}
                    
                    mock_request = MockRequest(environ)
                    
                    # Get agent response using the real implementation
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        result = loop.run_until_complete(agent_functions['get_agent_response'](
                            agent_type=agent_type,
                            message=message,
                            conversation_id=conversation_id,
                            request=mock_request,
                            db=db,
                            current_user_id=1
                        ))
                        
                        # Add flag to indicate real agent was used
                        result["using_real_agent"] = True
                        
                        # Convert to JSON
                        response_json = json.dumps(result).encode('utf-8')
                        
                        # Send the response
                        status = '200 OK'
                        headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                        start_response(status, headers)
                        return [response_json]
                    finally:
                        loop.close()
                        
                except Exception as e:
                    # Log the error
                    print(f"Error in real agent endpoint: {str(e)}")
                    traceback.print_exc()
                    
                    # Fall back to mock responses
                    print("Falling back to mock responses")
                    real_agents_available = False
        
        # Handle /api/agents/available endpoint
        if path_info == '/api/agents/available' and environ.get('REQUEST_METHOD') == 'GET':
            # Get real agents status (lazy load if needed)
            _, real_agents_available = get_agent_functions()
            
            # Response for available agents with real agent flag
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
                "using_real_agent": real_agents_available
            }
            
            # Convert to JSON
            response_json = json.dumps(response_data).encode('utf-8')
            
            # Send the response
            status = '200 OK'
            headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
            start_response(status, headers)
            return [response_json]
        
        # Handle /api/agents/conversations endpoint
        elif path_info == '/api/agents/conversations' and environ.get('REQUEST_METHOD') == 'GET':
            # Get real agents status (lazy load if needed)
            _, real_agents_available = get_agent_functions()
            
            # Mock response for conversation list
            response_data = {
                "conversations": [
                    {
                        "conversation_id": "conv_1",
                        "agent_type": "coordinator",
                        "preview": "I need help planning a corporate conference...",
                        "timestamp": "2025-06-15T18:30:00Z"
                    },
                    {
                        "conversation_id": "conv_2",
                        "agent_type": "financial",
                        "preview": "What's the budget for catering?",
                        "timestamp": "2025-06-15T17:45:00Z"
                    }
                ],
                "using_real_agent": real_agents_available
            }
            
            # Convert to JSON
            response_json = json.dumps(response_data).encode('utf-8')
            
            # Send the response
            status = '200 OK'
            headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
            start_response(status, headers)
            return [response_json]
        
        # Handle /api/events endpoint
        elif path_info == '/api/events' and environ.get('REQUEST_METHOD') == 'GET':
            # Mock response for events
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
                ]
            }
            
            # Convert to JSON
            response_json = json.dumps(response_data).encode('utf-8')
            
            # Send the response
            status = '200 OK'
            headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
            start_response(status, headers)
            return [response_json]
        
        # Mock responses for API requests when real agents are not available
        elif path_info == '/api/agents/message' and environ.get('REQUEST_METHOD') == 'POST':
            # Get real agents status (lazy load if needed)
            _, real_agents_available = get_agent_functions()
            
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
                "response": f"This is a {'real' if real_agents_available else 'mock'} response from the {agent_type} agent. You said: {message}",
                "conversation_id": conversation_id,
                "agent_type": agent_type,
                "organization_id": None,
                "using_real_agent": real_agents_available
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
        # Get real agents status (lazy load if needed)
        _, real_agents_available = get_agent_functions()
        
        # Health check endpoint
        response_data = {
            "status": "healthy",
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "real_agents_available": real_agents_available
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
