#!/bin/bash
# Docker-based deployment script for AI Event Planner SaaS application to Azure

set -e

# Configuration
APP_NAME="ai-event-planner-saas"
RESOURCE_GROUP="ai-event-planner-rg"
REGISTRY_NAME="aieventplannerregistry"
IMAGE_NAME="ai-event-planner-saas"
IMAGE_TAG="latest"

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "Creating a Docker-based deployment for Azure..."

# Create Azure Container Registry if it doesn't exist
echo "Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic --admin-enabled true

# Get the registry credentials
echo "Getting registry credentials..."
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query "passwords[0].value" -o tsv)

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME:$IMAGE_TAG -f Dockerfile.saas .

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
az appservice plan create --name ${APP_NAME}-plan --resource-group $RESOURCE_GROUP --is-linux --sku B1

# Create or update the Web App
echo "Creating Web App..."
az webapp create --resource-group $RESOURCE_GROUP --plan ${APP_NAME}-plan --name $APP_NAME --deployment-container-image-name $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG

# Configure the Web App
echo "Configuring Web App..."
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings \
    WEBSITES_PORT=8000 \
    DOCKER_REGISTRY_SERVER_URL=https://$REGISTRY_NAME.azurecr.io \
    DOCKER_REGISTRY_SERVER_USERNAME=$ACR_USERNAME \
    DOCKER_REGISTRY_SERVER_PASSWORD=$ACR_PASSWORD

# Restart the Web App
echo "Restarting Web App..."
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Your application is available at: https://$APP_NAME.azurewebsites.net${NC}"
echo -e "${GREEN}SaaS application available at: https://$APP_NAME.azurewebsites.net/static/saas/index.html${NC}"
