#!/bin/bash

# GitHub Actions Deployment Script for AI Event Planner
# This script commits changes and pushes to trigger GitHub Actions deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  GitHub Actions Deployment                ║${NC}"
echo -e "${BLUE}║  AI Event Planner SaaS                    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}✗${NC} Not in a git repository"
    exit 1
fi

# Get repository info
REPO_OWNER=$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\/.*/\1/')
REPO_NAME=$(git config --get remote.origin.url | sed 's/.*\/\(.*\)\.git/\1/' | sed 's/.*\/\(.*\)/\1/')

echo -e "${GREEN}Repository:${NC} $REPO_OWNER/$REPO_NAME"
echo ""

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}You have uncommitted changes:${NC}"
    git status -s
    echo ""
    echo "Would you like to commit these changes? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Enter commit message:"
        read -r commit_message
        
        if [ -z "$commit_message" ]; then
            commit_message="Deploy updates to Azure"
        fi
        
        git add .
        git commit -m "$commit_message"
        echo -e "${GREEN}✓${NC} Changes committed"
    else
        echo ""
        echo "Would you like to continue with deployment anyway? (y/n)"
        read -r continue_response
        
        if [[ ! "$continue_response" =~ ^[Yy]$ ]]; then
            echo "Deployment cancelled"
            exit 0
        fi
    fi
fi

echo ""
echo -e "${BLUE}Current branch:${NC} $(git branch --show-current)"
echo ""

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}⚠${NC}  You are not on the 'main' branch"
    echo "   The GitHub Actions workflow triggers on pushes to 'main'"
    echo ""
    echo "Would you like to:"
    echo "  1) Switch to main and merge changes"
    echo "  2) Push current branch anyway"
    echo "  3) Cancel"
    echo ""
    read -r branch_choice
    
    case $branch_choice in
        1)
            echo "Switching to main..."
            git checkout main
            git pull origin main
            git merge "$CURRENT_BRANCH"
            ;;
        2)
            echo "Pushing current branch..."
            ;;
        *)
            echo "Deployment cancelled"
            exit 0
            ;;
    esac
fi

echo ""
echo -e "${BLUE}Pushing to GitHub...${NC}"
echo ""

# Push to GitHub
if git push origin "$(git branch --show-current)"; then
    echo ""
    echo -e "${GREEN}✓${NC} Code pushed successfully!"
    echo ""
    echo -e "${BLUE}GitHub Actions workflow has been triggered${NC}"
    echo ""
    echo "You can monitor the deployment at:"
    echo "https://github.com/$REPO_OWNER/$REPO_NAME/actions"
    echo ""
    echo "The deployment process includes:"
    echo "  • Running tests"
    echo "  • Building the application"
    echo "  • Deploying to Azure Web App"
    echo "  • Running database migrations"
    echo "  • Verifying deployment"
    echo ""
    echo "This typically takes 5-10 minutes."
    echo ""
    
    # Check if gh is installed for monitoring
    if command -v gh &> /dev/null; then
        echo "Would you like to watch the workflow progress? (y/n)"
        read -r watch_response
        
        if [[ "$watch_response" =~ ^[Yy]$ ]]; then
            echo ""
            echo "Opening GitHub Actions in browser..."
            gh run watch
        fi
    else
        echo "Install GitHub CLI (gh) to watch deployment progress from terminal"
        echo "  brew install gh"
    fi
    
    echo ""
    echo "After deployment completes, verify with:"
    echo -e "  ${BLUE}./scripts/verify_deployment.sh${NC}"
    
else
    echo -e "${RED}✗${NC} Failed to push to GitHub"
    exit 1
fi
