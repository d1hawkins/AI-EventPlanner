#!/bin/bash
# Custom deployment script for AI Event Planner SaaS application to Azure

set -e

# Configuration
APP_NAME="ai-event-planner-saas"
RESOURCE_GROUP="ai-event-planner-rg"

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "Creating a custom deployment package..."

# Create a temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Created temporary directory: $DEPLOY_DIR"

# Copy application files to the deployment directory
cp -r app $DEPLOY_DIR/
cp -r migrations $DEPLOY_DIR/
cp -r scripts $DEPLOY_DIR/
cp -r alembic.ini $DEPLOY_DIR/
cp -r app/web/static $DEPLOY_DIR/static

# Create a requirements.txt file with all necessary packages explicitly listed
cat > $DEPLOY_DIR/requirements.txt << 'EOF'
# FastAPI and dependencies
fastapi==0.68.0
uvicorn==0.15.0
gunicorn==20.1.0
python-multipart==0.0.5
pydantic==1.8.0
email-validator==1.1.3

# Database
sqlalchemy==1.4.23
alembic==1.7.1
psycopg2-binary==2.9.1

# Authentication
python-jose==3.3.0
passlib==1.7.4
bcrypt==3.2.0
python-dotenv==0.19.0

# Azure Storage
azure-storage-blob==12.9.0

# Additional dependencies
requests==2.26.0
aiohttp==3.7.4
jinja2==3.0.1
EOF

# Create a startup.py script
cat > $DEPLOY_DIR/startup.py << 'EOF'
import os
import sys
import subprocess
import time

def main():
    print("Starting deployment process...")
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Run database migrations
    print("Running database migrations...")
    try:
        subprocess.check_call([sys.executable, "-m", "scripts.migrate"])
    except Exception as e:
        print(f"Warning: Migration failed: {e}")
    
    # Start the application
    print("Starting the application...")
    os.environ["PORT"] = "8000"
    subprocess.check_call([
        sys.executable, "-m", "uvicorn", "app.main_saas:app", 
        "--host", "0.0.0.0", "--port", "8000"
    ])

if __name__ == "__main__":
    main()
EOF

# Create a zip file for deployment
CURRENT_DIR=$(pwd)
DEPLOY_ZIP="$CURRENT_DIR/deploy-custom.zip"

cd $DEPLOY_DIR
zip -r "$DEPLOY_ZIP" .
cd "$CURRENT_DIR"

# Deploy the zip file
echo "Deploying to App Service..."
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src "$DEPLOY_ZIP"

# Configure the App Service to use Python and the startup script
echo "Configuring App Service..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-command "python startup.py"

# Clean up
rm -rf $DEPLOY_DIR
rm "$DEPLOY_ZIP"

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Your application is available at: https://$APP_NAME.azurewebsites.net${NC}"
echo -e "${GREEN}SaaS application available at: https://$APP_NAME.azurewebsites.net/static/saas/index.html${NC}"
