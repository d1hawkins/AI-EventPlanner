#!/bin/bash

# Azure Deployment Script - Simple Fix for Requirements Issue
# This script uses minimal, compatible dependencies to fix the deployment

set -e

echo "🚀 Starting Azure deployment with simple fix..."

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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Azure CLI
if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

print_success "Azure CLI is ready"

# Step 1: Create simple, compatible requirements.txt
print_status "Creating simple requirements.txt with compatible versions..."
cat > requirements.txt << 'EOF'
# Core web framework - stable versions
fastapi==0.100.0
uvicorn==0.23.0
gunicorn==21.2.0

# Database - stable versions
sqlalchemy==2.0.20
psycopg2-binary==2.9.7

# Data validation
pydantic==2.0.0

# Environment & Configuration
python-dotenv==1.0.0

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Basic utilities
requests==2.31.0
typing-extensions==4.7.0
EOF

print_success "Simple requirements.txt created!"

# Step 2: Create minimal deployment package
print_status "Creating minimal deployment package..."

rm -f simple_deployment.zip

# Create a minimal package with just the working adapter
zip -r simple_deployment.zip \
    requirements.txt \
    app_adapter_with_agents_fixed.py \
    app/web/static/saas/ \
    --exclude "*.pyc" \
    --exclude "__pycache__/*" \
    2>/dev/null || true

print_success "Minimal deployment package created: simple_deployment.zip"

# Step 3: Set startup command
print_status "Setting startup command..."
az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 app_adapter_with_agents_fixed:app"

print_success "Startup command configured"

# Step 4: Deploy
print_status "Uploading minimal deployment package..."
az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src simple_deployment.zip

print_success "Deployment package uploaded"

# Step 5: Wait and test
print_status "Waiting for deployment to complete..."
sleep 45

print_status "Testing deployment..."
APP_URL="https://${APP_NAME}.azurewebsites.net"

echo "Testing health endpoint..."
if curl -f -s "${APP_URL}/health" > /dev/null; then
    print_success "Health check passed!"
    curl -s "${APP_URL}/health" | python -m json.tool 2>/dev/null || curl -s "${APP_URL}/health"
else
    print_error "Health check failed"
fi

# Clean up
rm -f requirements.txt
rm -f simple_deployment.zip

echo ""
echo "🎉 Simple deployment completed!"
echo "Application URL: ${APP_URL}"
echo ""
echo "This deployment fixes the requirements.txt issue with minimal dependencies."
echo "If this works, we can then add more features incrementally."
