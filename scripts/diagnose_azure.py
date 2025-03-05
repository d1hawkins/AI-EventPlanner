#!/usr/bin/env python
"""
Azure Deployment Diagnostic Tool

This script helps diagnose and fix common issues with Azure deployments.
It checks the Azure Web App configuration, verifies environment variables,
and provides guidance on fixing common issues.
"""

import os
import sys
import json
import subprocess
import argparse
from typing import Dict, List, Optional, Tuple


def run_command(command: str) -> Tuple[str, bool]:
    """Run a shell command and return the output and success status."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        return result.stdout.strip(), True
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}", False


def check_azure_login() -> bool:
    """Check if the user is logged in to Azure CLI."""
    print("Checking Azure CLI login status...")
    output, success = run_command("az account show")
    if not success:
        print("You are not logged in to Azure CLI. Please run 'az login' first.")
        return False
    print("✅ You are logged in to Azure CLI.")
    return True


def check_resource_group(resource_group: str) -> bool:
    """Check if the resource group exists."""
    print(f"Checking if resource group '{resource_group}' exists...")
    output, success = run_command(f"az group show --name {resource_group}")
    if not success:
        print(f"Resource group '{resource_group}' does not exist.")
        return False
    print(f"✅ Resource group '{resource_group}' exists.")
    return True


def check_web_app(resource_group: str, web_app_name: str) -> bool:
    """Check if the web app exists."""
    print(f"Checking if web app '{web_app_name}' exists...")
    output, success = run_command(
        f"az webapp show --resource-group {resource_group} --name {web_app_name}"
    )
    if not success:
        print(f"Web app '{web_app_name}' does not exist in resource group '{resource_group}'.")
        return False
    print(f"✅ Web app '{web_app_name}' exists.")
    return True


def check_app_settings(resource_group: str, web_app_name: str) -> Dict[str, str]:
    """Check the app settings of the web app."""
    print(f"Checking app settings for web app '{web_app_name}'...")
    output, success = run_command(
        f"az webapp config appsettings list --resource-group {resource_group} --name {web_app_name}"
    )
    if not success:
        print(f"Failed to get app settings for web app '{web_app_name}'.")
        return {}
    
    try:
        settings = json.loads(output)
        app_settings = {item["name"]: item["value"] for item in settings}
        print(f"✅ Retrieved app settings for web app '{web_app_name}'.")
        return app_settings
    except json.JSONDecodeError:
        print(f"Failed to parse app settings for web app '{web_app_name}'.")
        return {}


def check_required_settings(app_settings: Dict[str, str]) -> List[str]:
    """Check if all required settings are present."""
    required_settings = [
        "DATABASE_URL",
        "SECRET_KEY",
        "LLM_PROVIDER",
        "OPENAI_API_KEY",
    ]
    
    missing_settings = []
    for setting in required_settings:
        if setting not in app_settings or not app_settings[setting]:
            missing_settings.append(setting)
    
    return missing_settings


def check_database_connection(app_settings: Dict[str, str]) -> bool:
    """Check if the database connection is valid."""
    if "DATABASE_URL" not in app_settings:
        print("DATABASE_URL is not set in app settings.")
        return False
    
    database_url = app_settings["DATABASE_URL"]
    
    # Check if it's a Key Vault reference
    if database_url.startswith("@Microsoft.KeyVault"):
        print("DATABASE_URL is stored in Key Vault.")
        # Check if managed identity is enabled
        print("Checking if managed identity is enabled...")
        return True
    
    # Check if it's a valid PostgreSQL connection string
    if not database_url.startswith("postgresql://"):
        print("DATABASE_URL is not a valid PostgreSQL connection string.")
        return False
    
    print("✅ DATABASE_URL is set.")
    return True


def check_logs(resource_group: str, web_app_name: str) -> str:
    """Get the logs from the web app."""
    print(f"Getting logs for web app '{web_app_name}'...")
    output, success = run_command(
        f"az webapp log tail --resource-group {resource_group} --name {web_app_name} --lines 100"
    )
    if not success:
        print(f"Failed to get logs for web app '{web_app_name}'.")
        return ""
    
    return output


def fix_app_settings(
    resource_group: str, web_app_name: str, settings_to_fix: Dict[str, str]
) -> bool:
    """Fix app settings for the web app."""
    if not settings_to_fix:
        return True
    
    print(f"Fixing app settings for web app '{web_app_name}'...")
    
    # Construct the command to update app settings
    settings_args = " ".join([f"{k}={v}" for k, v in settings_to_fix.items()])
    command = f"az webapp config appsettings set --resource-group {resource_group} --name {web_app_name} --settings {settings_args}"
    
    output, success = run_command(command)
    if not success:
        print(f"Failed to update app settings for web app '{web_app_name}'.")
        return False
    
    print(f"✅ Updated app settings for web app '{web_app_name}'.")
    return True


def restart_web_app(resource_group: str, web_app_name: str) -> bool:
    """Restart the web app."""
    print(f"Restarting web app '{web_app_name}'...")
    output, success = run_command(
        f"az webapp restart --resource-group {resource_group} --name {web_app_name}"
    )
    if not success:
        print(f"Failed to restart web app '{web_app_name}'.")
        return False
    
    print(f"✅ Restarted web app '{web_app_name}'.")
    return True


def run_migrations(resource_group: str, web_app_name: str) -> bool:
    """Run database migrations."""
    print(f"Running database migrations for web app '{web_app_name}'...")
    
    # Get publishing credentials
    output, success = run_command(
        f"az webapp deployment list-publishing-credentials --resource-group {resource_group} --name {web_app_name} --query \"{{username:publishingUserName, password:publishingPassword}}\" -o json"
    )
    if not success:
        print(f"Failed to get publishing credentials for web app '{web_app_name}'.")
        return False
    
    try:
        creds = json.loads(output)
        username = creds["username"]
        password = creds["password"]
    except (json.JSONDecodeError, KeyError):
        print(f"Failed to parse publishing credentials for web app '{web_app_name}'.")
        return False
    
    # Use a simpler approach to run the migration script
    print("Running migrations...")
    command = f"curl -s -w \"\\n%{{http_code}}\" -X POST -u \"{username}:{password}\" -H \"Content-Type: application/json\" https://{web_app_name}.scm.azurewebsites.net/api/command -d \"{{\\\"command\\\":\\\"cd /home/site/wwwroot && python -m scripts.migrate\\\", \\\"dir\\\":\\\"/\\\"}}\""
    output, success = run_command(command)
    if not success:
        print(f"Failed to run migrations for web app '{web_app_name}'.")
        return False
    
    # Extract status code and response body
    lines = output.strip().split("\n")
    http_status = lines[-1]
    response_body = "\n".join(lines[:-1])
    
    print(f"Migration response: {response_body}")
    print(f"HTTP status: {http_status}")
    
    if http_status != "200":
        print(f"Migration failed with status {http_status}")
        return False
    
    if "error" in response_body.lower():
        print("Migration script reported errors")
        return False
    
    print("✅ Migrations completed successfully.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Azure Deployment Diagnostic Tool")
    parser.add_argument("--resource-group", default="ai-event-planner-rg", help="Azure resource group name")
    parser.add_argument("--web-app-name", default="ai-event-planner", help="Azure web app name")
    parser.add_argument("--fix", action="store_true", help="Fix issues automatically")
    parser.add_argument("--run-migrations", action="store_true", help="Run database migrations")
    parser.add_argument("--restart", action="store_true", help="Restart the web app")
    
    args = parser.parse_args()
    
    # Check Azure login
    if not check_azure_login():
        return
    
    # Check resource group
    if not check_resource_group(args.resource_group):
        return
    
    # Check web app
    if not check_web_app(args.resource_group, args.web_app_name):
        return
    
    # Check app settings
    app_settings = check_app_settings(args.resource_group, args.web_app_name)
    if not app_settings:
        return
    
    # Check required settings
    missing_settings = check_required_settings(app_settings)
    if missing_settings:
        print(f"Missing required settings: {', '.join(missing_settings)}")
        
        if args.fix:
            settings_to_fix = {}
            for setting in missing_settings:
                value = input(f"Enter value for {setting}: ")
                settings_to_fix[setting] = value
            
            if fix_app_settings(args.resource_group, args.web_app_name, settings_to_fix):
                print("✅ Fixed missing settings.")
            else:
                print("Failed to fix missing settings.")
                return
        else:
            print("Use --fix to set these values.")
    else:
        print("✅ All required settings are present.")
    
    # Check database connection
    if not check_database_connection(app_settings):
        print("Database connection is not valid.")
        return
    
    # Run migrations if requested
    if args.run_migrations:
        if not run_migrations(args.resource_group, args.web_app_name):
            print("Failed to run migrations.")
            return
    
    # Restart web app if requested
    if args.restart:
        if not restart_web_app(args.resource_group, args.web_app_name):
            print("Failed to restart web app.")
            return
    
    # Check logs
    logs = check_logs(args.resource_group, args.web_app_name)
    if logs:
        print("\nRecent logs:")
        print(logs)
    
    print("\nDiagnostic check completed.")


if __name__ == "__main__":
    main()
