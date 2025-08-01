#!/bin/bash
set -e

echo "=== Deploy Fixed App to Azure ==="
echo "Timestamp: $(date)"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    log "ERROR: Azure CLI is not installed. Please install it first:"
    log "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    log "ERROR: Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

# Configuration - Update these values for your Azure App Service
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-your-resource-group}"
APP_NAME="${AZURE_APP_NAME:-your-app-name}"

log "Deploying to Azure App Service: $APP_NAME in resource group: $RESOURCE_GROUP"

# Validate that the fixed files exist
log "Validating fixed files exist..."

critical_files=(
    "app_adapter_with_agents_fixed.py"
    "azure_import_diagnostics.py"
    "app/agents/agent_router.py"
    "app/agents/api_router.py"
    "app/agents/agent_factory.py"
)

missing_files=0
for file in "${critical_files[@]}"; do
    if [ ! -f "$file" ]; then
        log "ERROR: Critical file missing: $file"
        missing_files=$((missing_files + 1))
    else
        log "✓ Found: $file"
    fi
done

if [ $missing_files -gt 0 ]; then
    log "ERROR: $missing_files critical files are missing. Cannot deploy."
    exit 1
fi

# Create a temporary deployment directory
DEPLOY_DIR="azure_deployment_$(date +%Y%m%d_%H%M%S)"
log "Creating deployment directory: $DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Copy all necessary files to deployment directory
log "Copying files to deployment directory..."

# Copy the fixed app adapter as the main app file
cp "app_adapter_with_agents_fixed.py" "$DEPLOY_DIR/app.py"
log "✓ Copied fixed app adapter as app.py"

# Copy diagnostic files
cp "azure_import_diagnostics.py" "$DEPLOY_DIR/"
log "✓ Copied diagnostics"

# Copy the entire app directory
if [ -d "app" ]; then
    cp -r "app" "$DEPLOY_DIR/"
    log "✓ Copied app directory"
else
    log "ERROR: app directory not found"
    exit 1
fi

# Copy configuration files
config_files=(
    "requirements.txt"
    "requirements_complete.txt"
    ".env.example"
    "alembic.ini"
    "langgraph.json"
)

for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$DEPLOY_DIR/"
        log "✓ Copied: $file"
    else
        log "WARNING: Config file not found: $file"
    fi
done

# Copy migrations if they exist
if [ -d "migrations" ]; then
    cp -r "migrations" "$DEPLOY_DIR/"
    log "✓ Copied migrations directory"
fi

# Copy scripts if they exist
if [ -d "scripts" ]; then
    cp -r "scripts" "$DEPLOY_DIR/"
    log "✓ Copied scripts directory"
fi

# Create a startup script for Azure
log "Creating Azure startup script..."
cat > "$DEPLOY_DIR/startup.sh" << 'EOF'
#!/bin/bash
echo "Starting Azure App Service with fixed agent system..."

# Set Python path
export PYTHONPATH="/home/site/wwwroot:/home/site/wwwroot/app:/home/site/wwwroot/app/agents:/home/site/wwwroot/app/graphs:/home/site/wwwroot/app/tools:/home/site/wwwroot/app/utils:/home/site/wwwroot/app/db:/home/site/wwwroot/app/middleware"

echo "Python path set to: $PYTHONPATH"

# Run diagnostics
echo "Running import diagnostics..."
cd /home/site/wwwroot
python azure_import_diagnostics.py || echo "Diagnostics completed with warnings"

# Start the application
echo "Starting application..."
python -m gunicorn --bind=0.0.0.0 --timeout 600 app:app
EOF

chmod +x "$DEPLOY_DIR/startup.sh"
log "✓ Created startup script"

# Create web.config for Azure App Service
log "Creating web.config for Azure..."
cat > "$DEPLOY_DIR/web.config" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="D:\home\Python\python.exe"
                  arguments="D:\home\site\wwwroot\app.py"
                  stdoutLogEnabled="true"
                  stdoutLogFile="D:\home\LogFiles\python.log"
                  startupTimeLimit="60"
                  requestTimeout="00:04:00">
      <environmentVariables>
        <environmentVariable name="PYTHONPATH" value="D:\home\site\wwwroot;D:\home\site\wwwroot\app;D:\home\site\wwwroot\app\agents;D:\home\site\wwwroot\app\graphs;D:\home\site\wwwroot\app\tools;D:\home\site\wwwroot\app\utils;D:\home\site\wwwroot\app\db;D:\home\site\wwwroot\app\middleware" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
EOF

log "✓ Created web.config"

# Deploy to Azure using ZIP deployment
log "Deploying to Azure App Service..."

# Create ZIP file
ZIP_FILE="${DEPLOY_DIR}.zip"
log "Creating deployment ZIP: $ZIP_FILE"
cd "$DEPLOY_DIR"
zip -r "../$ZIP_FILE" . > /dev/null
cd ..

log "Uploading to Azure App Service: $APP_NAME"

# Deploy using Azure CLI
az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src "$ZIP_FILE"

if [ $? -eq 0 ]; then
    log "✅ Deployment successful!"
    
    # Wait a moment for deployment to complete
    log "Waiting for deployment to complete..."
    sleep 10
    
    # Test the deployment
    log "Testing deployment..."
    APP_URL="https://${APP_NAME}.azurewebsites.net"
    
    log "Testing health endpoint: $APP_URL/health"
    if curl -s "$APP_URL/health" > /dev/null; then
        log "✅ Health endpoint responding"
    else
        log "⚠️ Health endpoint not responding yet (may take a few minutes)"
    fi
    
    log "Your application is deployed at: $APP_URL"
    log "Health check: $APP_URL/health"
    log "Agent chat: $APP_URL/agents.html"
    
else
    log "❌ Deployment failed!"
    exit 1
fi

# Cleanup
log "Cleaning up temporary files..."
rm -rf "$DEPLOY_DIR"
rm -f "$ZIP_FILE"

log "=== Deployment Complete ==="
log "Next steps:"
log "1. Check your app at: https://${APP_NAME}.azurewebsites.net"
log "2. Monitor logs: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
log "3. Test agent functionality through the web interface"

echo ""
echo "🎉 Fixed application deployed successfully to Azure!"
echo "🔗 URL: https://${APP_NAME}.azurewebsites.net"
echo "🏥 Health: https://${APP_NAME}.azurewebsites.net/health"
