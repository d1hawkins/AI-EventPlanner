#!/usr/bin/env python3
"""
Script to check if the alembic package is installed in the Azure App Service.
This script uses the Azure CLI to connect to the Azure App Service and check if the alembic package is installed.
"""

import subprocess
import sys

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

def check_alembic_installation():
    """Check if the alembic package is installed in the Azure App Service."""
    print("Checking if the alembic package is installed...")
    command = f"az webapp ssh --resource-group {RESOURCE_GROUP} --name {APP_NAME} --command \"pip list | grep alembic\""
    output = run_command(command)
    if output:
        print("alembic package is installed:")
        print(output)
        return True
    else:
        print("Error: alembic package is not installed.")
        return False

def install_alembic():
    """Install the alembic package in the Azure App Service."""
    print("Installing the alembic package...")
    command = f"az webapp ssh --resource-group {RESOURCE_GROUP} --name {APP_NAME} --command \"pip install alembic\""
    output = run_command(command)
    print("Installation output:")
    print(output)
    
    # Verify installation
    if check_alembic_installation():
        print("alembic package was successfully installed.")
        return True
    else:
        print("Error: Failed to install the alembic package.")
        return False

def main():
    """Main function."""
    print("Starting alembic installation check...")
    
    # Check if logged in to Azure
    check_azure_login()
    
    # Check if the app exists
    check_app_exists()
    
    # Check if the alembic package is installed
    if not check_alembic_installation():
        # If not installed, install it
        print("alembic package is not installed. Installing...")
        if not install_alembic():
            sys.exit(1)
    
    print("alembic installation check completed successfully.")

if __name__ == "__main__":
    main()
