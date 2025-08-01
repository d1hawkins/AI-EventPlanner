#!/usr/bin/env python3
"""
Script to verify that the auth directory is properly deployed to Azure.
This script uses the Azure CLI to connect to the Azure App Service and check if the auth directory and its files exist.
"""

import subprocess
import sys
import json

# Configuration
APP_NAME = "ai-event-planner-saas-py"
RESOURCE_GROUP = "ai-event-planner-rg"

def run_command(command):
    """Run a command and return the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error message: {e.stderr}")
        sys.exit(1)

def check_azure_login():
    """Check if logged in to Azure."""
    print("Checking Azure login status...")
    try:
        run_command("az account show")
        print("Logged in to Azure.")
    except:
        print("Not logged in to Azure. Please login.")
        run_command("az login")

def check_app_exists():
    """Check if the app exists in Azure."""
    print("Checking if the app exists in Azure...")
    try:
        run_command(f"az webapp show --name {APP_NAME} --resource-group {RESOURCE_GROUP}")
        print(f"App {APP_NAME} found in resource group {RESOURCE_GROUP}.")
    except:
        print(f"Error: App {APP_NAME} not found in resource group {RESOURCE_GROUP}.")
        sys.exit(1)

def check_auth_directory():
    """Check if the auth directory exists in the deployment."""
    print("Checking if the auth directory exists...")
    command = f"az webapp ssh --resource-group {RESOURCE_GROUP} --name {APP_NAME} --command \"ls -la /home/site/wwwroot/app | grep auth\""
    output = run_command(command)
    if output:
        print("Auth directory exists in the deployment.")
        return True
    else:
        print("Error: Auth directory does not exist in the deployment.")
        return False

def check_auth_files():
    """Check if the auth files exist in the deployment."""
    print("Checking if the auth files exist...")
    command = f"az webapp ssh --resource-group {RESOURCE_GROUP} --name {APP_NAME} --command \"ls -la /home/site/wwwroot/app/auth\""
    output = run_command(command)
    print("Auth directory contents:")
    print(output)
    
    # Check for router.py
    if "router.py" in output:
        print("Auth router file exists in the deployment.")
    else:
        print("Error: Auth router file does not exist in the deployment.")
        return False
    
    # Check for dependencies.py
    if "dependencies.py" in output:
        print("Auth dependencies file exists in the deployment.")
    else:
        print("Error: Auth dependencies file does not exist in the deployment.")
        return False
    
    # Check for __init__.py
    if "__init__.py" in output:
        print("Auth __init__.py file exists in the deployment.")
    else:
        print("Error: Auth __init__.py file does not exist in the deployment.")
        return False
    
    return True

def main():
    """Main function."""
    print("Starting verification...")
    
    # Check if logged in to Azure
    check_azure_login()
    
    # Check if the app exists
    check_app_exists()
    
    # Check if the auth directory exists
    if not check_auth_directory():
        sys.exit(1)
    
    # Check if the auth files exist
    if not check_auth_files():
        sys.exit(1)
    
    print("Verification completed successfully.")
    print("The auth directory and its files are properly deployed to Azure.")

if __name__ == "__main__":
    main()
