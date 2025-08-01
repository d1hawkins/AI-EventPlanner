#!/bin/bash
# Deploy the AI Event Planner SaaS application to Azure with REAL agents

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

# Copy the updated files to the deployment directory
echo "Copying updated files to deployment directory..."
mkdir -p $DEPLOY_DIR
cp startup.py $DEPLOY_DIR/
cp wsgi.py $DEPLOY_DIR/
cp web.config $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/
cp run_azure_migrations_fixed.py $DEPLOY_DIR/

# Create a custom startup.sh that ensures dependencies are installed
echo "Creating custom startup.sh..."
cat > $DEPLOY_DIR/startup.sh << 'EOF'
#!/bin/bash
cd /home/site/wwwroot

# Print debugging information
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Python path: $PYTHONPATH"

# Install required dependencies with explicit versions
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install fastapi==0.95.1 uvicorn==0.22.0 gunicorn==20.1.0 sqlalchemy==2.0.9 pydantic==1.10.7 \
    langchain==0.0.267 langgraph==0.0.11 google-generativeai==0.3.1 openai==0.28.1 \
    passlib==1.7.4 python-jose==3.3.0 python-multipart==0.0.6 bcrypt==4.0.1 \
    python-dotenv==1.0.0 psycopg2-binary==2.9.6 email-validator==2.0.0 icalendar==5.0.7 alembic==1.10.4

# Print environment for debugging
echo "Environment variables:"
env | grep -v "PATH" | grep -v "PYTHONPATH"

# Add current directory to Python path
export PYTHONPATH=$PYTHONPATH:/home/site/wwwroot

# List all directories in the current path to help with debugging
echo "Listing directories in current path:"
ls -la
echo "App directory contents:"
ls -la app

# Run database migrations if needed
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    if [ -f "run_azure_migrations_fixed.py" ]; then
        python run_azure_migrations_fixed.py
    else
        echo "Migration script not found, skipping migrations."
    fi
fi

# Check if main_saas.py exists in the app directory
MAIN_SAAS_PATH="app/main_saas.py"
APP_ADAPTER_PATH="app_adapter.py"
MAIN_PATH="app/main.py"

echo "Checking for $MAIN_SAAS_PATH: $([ -f "$MAIN_SAAS_PATH" ] && echo "Found" || echo "Not found")"
echo "Checking for $APP_ADAPTER_PATH: $([ -f "$APP_ADAPTER_PATH" ] && echo "Found" || echo "Not found")"
echo "Checking for $MAIN_PATH: $([ -f "$MAIN_PATH" ] && echo "Found" || echo "Not found")"

# Try to determine which module to use
if [ -f "$MAIN_SAAS_PATH" ]; then
    echo "Found main_saas.py, using app.main_saas:app"
    APP_MODULE="app.main_saas:app"
elif [ -f "$MAIN_PATH" ]; then
    echo "Found main.py, using app.main:app"
    APP_MODULE="app.main:app"
else
    echo "Using app_adapter:app as fallback"
    APP_MODULE="app_adapter:app"
fi

# Run gunicorn with the determined app module
echo "Starting application with $APP_MODULE..."
gunicorn $APP_MODULE --bind=0.0.0.0:8000 --workers=4 --timeout=120
EOF

chmod +x $DEPLOY_DIR/startup.sh

# Use app_adapter_with_agents.py as app_adapter.py for real agent support
echo "Setting up app_adapter with real agent support..."
cp app_adapter_with_agents.py $DEPLOY_DIR/app_adapter.py

# Copy the scripts directory
echo "Copying scripts directory..."
mkdir -p $DEPLOY_DIR/scripts
if [ -d "scripts" ]; then
    cp -r scripts/* $DEPLOY_DIR/scripts/
    # Ensure __init__.py exists in scripts directory
    touch $DEPLOY_DIR/scripts/__init__.py
fi

# Create app directory structure with __init__.py files
echo "Creating app directory structure..."
mkdir -p $DEPLOY_DIR/app
touch $DEPLOY_DIR/app/__init__.py

# Copy the entire app directory with proper structure
echo "Copying app directory with proper structure..."
for dir in agents auth db middleware graphs tools schemas state utils web; do
    if [ -d "app/$dir" ]; then
        echo "Copying app/$dir..."
        mkdir -p $DEPLOY_DIR/app/$dir
        cp -r app/$dir/* $DEPLOY_DIR/app/$dir/
        # Ensure __init__.py exists in each directory
        touch $DEPLOY_DIR/app/$dir/__init__.py
    fi
done

# Copy any Python files in the app root
echo "Copying Python files in app root..."
cp app/*.py $DEPLOY_DIR/app/ 2>/dev/null || :

# Make sure __init__.py exists in all subdirectories
echo "Ensuring __init__.py exists in all subdirectories..."
find $DEPLOY_DIR/app -type d -exec touch {}/__init__.py \;

# Print the list of files being deployed
echo "Files being deployed:"
ls -la $DEPLOY_DIR
echo "App directory contents:"
ls -la $DEPLOY_DIR/app

# Create a zip file for deployment
echo "Creating deployment package..."
cd $DEPLOY_DIR
zip -r ../deploy-full-saas.zip .
cd ..

# Switch to a non-containerized approach
echo "Switching to a non-containerized approach..."
echo "When prompted, type 'y' to confirm deletion of the web app"
az webapp delete --name $APP_NAME --resource-group $RESOURCE_GROUP --keep-empty-plan

# Create a new web app with the non-containerized Python runtime
echo "Creating a new web app with the non-containerized Python runtime..."
az webapp create --name $APP_NAME --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime "PYTHON:$PYTHON_VERSION"

# Deploy to Azure App Service
echo "Deploying to Azure App Service..."
az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $APP_NAME --src deploy-full-saas.zip

# Configure the App Service
echo "Configuring App Service..."
az webapp config set --resource-group $RESOURCE_GROUP --name $APP_NAME --startup-file "startup.sh"

# Set environment variables
echo "Setting critical environment variables..."
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings \
    "ENABLE_AGENT_LOGGING=true" \
    "AGENT_MEMORY_STORAGE=file" \
    "AGENT_MEMORY_PATH=/home/site/wwwroot/agent_memory" \
    "PYTHONPATH=/home/site/wwwroot" \
    "WEBSITE_HTTPLOGGING_RETENTION_DAYS=7" \
    "RUN_MIGRATIONS=false" \
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true"

# Enable logging
echo "Enabling logging..."
az webapp log config --resource-group $RESOURCE_GROUP --name $APP_NAME --application-logging filesystem --detailed-error-messages true --failed-request-tracing true --web-server-logging filesystem

# Restart the app
echo "Restarting the app..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

# Clean up
echo "Cleaning up..."
rm -rf $DEPLOY_DIR
rm -f deploy-full-saas.zip

echo -e "${GREEN}Deployment completed successfully.${NC}"
echo -e "Your application with REAL agents is available at: https://$APP_NAME.azurewebsites.net"
echo -e "Please allow a few minutes for the changes to take effect."
echo -e "You can check the logs at: https://$APP_NAME.scm.azurewebsites.net/api/logs/docker"
