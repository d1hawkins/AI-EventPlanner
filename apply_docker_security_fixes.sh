#!/bin/bash
# Script to apply Docker security fixes for Azure deployment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Applying Docker security fixes for Azure deployment...${NC}"

# Check if the fixed files exist
if [ ! -f "Dockerfile.saas.fixed" ]; then
    echo -e "${RED}Error: Dockerfile.saas.fixed not found.${NC}"
    exit 1
fi

if [ ! -f "azure-deploy-docker.sh.fixed" ]; then
    echo -e "${RED}Error: azure-deploy-docker.sh.fixed not found.${NC}"
    exit 1
fi

if [ ! -f "entrypoint.sh" ]; then
    echo -e "${RED}Error: entrypoint.sh not found.${NC}"
    exit 1
fi

if [ ! -f "scripts/create_azure_tables_direct_fixed.py" ]; then
    echo -e "${RED}Error: scripts/create_azure_tables_direct_fixed.py not found.${NC}"
    exit 1
fi

if [ ! -f "scripts/setup_azure_db_complete_fixed.py" ]; then
    echo -e "${RED}Error: scripts/setup_azure_db_complete_fixed.py not found.${NC}"
    exit 1
fi

if [ ! -f ".github/workflows/azure-deploy-docker.yml.fixed" ]; then
    echo -e "${YELLOW}Warning: .github/workflows/azure-deploy-docker.yml.fixed not found. GitHub Actions workflow will not be updated.${NC}"
fi

# Backup original files
echo "Creating backups of original files..."
if [ -f "Dockerfile.saas" ]; then
    cp Dockerfile.saas Dockerfile.saas.backup
    echo "Backed up Dockerfile.saas to Dockerfile.saas.backup"
fi

if [ -f "azure-deploy-docker.sh" ]; then
    cp azure-deploy-docker.sh azure-deploy-docker.sh.backup
    echo "Backed up azure-deploy-docker.sh to azure-deploy-docker.sh.backup"
fi

if [ -f ".github/workflows/azure-deploy-docker.yml" ]; then
    cp .github/workflows/azure-deploy-docker.yml .github/workflows/azure-deploy-docker.yml.backup
    echo "Backed up .github/workflows/azure-deploy-docker.yml to .github/workflows/azure-deploy-docker.yml.backup"
fi

# Replace original files with fixed versions
echo "Replacing original files with fixed versions..."
cp Dockerfile.saas.fixed Dockerfile.saas
echo "Replaced Dockerfile.saas with fixed version"

cp azure-deploy-docker.sh.fixed azure-deploy-docker.sh
chmod +x azure-deploy-docker.sh
echo "Replaced azure-deploy-docker.sh with fixed version and made it executable"

# Make sure the entrypoint script is executable
chmod +x entrypoint.sh
echo "Made entrypoint.sh executable"

# Make sure the Python scripts are executable
chmod +x scripts/create_azure_tables_direct_fixed.py
chmod +x scripts/setup_azure_db_complete_fixed.py
echo "Made Python scripts executable"

if [ -f ".github/workflows/azure-deploy-docker.yml.fixed" ]; then
    mkdir -p .github/workflows
    cp .github/workflows/azure-deploy-docker.yml.fixed .github/workflows/azure-deploy-docker.yml
    echo "Replaced .github/workflows/azure-deploy-docker.yml with fixed version"
fi

echo -e "${GREEN}Docker security fixes applied successfully!${NC}"
echo -e "${YELLOW}Please review the changes and make sure your .env.saas file is up to date with all required environment variables.${NC}"
echo -e "${YELLOW}To deploy the application to Azure, run:${NC}"
echo -e "${GREEN}./azure-deploy-docker.sh${NC}"
echo -e "${YELLOW}For more information, see AZURE_DOCKER_DEPLOYMENT_SECURITY_FIX.md${NC}"
