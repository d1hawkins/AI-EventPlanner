#!/bin/bash
# Deploy the AI Event Planner SaaS application to Azure

set -e

# Configuration
APP_NAME="ai-event-planner-saas"
RESOURCE_GROUP="ai-event-planner-rg"
LOCATION="eastus"
SKU="P1V2"
POSTGRES_SERVER_NAME="ai-event-planner-db"
POSTGRES_ADMIN_USER="aiepadmin"
POSTGRES_DB_NAME="aieventplanner"
STORAGE_ACCOUNT_NAME="aieventplannerstorage"

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

# Check if .env.azure file exists
if [ ! -f .env.azure ]; then
    echo -e "${YELLOW}No .env.azure file found. Creating one from .env.saas.example...${NC}"
    if [ -f .env.saas.example ]; then
        cp .env.saas.example .env.azure
        echo -e "${GREEN}.env.azure file created. Please edit it with your Azure configuration.${NC}"
        echo -e "${YELLOW}Press Enter to continue after editing the file, or Ctrl+C to cancel.${NC}"
        read
    else
        echo -e "${RED}No .env.saas.example file found. Please create a .env.azure file manually.${NC}"
        exit 1
    fi
fi

# Load environment variables from .env.azure
echo "Loading environment variables from .env.azure..."
export $(grep -v '^#' .env.azure | xargs)

# Create resource group if it doesn't exist
echo "Creating resource group if it doesn't exist..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create PostgreSQL server if it doesn't exist
echo "Creating PostgreSQL server if it doesn't exist..."
if ! az postgres server show --name $POSTGRES_SERVER_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating PostgreSQL server..."
    
    # Generate a random password for PostgreSQL admin
    POSTGRES_ADMIN_PASSWORD=$(openssl rand -base64 16)
    
    # Create PostgreSQL server
    az postgres server create \
        --name $POSTGRES_SERVER_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --admin-user $POSTGRES_ADMIN_USER \
        --admin-password $POSTGRES_ADMIN_PASSWORD \
        --sku-name GP_Gen5_2 \
        --version 11
    
    # Allow Azure services to access the PostgreSQL server
    az postgres server firewall-rule create \
        --name AllowAllAzureIPs \
        --resource-group $RESOURCE_GROUP \
        --server-name $POSTGRES_SERVER_NAME \
        --start-ip-address 0.0.0.0 \
        --end-ip-address 0.0.0.0
    
    # Create database
    az postgres db create \
        --name $POSTGRES_DB_NAME \
        --resource-group $RESOURCE_GROUP \
        --server-name $POSTGRES_SERVER_NAME
    
    # Update .env.azure with PostgreSQL connection string
    POSTGRES_HOST="$POSTGRES_SERVER_NAME.postgres.database.azure.com"
    POSTGRES_CONNECTION_STRING="postgresql://$POSTGRES_ADMIN_USER@$POSTGRES_SERVER_NAME:$POSTGRES_ADMIN_PASSWORD@$POSTGRES_HOST/$POSTGRES_DB_NAME"
    
    # Update .env.azure file
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=$POSTGRES_CONNECTION_STRING|g" .env.azure
    
    echo -e "${GREEN}PostgreSQL server created.${NC}"
    echo -e "${YELLOW}PostgreSQL admin password: $POSTGRES_ADMIN_PASSWORD${NC}"
    echo -e "${YELLOW}Please save this password in a secure location.${NC}"
else
    echo -e "${GREEN}PostgreSQL server already exists.${NC}"
fi

# Create storage account if it doesn't exist
echo "Creating storage account if it doesn't exist..."
if ! az storage account show --name $STORAGE_ACCOUNT_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating storage account..."
    az storage account create \
        --name $STORAGE_ACCOUNT_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Standard_LRS \
        --kind StorageV2
    
    # Get storage account connection string
    STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
        --name $STORAGE_ACCOUNT_NAME \
        --resource-group $RESOURCE_GROUP \
        --query connectionString \
        --output tsv)
    
    # Update .env.azure file
    sed -i "s|STORAGE_CONNECTION_STRING=.*|STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION_STRING|g" .env.azure
    
    echo -e "${GREEN}Storage account created.${NC}"
else
    echo -e "${GREEN}Storage account already exists.${NC}"
fi

# Create App Service plan if it doesn't exist
echo "Creating App Service plan if it doesn't exist..."
if ! az appservice plan show --name $APP_NAME-plan --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating App Service plan..."
    az appservice plan create \
        --name $APP_NAME-plan \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku $SKU \
        --is-linux
    
    echo -e "${GREEN}App Service plan created.${NC}"
else
    echo -e "${GREEN}App Service plan already exists.${NC}"
fi

# Create App Service if it doesn't exist
echo "Creating App Service if it doesn't exist..."
if ! az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating App Service..."
    az webapp create \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --plan $APP_NAME-plan \
        --runtime "PYTHON|3.9"
    
    echo -e "${GREEN}App Service created.${NC}"
else
    echo -e "${GREEN}App Service already exists.${NC}"
fi

# Configure App Service
echo "Configuring App Service..."
az webapp config set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "gunicorn app.main_saas:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"

# Set environment variables from .env.azure
echo "Setting environment variables..."
while IFS='=' read -r key value; do
    # Skip empty lines and comments
    if [[ -z "$key" || "$key" == \#* ]]; then
        continue
    fi
    
    # Set environment variable
    az webapp config appsettings set \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --settings "$key=$value"
done < .env.azure

# Build and deploy the application
echo "Building and deploying the application..."

# Create a temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Created temporary directory: $DEPLOY_DIR"

# Copy application files to the deployment directory
cp -r app $DEPLOY_DIR/
cp -r migrations $DEPLOY_DIR/
cp -r scripts $DEPLOY_DIR/
cp -r alembic.ini $DEPLOY_DIR/
cp -r requirements.txt $DEPLOY_DIR/

# Create a deployment script
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
cd $DEPLOY_DIR
zip -r ../deploy.zip .
cd -

# Deploy the zip file
echo "Deploying to App Service..."
az webapp deployment source config-zip \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --src deploy.zip

# Clean up
rm -rf $DEPLOY_DIR
rm deploy.zip

# Get the URL of the deployed application
APP_URL="https://$APP_NAME.azurewebsites.net"

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Your application is available at: $APP_URL${NC}"
echo -e "${GREEN}SaaS application available at: $APP_URL/static/saas/index.html${NC}"
