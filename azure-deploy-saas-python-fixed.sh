#!/bin/bash
# Deploy the AI Event Planner SaaS application to Azure using Python-specific configuration

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

# Check if .env.azure.fixed file exists
if [ ! -f .env.azure.fixed ]; then
    echo -e "${YELLOW}No .env.azure.fixed file found. Using .env.azure.fixed...${NC}"
    if [ ! -f .env.azure.fixed ]; then
        echo -e "${RED}No .env.azure.fixed file found. Please create a .env.azure.fixed file manually.${NC}"
        exit 1
    fi
fi

# Load environment variables from .env.azure.fixed
echo "Loading environment variables from .env.azure.fixed..."
# Using source instead of export to properly handle quoted values
source .env.azure.fixed

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
    
    # Update .env.azure.fixed with PostgreSQL connection string
    POSTGRES_HOST="$POSTGRES_SERVER_NAME.postgres.database.azure.com"
    POSTGRES_CONNECTION_STRING="postgresql://$POSTGRES_ADMIN_USER@$POSTGRES_SERVER_NAME:$POSTGRES_ADMIN_PASSWORD@$POSTGRES_HOST/$POSTGRES_DB_NAME"
    
    # Update .env.azure.fixed file
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=\"$POSTGRES_CONNECTION_STRING\"|g" .env.azure.fixed
    
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
    
    # Update .env.azure.fixed file
    sed -i "s|STORAGE_CONNECTION_STRING=.*|STORAGE_CONNECTION_STRING=\"$STORAGE_CONNECTION_STRING\"|g" .env.azure.fixed
    
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

# Set environment variables from .env.azure.fixed
echo "Setting environment variables..."
while IFS='=' read -r key value; do
    # Skip empty lines and comments
    if [[ -z "$key" || "$key" == \#* ]]; then
        continue
    fi
    
    # Extract the key (remove any leading/trailing whitespace)
    key=$(echo "$key" | xargs)
    
    # Extract the value (remove quotes if present)
    value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
    
    # Set environment variable
    az webapp config appsettings set \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --settings "$key=$value"
done < .env.azure.fixed

# Create a temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Created temporary directory: $DEPLOY_DIR"

# Copy application files to the deployment directory
cp -r app $DEPLOY_DIR/
cp -r migrations $DEPLOY_DIR/
cp -r scripts $DEPLOY_DIR/
cp -r alembic.ini $DEPLOY_DIR/

# Create an updated requirements.txt file with all necessary packages
cat > $DEPLOY_DIR/requirements.txt << 'EOF'
# FastAPI and dependencies
fastapi>=0.68.0,<0.69.0
uvicorn>=0.15.0,<0.16.0
gunicorn>=20.1.0,<20.2.0
python-multipart>=0.0.5,<0.1.0
pydantic>=1.8.0,<1.9.0
email-validator>=1.1.3,<1.2.0

# Database
sqlalchemy>=1.4.23,<1.5.0
alembic>=1.7.1,<1.8.0
psycopg2-binary>=2.9.1,<2.10.0

# Authentication
python-jose>=3.3.0,<3.4.0
passlib>=1.7.4,<1.8.0
bcrypt>=3.2.0,<3.3.0
python-dotenv>=0.19.0,<0.20.0

# Azure Storage
azure-storage-blob>=12.9.0,<12.10.0

# Additional dependencies
requests>=2.26.0,<2.27.0
aiohttp>=3.7.4,<3.8.0
jinja2>=3.0.1,<3.1.0
EOF

# Create a startup script
cat > $DEPLOY_DIR/startup.sh << 'EOF'
#!/bin/bash
set -e

# Run database migrations
python -m scripts.migrate

# Start the application
gunicorn app.main_saas:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
EOF

chmod +x $DEPLOY_DIR/startup.sh

# Create a .deployment file to specify the deployment approach
cat > $DEPLOY_DIR/.deployment << 'EOF'
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
EOF

# Create a .python_packages directory to ensure Python packages are installed
mkdir -p $DEPLOY_DIR/.python_packages

# Create a zip file for deployment
CURRENT_DIR=$(pwd)
DEPLOY_ZIP="$CURRENT_DIR/deploy.zip"

cd $DEPLOY_DIR
zip -r "$DEPLOY_ZIP" .
cd "$CURRENT_DIR"

# Deploy the zip file
echo "Deploying to App Service..."
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src "$DEPLOY_ZIP"

# Configure the App Service to use Python 3.9 and the startup command
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --linux-fx-version "PYTHON|3.9" \
    --startup-file "startup.sh"

# Enable local cache to improve performance
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings WEBSITE_LOCAL_CACHE_OPTION=Always

# Enable SCM_DO_BUILD_DURING_DEPLOYMENT to ensure packages are installed
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Clean up
rm -rf $DEPLOY_DIR
rm "$DEPLOY_ZIP"

# Get the URL of the deployed application
APP_URL="https://$APP_NAME.azurewebsites.net"

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Your application is available at: $APP_URL${NC}"
echo -e "${GREEN}SaaS application available at: $APP_URL/static/saas/index.html${NC}"
