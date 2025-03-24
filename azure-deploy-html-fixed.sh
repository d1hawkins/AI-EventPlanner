#!/bin/bash
# Static HTML deployment script for AI Event Planner SaaS application to Azure

set -e

# Configuration
APP_NAME="ai-event-planner-saas"
RESOURCE_GROUP="ai-event-planner-rg"

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "Creating a static HTML deployment package..."

# Create a temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Created temporary directory: $DEPLOY_DIR"

# Create a simple index.html file
mkdir -p $DEPLOY_DIR/wwwroot
cat > $DEPLOY_DIR/wwwroot/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Event Planner SaaS</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            color: #333;
            background-color: #f4f7f9;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background-color: #2c3e50;
            color: white;
            padding: 1rem 0;
            text-align: center;
        }
        h1 {
            margin: 0;
        }
        .content {
            background-color: white;
            padding: 2rem;
            margin-top: 2rem;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .feature {
            margin-bottom: 2rem;
        }
        .feature h2 {
            color: #2c3e50;
        }
        footer {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem 0;
            background-color: #2c3e50;
            color: white;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>AI Event Planner SaaS</h1>
            <p>Your intelligent event planning solution</p>
        </div>
    </header>

    <div class="container">
        <div class="content">
            <div class="feature">
                <h2>Welcome to AI Event Planner SaaS</h2>
                <p>This is a placeholder page for the AI Event Planner SaaS application. The full application is currently being deployed to Azure.</p>
                <p>The application has been successfully deployed to Azure App Service and is now running.</p>
            </div>
            
            <div class="feature">
                <h2>Features</h2>
                <ul>
                    <li>Intelligent event planning with AI assistance</li>
                    <li>Resource management and allocation</li>
                    <li>Budget tracking and financial planning</li>
                    <li>Stakeholder management</li>
                    <li>Marketing and communications planning</li>
                    <li>Compliance and security management</li>
                    <li>Analytics and reporting</li>
                </ul>
            </div>
        </div>
    </div>

    <footer>
        <div class="container">
            <p>&copy; 2025 AI Event Planner SaaS. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
EOF

# Create a web.config file for static website
cat > $DEPLOY_DIR/wwwroot/web.config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <staticContent>
      <mimeMap fileExtension=".json" mimeType="application/json" />
    </staticContent>
    <handlers>
      <clear />
      <add name="StaticFile" path="*" verb="*" modules="StaticFileModule" resourceType="File" requireAccess="Read" />
    </handlers>
    <rewrite>
      <rules>
        <rule name="Redirect to index.html">
          <match url="^$" />
          <action type="Redirect" url="index.html" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
EOF

# Create a zip file for deployment
CURRENT_DIR=$(pwd)
DEPLOY_ZIP="$CURRENT_DIR/deploy-html.zip"

cd $DEPLOY_DIR
zip -r "$DEPLOY_ZIP" .
cd "$CURRENT_DIR"

# Deploy the zip file
echo "Deploying to App Service..."
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src "$DEPLOY_ZIP"

# Configure the App Service to use static website
echo "Configuring App Service..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file ""

# Clean up
rm -rf $DEPLOY_DIR
rm "$DEPLOY_ZIP"

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Your application is available at: https://$APP_NAME.azurewebsites.net${NC}"
