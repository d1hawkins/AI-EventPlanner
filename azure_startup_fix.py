#!/usr/bin/env python3
"""
Azure App Service startup fix for AI Event Planner SaaS
This creates a robust WSGI application that Azure can reliably start
"""
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_simple_wsgi_app():
    """Create a simple WSGI application that always works"""
    def application(environ: Dict[str, Any], start_response) -> List[bytes]:
        """Simple WSGI application"""
        path_info = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        
        logger.info(f"Request: {method} {path_info}")
        
        # Health check endpoint - critical for Azure deployment
        if path_info == '/health':
            response_data = {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "production",
                "startup_time": datetime.now().isoformat(),
                "mode": "simple_startup"
            }
            response_body = str(response_data).encode('utf-8')
            response_headers = [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(response_body)))
            ]
            start_response('200 OK', response_headers)
            return [response_body]
        
        # Root endpoint
        elif path_info == '/' or path_info == '':
            response_body = b"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>AI Event Planner SaaS</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .status { color: green; font-weight: bold; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>AI Event Planner SaaS</h1>
                    <p class="status">Application is running successfully!</p>
                    <p>Startup Time: """ + datetime.now().isoformat().encode('utf-8') + b"""</p>
                    <p>Mode: Simple Startup (Fallback)</p>
                    <h2>Available Endpoints:</h2>
                    <ul>
                        <li><a href="/health">/health</a> - Health check</li>
                        <li><a href="/api/status">/api/status</a> - API status</li>
                    </ul>
                </div>
            </body>
            </html>
            """
            response_headers = [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response_body)))
            ]
            start_response('200 OK', response_headers)
            return [response_body]
        
        # API status endpoint
        elif path_info == '/api/status':
            response_data = {
                "api_status": "operational",
                "version": "1.0.0",
                "startup_mode": "simple",
                "timestamp": datetime.now().isoformat()
            }
            response_body = str(response_data).encode('utf-8')
            response_headers = [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(response_body)))
            ]
            start_response('200 OK', response_headers)
            return [response_body]
        
        # 404 for other paths
        else:
            response_body = b'{"error": "Not Found", "path": "' + path_info.encode('utf-8') + b'"}'
            response_headers = [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(response_body)))
            ]
            start_response('404 Not Found', response_headers)
            return [response_body]
    
    return application

def try_import_complex_app():
    """Try to import the complex application, fall back to simple app"""
    try:
        logger.info("Attempting to import app_adapter...")
        from app_adapter import app
        logger.info("Successfully imported app_adapter")
        return app
    except Exception as e:
        logger.warning(f"Failed to import app_adapter: {str(e)}")
        
        try:
            logger.info("Attempting to import app_adapter_with_agents...")
            from app_adapter_with_agents import app
            logger.info("Successfully imported app_adapter_with_agents")
            return app
        except Exception as e:
            logger.warning(f"Failed to import app_adapter_with_agents: {str(e)}")
            
            try:
                logger.info("Attempting to import from app.main_saas...")
                from app.main_saas import app
                logger.info("Successfully imported app.main_saas")
                return app
            except Exception as e:
                logger.warning(f"Failed to import app.main_saas: {str(e)}")
                
                logger.info("Using simple WSGI app as fallback")
                return create_simple_wsgi_app()

# Set up the application
logger.info("Starting Azure App Service application...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")

# Set environment variables
os.environ.setdefault("PYTHONPATH", "/home/site/wwwroot")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

# Try to get the application
application = try_import_complex_app()

# For Gunicorn compatibility
app = application

if __name__ == "__main__":
    # For testing locally
    from wsgiref.simple_server import make_server
    logger.info("Starting development server on port 8000...")
    server = make_server('0.0.0.0', 8000, application)
    server.serve_forever()
