#!/bin/bash

# Quick fix for Azure deployment - update requirements file only
set -e

echo "🔧 Fixing Azure deployment requirements..."

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"

echo "📦 Creating deployment package with fixed requirements..."
DEPLOY_DIR="deploy_fix_$(date +%s)"
mkdir -p $DEPLOY_DIR

# Copy all application files
cp -r app/ $DEPLOY_DIR/
cp -r migrations/ $DEPLOY_DIR/
cp app_adapter_conversational.py $DEPLOY_DIR/
cp requirements_real_agents.txt $DEPLOY_DIR/requirements.txt
cp startup.py $DEPLOY_DIR/

# Create the missing run_saas_with_agents.py file that startup.py expects
cat > $DEPLOY_DIR/run_saas_with_agents.py << 'EOF'
#!/usr/bin/env python3
"""
SaaS application runner with real conversational agents
"""
import os
import sys

def main():
    """Main entry point for SaaS application with agents"""
    print("Starting SaaS application with real conversational agents...")
    
    # Import and run the conversational adapter
    from app_adapter_conversational import app
    import uvicorn
    
    # Get port from environment (Azure sets this)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
EOF

# Create startup script
cat > $DEPLOY_DIR/startup.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting application with real agents..."
echo "Environment: $ENVIRONMENT"
echo "LLM Provider: $LLM_PROVIDER"
echo "Use Real Agents: $USE_REAL_AGENTS"

# Install dependencies
pip install -r requirements.txt

# Start the application
python startup.py
EOF

chmod +x $DEPLOY_DIR/startup.sh

# Deploy to Azure
echo "🚀 Deploying fixed version to Azure..."
cd $DEPLOY_DIR
zip -r ../deployment_fix.zip .
cd ..

az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --src deployment_fix.zip

echo "✅ Fixed deployment uploaded successfully!"
echo "🌐 Application URL: https://${APP_NAME}.azurewebsites.net"

# Cleanup
rm -rf $DEPLOY_DIR deployment_fix.zip

echo "🏁 Requirements fix deployment completed!"
