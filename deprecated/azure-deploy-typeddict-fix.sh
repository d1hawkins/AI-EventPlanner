#!/bin/bash
# Script to deploy the TypedDict compatibility fix to Azure

set -e  # Exit immediately if a command exits with a non-zero status

echo "Deploying TypedDict compatibility fix to Azure..."

# Ensure we have the necessary Azure CLI tools
if ! command -v az &> /dev/null; then
    echo "Azure CLI not found. Please install it first."
    exit 1
fi

# Check if we're logged in to Azure
az account show &> /dev/null || {
    echo "Not logged in to Azure. Please run 'az login' first."
    exit 1
}

# Set variables
WEBAPP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"

echo "Deploying to Azure Web App: $WEBAPP_NAME in Resource Group: $RESOURCE_GROUP"

# Verify the web app exists
if ! az webapp show --name "$WEBAPP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    echo "Web app $WEBAPP_NAME not found in resource group $RESOURCE_GROUP"
    exit 1
fi

# Run the verification script locally to ensure the fix works
echo "Verifying the fix locally..."
python3 verify_typeddict_fix.py
if [ $? -ne 0 ]; then
    echo "Local verification failed. Please fix the issues before deploying."
    exit 1
fi

# Create a temporary deployment directory
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Copy the necessary files to the temporary directory
echo "Copying files to temporary directory..."
mkdir -p "$TEMP_DIR/app/graphs"
cp app/graphs/coordinator_graph.py "$TEMP_DIR/app/graphs/"
cp app/graphs/simple_coordinator_graph.py "$TEMP_DIR/app/graphs/"
cp verify_typeddict_fix.py "$TEMP_DIR/"

# Create a simple test script in the temporary directory
cat > "$TEMP_DIR/test_fix.py" << 'EOF'
#!/usr/bin/env python3
"""
Script to test the TypedDict compatibility fix on Azure.
"""
import sys

def test_graphs():
    try:
        # Test simple coordinator graph
        from app.graphs.simple_coordinator_graph import create_coordinator_graph as create_simple_graph
        from app.graphs.simple_coordinator_graph import create_initial_state as create_simple_state
        simple_graph = create_simple_graph()
        simple_state = create_simple_state()
        
        # Test main coordinator graph
        from app.graphs.coordinator_graph import create_coordinator_graph as create_main_graph
        from app.graphs.coordinator_graph import create_initial_state as create_main_state
        main_graph = create_main_graph()
        main_state = create_main_state()
        
        print("TypedDict fix verification successful!")
        return 0
    except Exception as e:
        print(f"Error testing TypedDict fix: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_graphs())
EOF

# Make the test script executable
chmod +x "$TEMP_DIR/test_fix.py"

# Create a zip file for deployment
echo "Creating deployment zip file..."
cd "$TEMP_DIR"
zip -r deployment.zip .
cd - > /dev/null

# Deploy the zip file to Azure
echo "Deploying to Azure..."
az webapp deployment source config-zip --resource-group "$RESOURCE_GROUP" --name "$WEBAPP_NAME" --src "$TEMP_DIR/deployment.zip"

# Clean up the temporary directory
echo "Cleaning up temporary directory..."
rm -rf "$TEMP_DIR"

echo "Deployment completed successfully!"
echo "To verify the fix on Azure, run the following command:"
echo "az webapp ssh --resource-group \"$RESOURCE_GROUP\" --name \"$WEBAPP_NAME\" --command \"python test_fix.py\""

# Optionally, run the verification on Azure
read -p "Do you want to verify the fix on Azure now? (y/n): " VERIFY
if [[ "$VERIFY" == "y" || "$VERIFY" == "Y" ]]; then
    echo "Running verification on Azure..."
    az webapp ssh --resource-group "$RESOURCE_GROUP" --name "$WEBAPP_NAME" --command "python test_fix.py"
fi

echo "TypedDict compatibility fix deployment completed!"
