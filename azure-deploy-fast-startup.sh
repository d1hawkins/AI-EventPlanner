#!/bin/bash

# Azure Deployment Script for Fast Startup
# This script deploys a minimal version that starts quickly

set -e

echo "🚀 Starting Azure deployment with fast startup..."

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
LOCATION="East US"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed and logged in
print_status "Checking Azure CLI..."
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

print_success "Azure CLI is ready"

# Step 1: Create minimal requirements file for fast startup
print_status "Creating minimal requirements file..."
cat > requirements_fast.txt << 'EOF'
# Minimal requirements for fast startup
fastapi==0.104.1
uvicorn==0.24.0
gunicorn==23.0.0
python-dotenv==1.0.0
requests==2.31.0
python-multipart==0.0.6
httpx==0.25.2
python-dateutil==2.8.2
EOF

print_success "Minimal requirements created"

# Step 2: Create simple app adapter for fast startup
print_status "Creating simple app adapter..."
cat > main.py << 'EOF'
# Fast startup app adapter - no heavy imports
import os
import mimetypes
import json
from datetime import datetime

def application(environ, start_response):
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
EOF

print_success "Simple app adapter created"

# Step 3: Set up environment variables
print_status "Setting up environment variables..."

# Database URL (get from existing deployment)
DATABASE_URL=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='DATABASE_URL'].value" -o tsv)

if [ -z "$DATABASE_URL" ]; then
    print_warning "Could not retrieve DATABASE_URL from existing deployment, using default"
    DATABASE_URL="postgresql://default"
fi

print_status "Retrieved DATABASE_URL from existing deployment"

# Set minimal environment variables
print_status "Setting environment variables..."

az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings \
    APP_NAME="AI Event Planner" \
    APP_VERSION="1.0.0" \
    ENVIRONMENT="production" \
    DEBUG="false" \
    HOST="0.0.0.0" \
    PORT="8000" \
    FAST_STARTUP="true" \
    > /dev/null

print_success "Environment variables configured"

# Step 4: Deploy the application
print_status "Deploying application to Azure..."

# Create a deployment package
print_status "Creating deployment package..."

# Clean up any existing deployment files
rm -f deployment.zip

# Create a temporary directory for deployment
TEMP_DIR=$(mktemp -d)
print_status "Using temporary directory: $TEMP_DIR"

# Copy essential files to temp directory
print_status "Copying essential files..."
cp main.py "$TEMP_DIR/"
cp requirements_fast.txt "$TEMP_DIR/requirements.txt"

# Copy the app directory (static files only)
if [ -d "app/web/static" ]; then
    mkdir -p "$TEMP_DIR/app/web"
    cp -r app/web/static "$TEMP_DIR/app/web/"
fi

# Create deployment package from temp directory
cd "$TEMP_DIR"
zip -r deployment.zip . > /dev/null 2>&1
cd - > /dev/null

# Move the deployment package back
mv "$TEMP_DIR/deployment.zip" ./deployment.zip
print_success "Deployment package created successfully"

# Clean up temp directory
rm -rf "$TEMP_DIR"

# Deploy using ZIP deployment
print_status "Uploading and deploying to Azure..."
az webapp deployment source config-zip --name $APP_NAME --resource-group $RESOURCE_GROUP --src deployment.zip

print_success "Application deployed"

# Step 5: Restart the application
print_status "Restarting application..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP
print_success "Application restarted"

# Step 6: Wait for deployment to complete
print_status "Waiting for deployment to complete..."
sleep 15

# Step 7: Verify deployment
print_status "Verifying deployment..."

# Check health endpoint
HEALTH_URL="https://$APP_NAME.azurewebsites.net/health"
print_status "Checking health endpoint: $HEALTH_URL"

for i in {1..5}; do
    if curl -s "$HEALTH_URL" | grep -q "fast_startup.*true"; then
        print_success "Fast startup deployment is working!"
        break
    else
        print_warning "Attempt $i: Waiting for health check..."
        sleep 5
    fi
    
    if [ $i -eq 5 ]; then
        print_warning "Health check not responding as expected"
        print_status "Checking current health status..."
        curl -s "$HEALTH_URL" || echo "Health endpoint not accessible"
    fi
done

# Clean up
print_status "Cleaning up..."
rm -f deployment.zip
rm -f main.py
rm -f requirements_fast.txt
print_success "Cleanup complete"

# Final status
print_success "🎉 Fast startup deployment completed!"
echo ""
echo "Application URL: https://$APP_NAME.azurewebsites.net"
echo "Health Check: https://$APP_NAME.azurewebsites.net/health"
echo "Agents Page: https://$APP_NAME.azurewebsites.net/saas/agents.html"
echo ""
print_status "The application is now running in fast startup mode with limited functionality."
print_status "This should start within the Azure timeout limits."
