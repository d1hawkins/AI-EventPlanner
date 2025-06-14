#!/bin/bash
# Docker-based deployment script for AI Event Planner SaaS application to Azure
# This script reads secrets and keys from the .env.saas file and sets them as app settings in Azure

set -e

# Configuration - Use names without spaces for Azure resources
APP_NAME="ai-event-planner-saas"
RESOURCE_GROUP="ai-event-planner-rg"
REGISTRY_NAME="aieventplannerregistry"
IMAGE_NAME="ai-event-planner-saas"
IMAGE_TAG="latest"
ENV_FILE=".env.saas"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Creating a Docker-based deployment for Azure with improved security..."

# Check if .env.saas file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Error: $ENV_FILE file not found.${NC}"
    echo "Please make sure the $ENV_FILE file exists in the current directory."
    exit 1
fi

# Load environment variables from .env.saas for this script
echo "Loading environment variables from $ENV_FILE..."
# Create arrays to store app settings
APP_SETTINGS=()

# Read each line from .env.saas
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ ]] && continue
    [[ -z "$line" ]] && continue
    
    # Extract key and value
    key=$(echo "$line" | cut -d= -f1)
    value=$(echo "$line" | cut -d= -f2-)
    
    # Skip APP_NAME from .env.saas to avoid conflicts with our hardcoded APP_NAME
    if [ "$key" = "APP_NAME" ]; then
        echo "Skipping APP_NAME from .env.saas, using hardcoded value: $APP_NAME"
        continue
    fi
    
    # Add to app settings array
    APP_SETTINGS+=("$key=\"$value\"")
    
    # Export as environment variable for this script
    export "$key"="$value"
done < "$ENV_FILE"

# Create Azure Container Registry if it doesn't exist
echo "Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic --admin-enabled true

# Get the registry credentials
echo "Getting registry credentials..."
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query "passwords[0].value" -o tsv)

# Build the Docker image without passing sensitive data as build args
echo "Building Docker image with improved security..."
docker build -t $IMAGE_NAME:$IMAGE_TAG -f Dockerfile.saas.fixed .

# Tag the image for the Azure Container Registry
echo "Tagging Docker image..."
docker tag $IMAGE_NAME:$IMAGE_TAG $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG

# Log in to the Azure Container Registry
echo "Logging in to Azure Container Registry..."
docker login $REGISTRY_NAME.azurecr.io --username $ACR_USERNAME --password $ACR_PASSWORD

# Push the image to the Azure Container Registry
echo "Pushing Docker image to Azure Container Registry..."
docker push $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG

# Create or update the App Service Plan
echo "Creating App Service Plan..."
az appservice plan create --name "${APP_NAME}-plan" --resource-group $RESOURCE_GROUP --is-linux --sku B1 || true

# Create or update the Web App
echo "Creating Web App..."
az webapp create --resource-group $RESOURCE_GROUP --plan "${APP_NAME}-plan" --name $APP_NAME --deployment-container-image-name $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG || true

# Configure the Web App with registry credentials
echo "Configuring Web App registry credentials..."
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings \
    WEBSITES_PORT=8000 \
    DOCKER_REGISTRY_SERVER_URL=https://$REGISTRY_NAME.azurecr.io \
    DOCKER_REGISTRY_SERVER_USERNAME=$ACR_USERNAME \
    DOCKER_REGISTRY_SERVER_PASSWORD=$ACR_PASSWORD

# Set the environment variables from .env.saas as app settings
echo "Setting environment variables from $ENV_FILE as app settings..."
APP_SETTINGS_CMD="az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings"
for setting in "${APP_SETTINGS[@]}"; do
    APP_SETTINGS_CMD+=" $setting"
done
echo "Running: Setting app settings in Azure..."
eval $APP_SETTINGS_CMD

# Restart the Web App
echo "Restarting Web App..."
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Your application is available at: https://$APP_NAME.azurewebsites.net${NC}"
echo -e "${GREEN}SaaS application available at: https://$APP_NAME.azurewebsites.net/static/saas/index.html${NC}"
