#!/bin/bash

# Azure Deployment Script for Standalone SaaS + Real Agents Solution
# This script deploys app_adapter_standalone.py with full SaaS functionality and real agents

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
LOCATION="East US"
GOOGLE_API_KEY="AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU"

echo -e "${BLUE}🚀 Starting Azure Deployment for Standalone SaaS + Real Agents Solution${NC}"
echo "=================================================="
echo "Resource Group: $RESOURCE_GROUP"
echo "App Name: $APP_NAME"
echo "Location: $LOCATION"
echo "=================================================="

# Function to print status
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

# Check prerequisites
print_status "Checking prerequisites..."
check_command "az"
check_command "zip"

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

print_success "Prerequisites check passed"

# Create deployment package
print_status "Creating deployment package..."

# Create temporary directory for deployment
DEPLOY_DIR="deploy_temp_$(date +%s)"
mkdir -p $DEPLOY_DIR

# Copy the CORRECT standalone adapter file
print_status "Copying standalone adapter..."
cp app_adapter_standalone.py $DEPLOY_DIR/

# Create minimal requirements.txt for standalone deployment
print_status "Creating requirements.txt..."
cat > $DEPLOY_DIR/requirements.txt << 'EOF'
uvicorn[standard]==0.24.0
gunicorn==21.2.0
google-generativeai==0.3.2
python-multipart==0.0.6
python-dotenv==1.0.0
EOF

# Copy SaaS static files
print_status "Copying SaaS website files..."
mkdir -p $DEPLOY_DIR/app/web/static/saas
cp -r app/web/static/saas/* $DEPLOY_DIR/app/web/static/saas/

# Create web.config for Azure with correct module reference
cat > $DEPLOY_DIR/web.config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="python" arguments="-m gunicorn --bind=0.0.0.0:%HTTP_PLATFORM_PORT% --timeout 600 --workers 1 --worker-class uvicorn.workers.UvicornWorker app_adapter_standalone:app" stdoutLogEnabled="true" stdoutLogFile="python.log" startupTimeLimit="120" requestTimeout="00:04:00">
      <environmentVariables>
        <environmentVariable name="PORT" value="%HTTP_PLATFORM_PORT%" />
        <environmentVariable name="USE_REAL_AGENTS" value="true" />
        <environmentVariable name="LLM_PROVIDER" value="google" />
        <environmentVariable name="GOOGLE_MODEL" value="gemini-2.0-flash" />
        <environmentVariable name="GOOGLE_API_KEY" value="AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
EOF

# Create startup script
cat > $DEPLOY_DIR/startup.sh << 'EOF'
#!/bin/bash
echo "Starting Azure standalone deployment..."
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Files in directory:"
ls -la
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting standalone application..."
python -m gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 --worker-class uvicorn.workers.UvicornWorker app_adapter_standalone:app
EOF

chmod +x $DEPLOY_DIR/startup.sh

# Create Procfile for Azure
cat > $DEPLOY_DIR/Procfile << 'EOF'
web: gunicorn --bind=0.0.0.0:$PORT --timeout 600 --workers 1 --worker-class uvicorn.workers.UvicornWorker app_adapter_standalone:app
EOF

print_success "Deployment package created"

# Create ZIP file
print_status "Creating deployment ZIP..."
cd $DEPLOY_DIR
zip -r ../deployment.zip . > /dev/null
cd ..

print_success "Deployment ZIP created: deployment.zip"

# Deploy to Azure
print_status "Deploying to Azure App Service..."

# Set environment variables
print_status "Setting environment variables..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    USE_REAL_AGENTS=true \
    LLM_PROVIDER=google \
    GOOGLE_MODEL=gemini-2.0-flash \
    GOOGLE_API_KEY=$GOOGLE_API_KEY \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    ENABLE_ORYX_BUILD=true \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=false \
    > /dev/null

print_success "Environment variables set"

# Set the startup command explicitly
print_status "Setting startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "gunicorn --bind=0.0.0.0:\$PORT --timeout 600 --workers 1 --worker-class uvicorn.workers.UvicornWorker app_adapter_standalone:app" \
    > /dev/null

print_success "Startup command set"

# Deploy the ZIP file
print_status "Uploading deployment package..."
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src deployment.zip \
    > /dev/null

print_success "Deployment package uploaded"

# Wait for deployment to complete
print_status "Waiting for deployment to complete..."
sleep 45

# Cleanup
print_status "Cleaning up temporary files..."
rm -rf $DEPLOY_DIR
rm -f deployment.zip

print_success "Cleanup completed"

# Test deployment
print_status "Testing deployment..."

APP_URL="https://${APP_NAME}.azurewebsites.net"
echo "Testing URL: $APP_URL"

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local description=$2
    local expected_status=${3:-200}
    
    print_status "Testing $description..."
    
    # Wait a bit for the app to be ready
    sleep 10
    
    response=$(curl -s -w "%{http_code}" -o /tmp/response.txt "$APP_URL$endpoint" || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        print_success "$description - Status: $response"
        return 0
    else
        print_error "$description - Status: $response"
        if [ -f /tmp/response.txt ]; then
            echo "Response content:"
            cat /tmp/response.txt
        fi
        return 1
    fi
}

# Test health endpoint
if test_endpoint "/health" "Health Check"; then
    print_success "Health check passed"
    
    # Parse health response to check real agents
    health_response=$(curl -s "$APP_URL/health" 2>/dev/null || echo "{}")
    if echo "$health_response" | grep -q '"real_agents_available": *true'; then
        print_success "Real agents are available"
    else
        print_warning "Real agents may not be available"
        echo "Health response: $health_response"
    fi
else
    print_error "Health check failed"
fi

# Test main page
test_endpoint "/" "Main Page"

# Test API endpoints
test_endpoint "/api/agents/available" "Available Agents API"
test_endpoint "/api/events" "Events API"

# Test real agent functionality
print_status "Testing real agent functionality..."
agent_test_response=$(curl -s -X POST "$APP_URL/api/agents/message" \
    -H "Content-Type: application/json" \
    -d '{"agent_type": "coordinator", "message": "Hello, test message"}' \
    2>/dev/null || echo "{}")

if echo "$agent_test_response" | grep -q '"using_real_agent": *true'; then
    print_success "Real agents are working correctly"
elif echo "$agent_test_response" | grep -q '"response"'; then
    print_warning "Agents responding but may be using fallback mode"
    echo "Agent response: $agent_test_response"
else
    print_error "Agent functionality test failed"
    echo "Agent response: $agent_test_response"
fi

# Check deployment logs
print_status "Checking deployment logs..."
deployment_logs=$(az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME --provider application 2>/dev/null | head -20 || echo "Could not retrieve logs")
if echo "$deployment_logs" | grep -q "error\|Error\|ERROR"; then
    print_warning "Errors found in deployment logs"
    echo "$deployment_logs"
else
    print_success "No critical errors in deployment logs"
fi

# Final status report
echo ""
echo "=================================================="
echo -e "${BLUE}🎉 DEPLOYMENT SUMMARY${NC}"
echo "=================================================="
echo "App URL: $APP_URL"
echo "Health Check: $APP_URL/health"
echo "API Test: $APP_URL/api/agents/available"
echo ""

# Test if the main functionality is working
main_test=$(curl -s "$APP_URL/health" 2>/dev/null || echo "{}")
if echo "$main_test" | grep -q '"status": *"healthy"'; then
    print_success "✅ DEPLOYMENT SUCCESSFUL!"
    print_success "✅ Standalone SaaS application is running"
    
    if echo "$main_test" | grep -q '"real_agents_available": *true'; then
        print_success "✅ Real AI agents are active and working"
    else
        print_warning "⚠️  Real agents status unclear - check manually"
    fi
    
    echo ""
    echo -e "${GREEN}🎯 Your standalone SaaS + Real Agents solution is now live!${NC}"
    echo -e "${GREEN}The application is running with embedded agent functionality.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Visit $APP_URL to see your application"
    echo "2. Test the health endpoint: $APP_URL/health"
    echo "3. Test agent functionality via API: $APP_URL/api/agents/message"
    
else
    print_error "❌ DEPLOYMENT FAILED"
    print_error "The application is not responding correctly"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check Azure portal for detailed logs"
    echo "2. Verify environment variables are set correctly"
    echo "3. Check if all dependencies are installed"
    echo "4. Review the deployment logs above"
fi

echo "=================================================="
