#!/bin/bash

# GitHub Secrets Setup Script for AI Event Planner
# This script helps you verify and set up required GitHub secrets

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  GitHub Secrets Setup Helper              ║${NC}"
echo -e "${BLUE}║  AI Event Planner SaaS                    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Get repository info
REPO_OWNER=$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\/.*/\1/')
REPO_NAME=$(git config --get remote.origin.url | sed 's/.*\/\(.*\)\.git/\1/' | sed 's/.*\/\(.*\)/\1/')

if [ -z "$REPO_OWNER" ] || [ -z "$REPO_NAME" ]; then
    echo -e "${RED}✗${NC} Could not determine GitHub repository information"
    echo "   Make sure you're in a git repository with a GitHub remote"
    exit 1
fi

echo -e "${GREEN}Repository:${NC} $REPO_OWNER/$REPO_NAME"
echo ""

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    echo -e "${GREEN}✓${NC} GitHub CLI is installed"
    
    # Check authentication
    if gh auth status &> /dev/null; then
        echo -e "${GREEN}✓${NC} GitHub CLI is authenticated"
        echo ""
        
        echo -e "${BLUE}Checking existing secrets...${NC}"
        echo ""
        
        # List secrets
        SECRETS=$(gh secret list -R "$REPO_OWNER/$REPO_NAME" 2>/dev/null || echo "")
        
        if [ -n "$SECRETS" ]; then
            echo "Existing secrets:"
            echo "$SECRETS"
        else
            echo -e "${YELLOW}No secrets found or unable to list secrets${NC}"
        fi
        echo ""
        
        # Check for required secrets
        REQUIRED_SECRETS=(
            "AZURE_CREDENTIALS"
            "AZURE_RESOURCE_GROUP"
            "AZURE_LOCATION"
            "DATABASE_URL"
            "SECRET_KEY"
            "OPENAI_API_KEY"
            "GOOGLE_API_KEY"
            "TAVILY_API_KEY"
        )
        
        echo -e "${BLUE}Checking required secrets for real agents:${NC}"
        MISSING_SECRETS=()
        
        for secret in "${REQUIRED_SECRETS[@]}"; do
            if echo "$SECRETS" | grep -q "^$secret"; then
                echo -e "  ${GREEN}✓${NC} $secret is set"
            else
                echo -e "  ${RED}✗${NC} $secret is missing"
                MISSING_SECRETS+=("$secret")
            fi
        done
        echo ""
        
        if [ ${#MISSING_SECRETS[@]} -eq 0 ]; then
            echo -e "${GREEN}✓${NC} All required secrets are configured!"
            echo ""
            echo "You can deploy by running:"
            echo -e "  ${BLUE}./scripts/deploy_via_github.sh${NC}"
            exit 0
        fi
        
        echo -e "${YELLOW}Missing ${#MISSING_SECRETS[@]} secret(s)${NC}"
        echo ""
        echo "Would you like to set up the missing secrets now? (y/n)"
        read -r response
        
        if [[ "$response" =~ ^[Yy]$ ]]; then
            for secret in "${MISSING_SECRETS[@]}"; do
                echo ""
                echo -e "${BLUE}Setting up $secret${NC}"
                
                case $secret in
                    "AZURE_CREDENTIALS")
                        echo "This should be a JSON string with your Azure service principal credentials."
                        echo "Get it by running: az ad sp create-for-rbac --name 'github-actions' --role contributor --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} --sdk-auth"
                        echo ""
                        echo "Paste the JSON output (it will not be displayed):"
                        ;;
                    "AZURE_RESOURCE_GROUP")
                        echo "Enter your Azure resource group name (e.g., 'ai-event-planner-rg'):"
                        ;;
                    "AZURE_LOCATION")
                        echo "Enter your Azure location (e.g., 'eastus', 'westus2'):"
                        ;;
                    "DATABASE_URL")
                        echo "Enter your PostgreSQL connection string:"
                        echo "Format: postgresql://username:password@host:port/database?sslmode=require"
                        echo ""
                        echo "Paste connection string (it will not be displayed):"
                        ;;
                    "SECRET_KEY")
                        echo "Enter a secret key for JWT tokens (or press Enter to generate one):"
                        ;;
                    "OPENAI_API_KEY")
                        echo "Enter your OpenAI API key (starts with 'sk-'):"
                        echo "Get it from: https://platform.openai.com/api-keys"
                        echo ""
                        echo "Paste API key (it will not be displayed):"
                        ;;
                    "GOOGLE_API_KEY")
                        echo "Enter your Google AI API key:"
                        echo "Get it from: https://aistudio.google.com/app/apikey"
                        echo ""
                        echo "Paste API key (it will not be displayed):"
                        ;;
                    "TAVILY_API_KEY")
                        echo "Enter your Tavily API key:"
                        echo "Get it from: https://tavily.com/"
                        echo ""
                        echo "Paste API key (it will not be displayed):"
                        ;;
                esac
                
                # Read secret value
                if [ "$secret" = "SECRET_KEY" ]; then
                    read -r secret_value
                    if [ -z "$secret_value" ]; then
                        # Generate a random secret key
                        secret_value=$(openssl rand -hex 32)
                        echo "Generated random secret key"
                    fi
                else
                    read -rs secret_value
                fi
                
                # Set the secret
                if [ -n "$secret_value" ]; then
                    echo "$secret_value" | gh secret set "$secret" -R "$REPO_OWNER/$REPO_NAME"
                    echo -e "${GREEN}✓${NC} $secret has been set"
                else
                    echo -e "${YELLOW}⊘${NC} Skipped $secret (no value provided)"
                fi
            done
            
            echo ""
            echo -e "${GREEN}✓${NC} Secret setup complete!"
            echo ""
            echo "You can now deploy by running:"
            echo -e "  ${BLUE}./scripts/deploy_via_github.sh${NC}"
        else
            echo "Secret setup cancelled"
            echo ""
            echo "To set secrets manually, visit:"
            echo "https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
        fi
    else
        echo -e "${YELLOW}⊘${NC} GitHub CLI is not authenticated"
        echo "   Run: ${BLUE}gh auth login${NC}"
        echo ""
        SHOW_MANUAL_INSTRUCTIONS=true
    fi
else
    echo -e "${YELLOW}⊘${NC} GitHub CLI is not installed"
    echo "   Install it from: https://cli.github.com/"
    echo "   Or use Homebrew: ${BLUE}brew install gh${NC}"
    echo ""
    SHOW_MANUAL_INSTRUCTIONS=true
fi

if [ "$SHOW_MANUAL_INSTRUCTIONS" = true ]; then
    echo -e "${BLUE}Manual Setup Instructions:${NC}"
    echo ""
    echo "1. Go to your repository settings:"
    echo "   https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
    echo ""
    echo "2. Click 'New repository secret' and add the following secrets:"
    echo ""
    echo -e "   ${GREEN}AZURE_CREDENTIALS${NC}"
    echo "   Get by running: az ad sp create-for-rbac --name 'github-actions' --role contributor --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} --sdk-auth"
    echo ""
    echo -e "   ${GREEN}AZURE_RESOURCE_GROUP${NC}"
    echo "   Your Azure resource group name (e.g., 'ai-event-planner-rg')"
    echo ""
    echo -e "   ${GREEN}AZURE_LOCATION${NC}"
    echo "   Your Azure location (e.g., 'eastus', 'westus2')"
    echo ""
    echo -e "   ${GREEN}DATABASE_URL${NC}"
    echo "   PostgreSQL connection string: postgresql://user:pass@host:5432/db?sslmode=require"
    echo ""
    echo -e "   ${GREEN}SECRET_KEY${NC}"
    echo "   Generate with: openssl rand -hex 32"
    echo ""
    echo -e "   ${GREEN}OPENAI_API_KEY${NC}"
    echo "   Get from: https://platform.openai.com/api-keys"
    echo ""
    echo -e "   ${GREEN}GOOGLE_API_KEY${NC}"
    echo "   Get from: https://aistudio.google.com/app/apikey"
    echo ""
    echo -e "   ${GREEN}TAVILY_API_KEY${NC}"
    echo "   Get from: https://tavily.com/"
    echo ""
    echo "3. After setting all secrets, deploy with:"
    echo "   ${BLUE}./scripts/deploy_via_github.sh${NC}"
fi
