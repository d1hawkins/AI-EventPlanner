#!/bin/bash
# Script to deploy the fixed version of the application to Azure
# This version includes the TypedDict compatibility fix

set -e  # Exit immediately if a command exits with a non-zero status

echo "=== Deploying Fixed Version to Azure ==="
echo ""

# Set variables
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
DEPLOYMENT_SOURCE="./deploy"
DEPLOYMENT_ZIP="deploy.zip"

# Create deployment directory if it doesn't exist
mkdir -p $DEPLOYMENT_SOURCE

# Copy necessary files to deployment directory
echo "Preparing deployment package..."
cp -r app $DEPLOYMENT_SOURCE/
cp app_adapter.py $DEPLOYMENT_SOURCE/
cp startup.py $DEPLOYMENT_SOURCE/
cp startup.sh $DEPLOYMENT_SOURCE/
cp requirements.txt $DEPLOYMENT_SOURCE/
cp wsgi.py $DEPLOYMENT_SOURCE/
cp -r migrations $DEPLOYMENT_SOURCE/
cp alembic.ini $DEPLOYMENT_SOURCE/

# Verify that the simple_coordinator_graph.py file exists
if [ ! -f "$DEPLOYMENT_SOURCE/app/graphs/simple_coordinator_graph.py" ]; then
    echo "ERROR: simple_coordinator_graph.py not found!"
    echo "Please create this file before deploying."
    exit 1
fi

# Run the verification script
echo "Verifying TypedDict fix..."
python3 verify_typeddict_fix.py
if [ $? -ne 0 ]; then
    echo "Verification failed! Please fix the issues before deploying."
    exit 1
fi

# Create deployment zip
echo "Creating deployment zip..."
cd $DEPLOYMENT_SOURCE
zip -r ../$DEPLOYMENT_ZIP .
cd ..

# Deploy to Azure
echo "Deploying to Azure App Service..."
az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $APP_NAME --src $DEPLOYMENT_ZIP

# Restart the web app
echo "Restarting the web app..."
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME

# Clean up
echo "Cleaning up..."
rm -f $DEPLOYMENT_ZIP

echo ""
echo "Deployment completed successfully!"
echo "To check if the fix is working, run: ./check_azure_logs.sh"
echo ""
echo "For more information about the fix, see AZURE_TYPEDDICT_FIX.md"
