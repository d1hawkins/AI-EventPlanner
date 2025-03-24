#!/bin/bash
# Deploy the AI Event Planner SaaS application to Azure

set -e

# Configuration
APP_NAME="ai-event-planner-saas"
RESOURCE_GROUP="ai-event-planner-rg"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Deploying AI Event Planner SaaS to Azure ===${NC}"

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

# Check if App Service exists
echo "Checking if App Service exists..."
if ! az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${RED}Error: App Service '$APP_NAME' does not exist in resource group '$RESOURCE_GROUP'.${NC}"
    echo -e "${YELLOW}Please run the full azure-deploy-saas.sh script first to create all required resources.${NC}"
    exit 1
fi

# Create a temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Created temporary directory: $DEPLOY_DIR"

# Copy application files to the deployment directory
echo "Copying application files..."
mkdir -p $DEPLOY_DIR/app
cp -r app/* $DEPLOY_DIR/app/
cp -r migrations $DEPLOY_DIR/
cp -r scripts $DEPLOY_DIR/
cp alembic.ini $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/

# Create a deployment script
echo "Creating deployment script..."
cat > $DEPLOY_DIR/deploy.sh << 'EOF'
#!/bin/bash
set -e

# Install dependencies
pip install -r requirements.txt

# Run database migrations using the migrate.py script
python -m scripts.migrate

# Start the application
gunicorn app.main_saas:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
EOF

chmod +x $DEPLOY_DIR/deploy.sh

# Create a zip file for deployment
echo "Creating deployment package..."
cd $DEPLOY_DIR
zip -r ../deploy.zip .
cd -

if [ ! -f deploy.zip ]; then
    echo -e "${RED}Error: Failed to create deployment package.${NC}"
    exit 1
fi

# Deploy the zip file using the current command
echo "Deploying to App Service..."
az webapp deploy --resource-group $RESOURCE_GROUP --name $APP_NAME --src-path deploy.zip --type zip

# Set startup command
echo "Setting startup command..."
az webapp config set --name $APP_NAME --resource-group $RESOURCE_GROUP \
    --startup-file "gunicorn app.main_saas:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"

# Set environment variables from .env.azure
echo "Setting environment variables..."
while IFS='=' read -r key value; do
    # Skip empty lines and comments
    if [[ -z "$key" || "$key" == \#* ]]; then
        continue
    fi
    # Skip lines with no value
    if [[ -z "$value" ]]; then
        continue
    fi
    
    # Set environment variable
    echo "Setting $key"
    az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings "$key=$value"
done < .env.azure

# Clean up
echo "Cleaning up..."
rm -rf $DEPLOY_DIR
rm deploy.zip

# Get the URL of the deployed application
APP_URL="https://$APP_NAME.azurewebsites.net"

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Your application is available at: $APP_URL${NC}"
echo -e "${GREEN}SaaS application available at: $APP_URL/static/saas/index.html${NC}"
