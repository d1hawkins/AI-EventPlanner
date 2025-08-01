#!/bin/bash
# Deploy the full AI Event Planner SaaS application to Azure App Service (Python) without Docker

set -e

# Configuration
APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"
LOCATION="eastus"
PYTHON_VERSION="3.9"
SKU="B1"
DB_SERVER="ai-event-planner-db"
DB_NAME="eventplanner"
DB_ADMIN="dbadmin"
DB_PASSWORD="VM*admin"

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

# Check if PostgreSQL server exists
echo "Checking if PostgreSQL server exists..."
if ! az postgres server show --name $DB_SERVER --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating PostgreSQL server $DB_SERVER..."
    az postgres server create \
        --name $DB_SERVER \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --admin-user $DB_ADMIN \
        --admin-password $DB_PASSWORD \
        --sku-name GP_Gen5_2 \
        --version 11
    
    # Configure firewall rules to allow Azure services
    echo "Configuring PostgreSQL firewall rules..."
    az postgres server firewall-rule create \
        --name AllowAllAzureIPs \
        --server $DB_SERVER \
        --resource-group $RESOURCE_GROUP \
        --start-ip-address 0.0.0.0 \
        --end-ip-address 0.0.0.0
fi

# Check if database exists
echo "Checking if database exists..."
if ! az postgres db show --name $DB_NAME --server $DB_SERVER --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating database $DB_NAME..."
    az postgres db create \
        --name $DB_NAME \
        --server $DB_SERVER \
        --resource-group $RESOURCE_GROUP
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
# Copy the entire app directory
cp -r app $DEPLOY_DIR/
# Copy migrations directory
cp -r migrations $DEPLOY_DIR/
# Copy scripts directory
cp -r scripts $DEPLOY_DIR/
# Copy adapter and startup files
cp app_adapter.py $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/
cp alembic.ini $DEPLOY_DIR/

# Copy web.config and startup files
echo "Copying web.config and startup files..."
cp web.config $DEPLOY_DIR/
cp startup.py $DEPLOY_DIR/
cp startup.sh $DEPLOY_DIR/
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

# Set environment variables
echo "Setting environment variables..."
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings \
    DATABASE_URL="postgresql://${DB_ADMIN}@${DB_SERVER}:${DB_PASSWORD}@${DB_SERVER}.postgres.database.azure.com:5432/${DB_NAME}" \
    SECRET_KEY="iuoiuoi_09870_87h98h9_98h98h_vh98h98h" \
    ACCESS_TOKEN_EXPIRE_MINUTES="60" \
    REFRESH_TOKEN_EXPIRE_DAYS="7" \
    ALGORITHM="HS256" \
    LLM_PROVIDER="google" \
    GOOGLE_API_KEY="AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU" \
    GOOGLE_MODEL="gemini-2.0-flash" \
    OPENAI_API_KEY="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" \
    OPENAI_MODEL="gpt-4" \
    SENDGRID_API_KEY="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" \
    EMAIL_FROM="noreply@aieventplanner.com" \
    EMAIL_FROM_NAME="AI Event Planner" \
    DEFAULT_TENANT="default" \
    TENANT_HEADER="X-Tenant-ID" \
    ENABLE_AGENT_LOGGING="true" \
    AGENT_MEMORY_STORAGE="file" \
    AGENT_MEMORY_PATH="./agent_memory" \
    RUN_MIGRATIONS="true" \
    ENVIRONMENT="production" \
    APP_VERSION="1.0.0" \
    APP_NAME="AI Event Planner"

# Enable logging
echo "Enabling logging..."
az webapp log config --resource-group $RESOURCE_GROUP --name $APP_NAME --application-logging filesystem --detailed-error-messages true --failed-request-tracing true --web-server-logging filesystem

# Clean up
echo "Cleaning up..."
rm -rf $DEPLOY_DIR
rm -f deploy.zip

echo -e "${GREEN}Deployment completed successfully.${NC}"
echo -e "Your application is available at: https://$APP_NAME.azurewebsites.net"
