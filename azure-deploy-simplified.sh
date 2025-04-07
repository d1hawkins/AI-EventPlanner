#!/bin/bash

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in to Azure
echo "Checking Azure login status..."
az account show &> /dev/null
if [ $? -ne 0 ]; then
    echo "You are not logged in to Azure. Please run 'az login' first."
    exit 1
fi

# Set variables
RESOURCE_GROUP="ai-event-planner-rg"
APP_SERVICE_PLAN="ai-event-planner-plan"
WEB_APP_NAME="ai-event-planner-saas-py"
LOCATION="eastus"

# Check if resource group exists
echo "Checking if resource group exists..."
if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo "Creating resource group $RESOURCE_GROUP..."
    az group create --name $RESOURCE_GROUP --location $LOCATION
fi

# Check if App Service Plan exists
echo "Checking if App Service Plan exists..."
if ! az appservice plan show --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating App Service Plan $APP_SERVICE_PLAN..."
    az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku B1 --is-linux
fi

# Check if Web App exists
echo "Checking if Web App exists..."
if ! az webapp show --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating Web App $WEB_APP_NAME..."
    az webapp create --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime "PYTHON|3.9"
fi

# Create a temporary directory for deployment
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Create simplified app files
echo "Creating simplified app files..."
mkdir -p $TEMP_DIR

# Copy app_simplified.py
cp app_simplified.py $TEMP_DIR/

# Create requirements.txt
cat > $TEMP_DIR/requirements.txt << EOF
fastapi==0.95.0
uvicorn==0.21.1
gunicorn==20.1.0
pydantic==1.10.7
EOF

# Create startup.sh
cat > $TEMP_DIR/startup.sh << EOF
#!/bin/bash
cd /home/site/wwwroot
pip install -r requirements.txt
gunicorn app_simplified:app --bind=0.0.0.0:8000 --workers=4
EOF

# Make startup.sh executable
chmod +x $TEMP_DIR/startup.sh

# Create deployment package
echo "Creating deployment package..."
cd $TEMP_DIR
zip -r ../deploy.zip .
cd ..

# Deploy to Azure
echo "Deploying to Azure App Service..."
az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --src deploy.zip

# Configure App Service
echo "Configuring App Service..."
az webapp config set --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --startup-file "startup.sh"

# Enable logging
echo "Enabling logging..."
az webapp log config --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --docker-container-logging filesystem

# Clean up
echo "Cleaning up..."
rm -rf $TEMP_DIR
rm -f deploy.zip

echo "Deployment completed successfully."
echo "Your application is available at: https://$WEB_APP_NAME.azurewebsites.net"
