#!/bin/bash

# Azure Direct Deployment Script
# This script deploys the AI Event Planner SaaS app directly to Azure

# Don't exit on error - we'll handle errors manually
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
DEPLOY_DIR="deploy"
DEPLOY_ZIP="deploy.zip"

echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Azure Direct Deployment Script          ║${NC}"
echo -e "${BLUE}║  AI Event Planner SaaS                    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Clean up any previous deployment artifacts
echo -e "${YELLOW}[1/5]${NC} Cleaning up previous deployment artifacts..."
rm -rf "$DEPLOY_DIR" "$DEPLOY_ZIP" 2>/dev/null || true
echo -e "${GREEN}✓${NC} Cleanup complete"
echo ""

# Step 2: Create deployment directory and copy files
echo -e "${YELLOW}[2/5]${NC} Creating deployment package..."
mkdir -p "$DEPLOY_DIR"

# Copy application files
cp -r app migrations scripts alembic.ini requirements.txt startup.sh "$DEPLOY_DIR/"

# Create the deployment zip
cd "$DEPLOY_DIR"
zip -r ../"$DEPLOY_ZIP" . > /dev/null
cd ..

PACKAGE_SIZE=$(ls -lh "$DEPLOY_ZIP" | awk '{print $5}')
echo -e "${GREEN}✓${NC} Deployment package created: $PACKAGE_SIZE"
echo ""

# Step 3: Deploy to Azure
echo -e "${YELLOW}[3/5]${NC} Deploying to Azure..."
echo -e "   ${BLUE}→${NC} Resource Group: $RESOURCE_GROUP"
echo -e "   ${BLUE}→${NC} App Name: $APP_NAME"
echo ""

# Try deployment without async flag for better error reporting
echo -e "   ${BLUE}→${NC} Starting deployment (this may take a few minutes)..."
if az webapp deploy \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --src-path "$DEPLOY_ZIP" \
  --type zip; then
    
    echo -e "${GREEN}✓${NC} Deployment completed successfully"
    echo ""
else
    DEPLOY_EXIT_CODE=$?
    echo -e "${RED}✗${NC} Deployment failed (exit code: $DEPLOY_EXIT_CODE)"
    echo ""
    echo -e "${YELLOW}This is a known Azure CLI issue. Use GitHub Actions instead:${NC}"
    echo -e "  1. Commit your changes: ${BLUE}git add . && git commit -m 'Deploy'${NC}"
    echo -e "  2. Push to GitHub: ${BLUE}git push origin main${NC}"
    echo -e "  3. GitHub Actions will deploy automatically"
    echo ""
    echo -e "${BLUE}Or try these alternatives:${NC}"
    echo -e "  • Upgrade Azure CLI: ${BLUE}brew upgrade azure-cli${NC}"
    echo -e "  • Use Azure Portal to deploy the zip file manually"
    echo -e "  • Use: ${BLUE}az webapp up${NC} command instead"
    echo ""
    # Clean up
    rm -rf "$DEPLOY_DIR" "$DEPLOY_ZIP"
    exit 1
fi

# Step 4: Clean up temporary files
echo -e "${YELLOW}[4/5]${NC} Cleaning up temporary files..."
rm -rf "$DEPLOY_DIR" "$DEPLOY_ZIP"
echo -e "${GREEN}✓${NC} Temporary files removed"
echo ""

# Step 5: Show deployment status
echo -e "${YELLOW}[5/5]${NC} Checking deployment status..."
echo ""

APP_STATE=$(az webapp show \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "state" \
  --output tsv)

APP_URL=$(az webapp show \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "defaultHostName" \
  --output tsv)

echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Deployment Complete!                     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BLUE}App Status:${NC} $APP_STATE"
echo -e "  ${BLUE}App URL:${NC} https://$APP_URL"
echo ""
echo -e "${YELLOW}Note:${NC} The build process may take 10-15 minutes to complete."
echo -e "      You can monitor logs with:"
echo ""
echo -e "      ${BLUE}az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP${NC}"
echo ""
echo -e "${GREEN}✓${NC} Deployment script completed successfully!"
echo ""
