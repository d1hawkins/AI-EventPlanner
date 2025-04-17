#!/usr/bin/env python3
"""
Script to check if the email-validator package is installed in the Azure App Service.
This script uses the Azure CLI to connect to the Azure App Service and check if the email-validator package is installed.
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

def check_email_validator_installation():
    """Check if the email-validator package is installed in the Azure App Service."""
    print("Checking if the email-validator package is installed...")
    command = f"az webapp ssh --resource-group {RESOURCE_GROUP} --name {APP_NAME} --command \"pip list | grep email-validator\""
    output = run_command(command)
    if output:
        print("email-validator package is installed:")
        print(output)
        return True
    else:
        print("Error: email-validator package is not installed.")
        return False

def install_email_validator():
    """Install the email-validator package in the Azure App Service."""
    print("Installing the email-validator package...")
    command = f"az webapp ssh --resource-group {RESOURCE_GROUP} --name {APP_NAME} --command \"pip install email-validator\""
    output = run_command(command)
    print("Installation output:")
    print(output)
    
    # Verify installation
    if check_email_validator_installation():
        print("email-validator package was successfully installed.")
        return True
    else:
        print("Error: Failed to install the email-validator package.")
        return False

def main():
    """Main function."""
    print("Starting email-validator installation check...")
    
    # Check if logged in to Azure
    check_azure_login()
    
    # Check if the app exists
    check_app_exists()
    
    # Check if the email-validator package is installed
    if not check_email_validator_installation():
        # If not installed, install it
        print("email-validator package is not installed. Installing...")
        if not install_email_validator():
            sys.exit(1)
    
    print("email-validator installation check completed successfully.")

if __name__ == "__main__":
    main()
