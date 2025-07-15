# Fast startup app adapter - no heavy imports
import os
import mimetypes
import json
from datetime import datetime

def app(environ, start_response):
    """Simple WSGI application for fast startup"""
    path_info = environ.get('PATH_INFO', '/')
    
    # Health check endpoint
    if path_info == '/health':
        response_data = {
            "status": "healthy",
            "version": "1.0.0",
            "environment": "production",
            "startup_time": datetime.now().isoformat(),
            "fast_startup": True
        }
        response_json = json.dumps(response_data).encode('utf-8')
        status = '200 OK'
        headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
        start_response(status, headers)
        return [response_json]
    
    # API endpoints with mock responses
    elif path_info.startswith('/api/'):
        if path_info == '/api/agents/available':
            response_data = {
                "agents": [
                    {
                        "agent_type": "coordinator",
                        "name": "Event Coordinator",
                        "description": "Orchestrates the event planning process",
                        "icon": "bi-diagram-3",
                        "available": True,
                        "subscription_tier": "free"
                    }
                ],
                "fast_startup_mode": True
            }
        elif path_info == '/api/agents/message' and environ.get('REQUEST_METHOD') == 'POST':
            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
                request_body = environ['wsgi.input'].read(request_body_size)
                request_data = json.loads(request_body)
                message = request_data.get('message', '')
            except:
                message = ''
            
            response_data = {
                "response": f"Fast startup mode: Your message '{message}' was received. Full agent functionality will be available after complete deployment.",
                "conversation_id": "fast_startup_conv",
                "agent_type": "coordinator",
                "fast_startup_mode": True
            }
        else:
            response_data = {"message": "Fast startup mode - limited functionality"}
        
        response_json = json.dumps(response_data).encode('utf-8')
        status = '200 OK'
        headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
        start_response(status, headers)
        return [response_json]
    
    # Serve static files
    else:
        if path_info == '/' or path_info == '/saas/' or path_info == '/saas':
            path_info = '/index.html'
        elif path_info.startswith('/saas/'):
            path_info = path_info[6:]
        
        file_path = os.path.join(os.path.dirname(__file__), 'app', 'web', 'static', 'saas', path_info.lstrip('/'))
        
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
            index_path = os.path.join(os.path.dirname(__file__), 'app', 'web', 'static', 'saas', 'index.html')
            if os.path.exists(index_path):
                with open(index_path, 'rb') as f:
                    index_content = f.read()
                status = '200 OK'
                headers = [('Content-type', 'text/html'), ('Content-Length', str(len(index_content)))]
                start_response(status, headers)
                return [index_content]
            else:
                status = '404 Not Found'
                response = b'File not found'
                headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(response)))]
                start_response(status, headers)
                return [response]
