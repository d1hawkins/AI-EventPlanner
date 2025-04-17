#!/bin/bash
# Deploy the AI Event Planner SaaS application to Azure App Service (Python) without Docker

set -e

# Configuration
APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"
LOCATION="eastus"
PYTHON_VERSION="3.9"
SKU="B1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if logged in to Azure
echo "Checking Azure login status..."
az account show &> /dev/null || {
    echo -e "${YELLOW}Not logged in to Azure. Please login.${NC}"
    az login
}

# Check if resource group exists
echo "Checking if resource group exists..."
if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo "Creating resource group $RESOURCE_GROUP in $LOCATION..."
    az group create --name $RESOURCE_GROUP --location $LOCATION
fi

# Check if App Service Plan exists
echo "Checking if App Service Plan exists..."
APP_SERVICE_PLAN="${APP_NAME}-plan"
if ! az appservice plan show --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating App Service Plan $APP_SERVICE_PLAN..."
    az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku $SKU --is-linux
fi

# Check if Web App exists
echo "Checking if Web App exists..."
if ! az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating Web App $APP_NAME..."
    az webapp create --name $APP_NAME --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime "PYTHON|$PYTHON_VERSION"
fi

# Create a temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Created temporary directory: $DEPLOY_DIR"

# Copy files to the deployment directory
echo "Copying files to deployment directory..."
cp app_simplified.py $DEPLOY_DIR/
cp app_adapter.py $DEPLOY_DIR/
cp app_adapter_with_agents.py $DEPLOY_DIR/
cp requirements_simplified.txt $DEPLOY_DIR/requirements.txt
mkdir -p $DEPLOY_DIR/app/web/static
cp -r app/web/static $DEPLOY_DIR/app/web/

# Copy agent-related directories to ensure they're available in Azure
echo "Copying agent-related directories..."
mkdir -p $DEPLOY_DIR/app/agents
cp -r app/agents $DEPLOY_DIR/app/
mkdir -p $DEPLOY_DIR/app/db
cp -r app/db $DEPLOY_DIR/app/
mkdir -p $DEPLOY_DIR/app/middleware
cp -r app/middleware $DEPLOY_DIR/app/

# Copy web.config and startup.py files
echo "Copying web.config and startup.py files..."
cp web.config $DEPLOY_DIR/
cp startup.py $DEPLOY_DIR/

# Create startup command file (as a backup)
echo "Creating startup command file..."
cat > $DEPLOY_DIR/startup.sh << 'EOF'
#!/bin/bash
cd /home/site/wwwroot
pip install -r requirements.txt
gunicorn app_adapter:app --bind=0.0.0.0:8000 --workers=4
EOF
chmod +x $DEPLOY_DIR/startup.sh

# Create a zip file for deployment
echo "Creating deployment package..."
cd $DEPLOY_DIR
zip -r ../deploy.zip .
cd ..

# Deploy to Azure App Service
echo "Deploying to Azure App Service..."
az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $APP_NAME --src deploy.zip

# Configure the App Service
echo "Configuring App Service..."
az webapp config set --resource-group $RESOURCE_GROUP --name $APP_NAME --startup-file "startup.sh"

# Enable logging
echo "Enabling logging..."
az webapp log config --resource-group $RESOURCE_GROUP --name $APP_NAME --application-logging filesystem --detailed-error-messages true --failed-request-tracing true --web-server-logging filesystem

# Clean up
echo "Cleaning up..."
rm -rf $DEPLOY_DIR
rm -f deploy.zip

echo -e "${GREEN}Deployment completed successfully.${NC}"
echo -e "Your application is available at: https://$APP_NAME.azurewebsites.net"
