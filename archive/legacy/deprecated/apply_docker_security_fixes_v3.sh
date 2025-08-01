#!/bin/bash
# Script to apply Docker security fixes V3 for Azure deployment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Applying Docker security fixes V3 for Azure deployment...${NC}"

# Check if the fixed files exist
if [ ! -f "entrypoint.sh" ]; then
    echo -e "${RED}Error: entrypoint.sh not found.${NC}"
    exit 1
fi

if [ ! -f "enable_azure_logging.sh" ]; then
    echo -e "${RED}Error: enable_azure_logging.sh not found.${NC}"
    exit 1
fi

if [ ! -f "Dockerfile.saas.fixed.v2" ]; then
    echo -e "${RED}Error: Dockerfile.saas.fixed.v2 not found.${NC}"
    exit 1
fi

# Backup original files
echo "Creating backups of original files..."
if [ -f "app/middleware/tenant.py" ]; then
    cp app/middleware/tenant.py app/middleware/tenant.py.backup
    echo "Backed up app/middleware/tenant.py to app/middleware/tenant.py.backup"
fi

if [ -f "Dockerfile.saas" ]; then
    cp Dockerfile.saas Dockerfile.saas.backup
    echo "Backed up Dockerfile.saas to Dockerfile.saas.backup"
fi

# Replace Dockerfile with the new version
cp Dockerfile.saas.fixed.v2 Dockerfile.saas
echo "Replaced Dockerfile.saas with fixed version V2"

# Make sure the scripts are executable
chmod +x entrypoint.sh
chmod +x enable_azure_logging.sh
echo "Made scripts executable"

# Apply the previous fixes if they haven't been applied yet
if [ -f "apply_docker_security_fixes.sh" ]; then
    echo "Applying previous Docker security fixes..."
    ./apply_docker_security_fixes.sh
    echo "Previous Docker security fixes applied successfully!"
fi

echo -e "${GREEN}Docker security fixes V3 applied successfully!${NC}"
echo -e "${YELLOW}Please review the changes and make sure your .env.saas file is up to date with all required environment variables.${NC}"
echo -e "${YELLOW}To enable detailed logging in Azure, run:${NC}"
echo -e "${GREEN}./enable_azure_logging.sh${NC}"
echo -e "${YELLOW}To deploy the application to Azure, run:${NC}"
echo -e "${GREEN}./azure-deploy-docker.sh${NC}"
echo -e "${YELLOW}For more information, see AZURE_DOCKER_DEPLOYMENT_FIXES_V2.md${NC}"
