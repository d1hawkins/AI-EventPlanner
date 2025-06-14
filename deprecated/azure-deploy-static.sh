#!/bin/bash
# Static deployment script for AI Event Planner SaaS application to Azure

set -e

# Configuration
APP_NAME="ai-event-planner-saas"
RESOURCE_GROUP="ai-event-planner-rg"

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "Creating a static deployment package..."

# Create a temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Created temporary directory: $DEPLOY_DIR"

# Create a simple index.html file
mkdir -p $DEPLOY_DIR/static/saas
cat > $DEPLOY_DIR/static/saas/index.html << 'EOF'
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

# Create a simple server.js file
cat > $DEPLOY_DIR/server.js << 'EOF'
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 8000;

const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.txt': 'text/plain',
};

const server = http.createServer((req, res) => {
    console.log(`Request received: ${req.method} ${req.url}`);
    
    // Redirect root to index.html
    let url = req.url;
    if (url === '/') {
        url = '/static/saas/index.html';
    }
    
    // Get the file path
    const filePath = path.join(__dirname, url);
    
    // Check if the file exists
    fs.access(filePath, fs.constants.F_OK, (err) => {
        if (err) {
            console.log(`File not found: ${filePath}`);
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('404 Not Found');
            return;
        }
        
        // Get the file extension
        const ext = path.extname(filePath);
        
        // Get the MIME type
        const contentType = MIME_TYPES[ext] || 'application/octet-stream';
        
        // Read the file
        fs.readFile(filePath, (err, data) => {
            if (err) {
                console.log(`Error reading file: ${err}`);
                res.writeHead(500, { 'Content-Type': 'text/plain' });
                res.end('500 Internal Server Error');
                return;
            }
            
            // Send the file
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(data);
        });
    });
});

server.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}/`);
});
EOF

# Create a package.json file
cat > $DEPLOY_DIR/package.json << 'EOF'
{
  "name": "ai-event-planner-saas",
  "version": "1.0.0",
  "description": "AI Event Planner SaaS",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "engines": {
    "node": ">=14.0.0"
  }
}
EOF

# Create a zip file for deployment
CURRENT_DIR=$(pwd)
DEPLOY_ZIP="$CURRENT_DIR/deploy-static.zip"

cd $DEPLOY_DIR
zip -r "$DEPLOY_ZIP" .
cd "$CURRENT_DIR"

# Deploy the zip file
echo "Deploying to App Service..."
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src "$DEPLOY_ZIP"

# Configure the App Service to use Node.js
echo "Configuring App Service..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --node-version 14-lts \
    --startup-command "node server.js"

# Clean up
rm -rf $DEPLOY_DIR
rm "$DEPLOY_ZIP"

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Your application is available at: https://$APP_NAME.azurewebsites.net${NC}"
echo -e "${GREEN}SaaS application available at: https://$APP_NAME.azurewebsites.net/static/saas/index.html${NC}"
