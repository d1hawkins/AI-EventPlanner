#!/bin/bash

# Azure Application Startup Diagnosis Script
# This script helps diagnose why the Azure app is not starting

set -e

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"

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

print_status "🔍 Diagnosing Azure application startup issues..."

# Check app status
print_status "Checking application status..."
APP_STATE=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "state" -o tsv)
echo "App State: $APP_STATE"

# Check app settings
print_status "Checking critical environment variables..."
DATABASE_URL_SET=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='DATABASE_URL'].value" -o tsv)
GOOGLE_API_KEY_SET=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='GOOGLE_API_KEY'].value" -o tsv)
LLM_PROVIDER_SET=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='LLM_PROVIDER'].value" -o tsv)

if [ -n "$DATABASE_URL_SET" ]; then
    print_success "DATABASE_URL is set"
else
    print_error "DATABASE_URL is not set"
fi

if [ -n "$GOOGLE_API_KEY_SET" ]; then
    print_success "GOOGLE_API_KEY is set"
else
    print_error "GOOGLE_API_KEY is not set"
fi

if [ -n "$LLM_PROVIDER_SET" ]; then
    print_success "LLM_PROVIDER is set to: $LLM_PROVIDER_SET"
else
    print_error "LLM_PROVIDER is not set"
fi

# Check startup command
print_status "Checking startup command..."
STARTUP_FILE=$(az webapp config show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "appCommandLine" -o tsv)
echo "Startup Command: $STARTUP_FILE"

# Check Python version
print_status "Checking Python runtime..."
PYTHON_VERSION=$(az webapp config show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "linuxFxVersion" -o tsv)
echo "Python Runtime: $PYTHON_VERSION"

# Get recent logs
print_status "Getting recent application logs..."
echo "=== Recent Application Logs ==="
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP --provider application --num-lines 50 || echo "Could not retrieve application logs"

echo ""
print_status "Getting recent deployment logs..."
echo "=== Recent Deployment Logs ==="
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP --provider deployment --num-lines 30 || echo "Could not retrieve deployment logs"

echo ""
print_status "Getting recent web server logs..."
echo "=== Recent Web Server Logs ==="
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP --provider web --num-lines 20 || echo "Could not retrieve web server logs"

# Check if we can access Kudu
print_status "Checking Kudu console access..."
KUDU_URL="https://$APP_NAME.scm.azurewebsites.net"
echo "Kudu Console: $KUDU_URL"

# Test basic connectivity
print_status "Testing basic connectivity..."
APP_URL="https://$APP_NAME.azurewebsites.net"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL" || echo "000")
echo "HTTP Status: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "500" ]; then
    print_error "Application is returning HTTP 500 - Internal Server Error"
    print_status "This usually indicates a Python application startup error"
elif [ "$HTTP_STATUS" = "000" ]; then
    print_error "Cannot connect to application"
else
    print_status "Application is responding with HTTP $HTTP_STATUS"
fi

# Recommendations
echo ""
print_status "=== RECOMMENDATIONS ==="

if [ "$HTTP_STATUS" = "500" ]; then
    echo "1. Check the application logs above for Python errors"
    echo "2. Common issues:"
    echo "   - Missing dependencies in requirements.txt"
    echo "   - Import errors in Python code"
    echo "   - Database connection issues"
    echo "   - Missing environment variables"
    echo "3. Try restarting the application:"
    echo "   az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP"
    echo "4. Check if startup.sh or main files exist and are correct"
fi

if [ -z "$DATABASE_URL_SET" ] || [ -z "$GOOGLE_API_KEY_SET" ]; then
    echo "5. Set missing environment variables using the fixed deployment script"
fi

echo ""
print_status "To restart the application:"
echo "az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP"

print_status "To view live logs:"
echo "az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"

print_status "To access Kudu console:"
echo "Open: $KUDU_URL"
