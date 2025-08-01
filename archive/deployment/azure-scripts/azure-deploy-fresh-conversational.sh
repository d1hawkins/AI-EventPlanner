#!/bin/bash

# Fresh Azure Deployment Script for Conversational SaaS with Real Agents
# This script ensures a completely clean deployment with real conversational agents

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

echo -e "${BLUE}🚀 Starting FRESH Azure Deployment for Conversational SaaS + Real Agents${NC}"
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

# Check prerequisites
print_status "Checking prerequisites..."
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

if ! command -v zip &> /dev/null; then
    print_error "zip is not installed. Please install it first."
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

print_success "Prerequisites check passed"

# Stop the app service to ensure clean deployment
print_status "Stopping Azure App Service for clean deployment..."
az webapp stop --resource-group $RESOURCE_GROUP --name $APP_NAME || true
print_success "App service stopped"

# Create deployment package
print_status "Creating fresh deployment package..."

# Create temporary directory for deployment
DEPLOY_DIR="deploy_fresh_$(date +%s)"
mkdir -p $DEPLOY_DIR

print_status "Copying conversational application files..."

# Copy the main conversational app
cp app_adapter_conversational.py $DEPLOY_DIR/

# Copy requirements
cp requirements_complete.txt $DEPLOY_DIR/requirements.txt

# Copy entire app directory structure with all conversational components
print_status "Copying complete app directory structure..."
cp -r app/ $DEPLOY_DIR/app/

# Ensure all conversational utilities are present
print_status "Verifying conversational components..."
required_files=(
    "app/utils/question_manager.py"
    "app/utils/recommendation_engine.py"
    "app/utils/conversation_memory.py"
    "app/utils/conversation_paths.py"
    "app/utils/proactive_suggestions.py"
    "app/utils/recommendation_learning.py"
    "app/graphs/coordinator_graph.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found: $file"
    else
        print_error "Missing required file: $file"
        exit 1
    fi
done

# Copy all SaaS static files
print_status "Copying SaaS website files..."
mkdir -p $DEPLOY_DIR/app/web/static/saas
cp -r app/web/static/saas/* $DEPLOY_DIR/app/web/static/saas/

# Create web.config for Azure with conversational settings
print_status "Creating Azure web.config..."
cat > $DEPLOY_DIR/web.config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="python" arguments="app_adapter_conversational.py" stdoutLogEnabled="true" stdoutLogFile="python.log" startupTimeLimit="120" requestTimeout="00:05:00">
      <environmentVariables>
        <environmentVariable name="PORT" value="%HTTP_PLATFORM_PORT%" />
        <environmentVariable name="USE_REAL_AGENTS" value="true" />
        <environmentVariable name="LLM_PROVIDER" value="google" />
        <environmentVariable name="GOOGLE_MODEL" value="gemini-2.0-flash" />
        <environmentVariable name="CONVERSATION_MODE" value="enabled" />
        <environmentVariable name="RECOMMENDATION_ENGINE" value="enabled" />
        <environmentVariable name="QUESTION_FLOW" value="conversational" />
        <environmentVariable name="CONVERSATION_MEMORY_LIMIT" value="50" />
        <environmentVariable name="ENABLE_PROACTIVE_SUGGESTIONS" value="true" />
        <environmentVariable name="CONVERSATION_FEATURE_FLAG" value="true" />
        <environmentVariable name="PYTHONPATH" value="/home/site/wwwroot" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
EOF

print_success "Deployment package created"

# Create ZIP file
print_status "Creating deployment ZIP..."
cd $DEPLOY_DIR
zip -r ../deployment_fresh.zip . > /dev/null
cd ..

print_success "Fresh deployment ZIP created: deployment_fresh.zip"

# Clear any existing deployment files
print_status "Clearing existing deployment files..."
az webapp deployment source delete --resource-group $RESOURCE_GROUP --name $APP_NAME || true

# Deploy to Azure
print_status "Deploying fresh package to Azure App Service..."

# Set environment variables with conversational settings
print_status "Setting conversational environment variables..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    USE_REAL_AGENTS=true \
    LLM_PROVIDER=google \
    GOOGLE_MODEL=gemini-2.0-flash \
    GOOGLE_API_KEY=$GOOGLE_API_KEY \
    CONVERSATION_MODE=enabled \
    RECOMMENDATION_ENGINE=enabled \
    QUESTION_FLOW=conversational \
    CONVERSATION_MEMORY_LIMIT=50 \
    ENABLE_PROACTIVE_SUGGESTIONS=true \
    CONVERSATION_FEATURE_FLAG=true \
    PYTHONPATH=/home/site/wwwroot \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    ENABLE_ORYX_BUILD=true \
    > /dev/null

print_success "Conversational environment variables set"

# Deploy the ZIP file
print_status "Uploading fresh deployment package..."
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src deployment_fresh.zip \
    > /dev/null

print_success "Fresh deployment package uploaded"

# Start the app service
print_status "Starting Azure App Service..."
az webapp start --resource-group $RESOURCE_GROUP --name $APP_NAME

# Wait for deployment to complete
print_status "Waiting for fresh deployment to complete..."
sleep 45

# Cleanup
print_status "Cleaning up temporary files..."
rm -rf $DEPLOY_DIR
rm -f deployment_fresh.zip

print_success "Cleanup completed"

# Test deployment
print_status "Testing fresh conversational deployment..."

APP_URL="https://${APP_NAME}.azurewebsites.net"
echo "Testing URL: $APP_URL"

# Function to test endpoint with retries
test_endpoint_with_retry() {
    local endpoint=$1
    local description=$2
    local max_retries=5
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        print_status "Testing $description (attempt $((retry + 1))/$max_retries)..."
        
        response=$(curl -s -w "%{http_code}" -o /tmp/response.txt "$APP_URL$endpoint" || echo "000")
        
        if [ "$response" = "200" ]; then
            print_success "$description - Status: $response"
            return 0
        else
            print_warning "$description - Status: $response (retrying...)"
            sleep 10
            retry=$((retry + 1))
        fi
    done
    
    print_error "$description - Failed after $max_retries attempts"
    return 1
}

# Test health endpoint with detailed check
print_status "Testing health endpoint for real agents..."
sleep 10

health_response=$(curl -s "$APP_URL/health" 2>/dev/null || echo "{}")
echo "Health response: $health_response"

if echo "$health_response" | grep -q '"status": *"healthy"'; then
    print_success "Application is healthy"
    
    if echo "$health_response" | grep -q '"real_agents_available": *true'; then
        print_success "🎉 REAL AGENTS ARE AVAILABLE!"
    elif echo "$health_response" | grep -q '"using_conversational_flow": *true'; then
        print_success "🎉 CONVERSATIONAL FLOW IS ACTIVE!"
    else
        print_warning "Real agents status unclear - checking further..."
    fi
else
    print_warning "Health check unclear - checking application status..."
fi

# Test conversational agent functionality
print_status "Testing conversational agent functionality..."
agent_test_response=$(curl -s -X POST "$APP_URL/api/agents/message" \
    -H "Content-Type: application/json" \
    -d '{"agent_type": "coordinator", "message": "I want to plan a corporate event"}' \
    2>/dev/null || echo "{}")

echo "Agent test response: $agent_test_response"

if echo "$agent_test_response" | grep -q '"using_real_agent": *true'; then
    print_success "🎉 REAL AGENTS ARE WORKING!"
elif echo "$agent_test_response" | grep -q '"using_conversational_flow": *true'; then
    print_success "🎉 CONVERSATIONAL FLOW IS WORKING!"
elif echo "$agent_test_response" | grep -q '"response"'; then
    print_warning "Agents responding but may be in fallback mode"
else
    print_error "Agent functionality test failed"
fi

# Test other endpoints
test_endpoint_with_retry "/" "Main Page"
test_endpoint_with_retry "/agents.html" "Agents Page"
test_endpoint_with_retry "/api/agents/available" "Available Agents API"

# Final status report
echo ""
echo "=================================================="
echo -e "${BLUE}🎉 FRESH DEPLOYMENT SUMMARY${NC}"
echo "=================================================="
echo "App URL: $APP_URL"
echo "Health Check: $APP_URL/health"
echo "Agents Page: $APP_URL/agents.html"
echo ""

# Final health check
final_health=$(curl -s "$APP_URL/health" 2>/dev/null || echo "{}")
if echo "$final_health" | grep -q '"status": *"healthy"'; then
    print_success "✅ FRESH DEPLOYMENT SUCCESSFUL!"
    
    if echo "$final_health" | grep -q '"real_agents_available": *true' || echo "$final_health" | grep -q '"using_conversational_flow": *true'; then
        print_success "✅ CONVERSATIONAL AGENTS ARE ACTIVE!"
        echo ""
        echo -e "${GREEN}🎯 Your fresh conversational SaaS solution is now live with real agents!${NC}"
        echo -e "${GREEN}Users can now experience the full conversational event planning flow.${NC}"
    else
        print_warning "⚠️  Conversational agents may need a few more minutes to initialize"
        echo ""
        echo "The application is deployed. If agents aren't fully active yet:"
        echo "1. Wait 2-3 minutes for full initialization"
        echo "2. Check $APP_URL/health again"
        echo "3. Test the agents page: $APP_URL/agents.html"
    fi
else
    print_error "❌ DEPLOYMENT NEEDS ATTENTION"
    echo "Please check the Azure portal for detailed logs"
fi

echo "=================================================="
