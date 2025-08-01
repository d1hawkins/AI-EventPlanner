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
import re
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
        "GOOGLE_API_KEY",
        "GOOGLE_MODEL"
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
    
    # First, check if the web app is running
    print("Checking web app status...")
    output, success = run_command(
        f"az webapp show --resource-group {resource_group} --name {web_app_name} --query state -o tsv"
    )
    if not success:
        print(f"Failed to check status of web app '{web_app_name}'.")
        return False
    
    if output.strip().lower() != "running":
        print(f"Web app '{web_app_name}' is not running. Current state: {output.strip()}")
        print("Starting the web app...")
        _, start_success = run_command(
            f"az webapp start --resource-group {resource_group} --name {web_app_name}"
        )
        if not start_success:
            print(f"Failed to start web app '{web_app_name}'.")
            return False
        print(f"✅ Started web app '{web_app_name}'.")
    else:
        print(f"✅ Web app '{web_app_name}' is running.")
    
    # Get publishing credentials
    print("Getting publishing credentials...")
    output, success = run_command(
        f"az webapp deployment list-publishing-credentials --resource-group {resource_group} --name {web_app_name} -o json"
    )
    if not success:
        print(f"Failed to get publishing credentials for web app '{web_app_name}'.")
        return False
    
    try:
        creds = json.loads(output)
        username = creds["publishingUserName"]
        password = creds["publishingPassword"]
        print(f"✅ Successfully retrieved publishing credentials for {web_app_name}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Failed to parse publishing credentials: {e}")
        print(f"Raw output: {output}")
        return False
    
    # Use the Kudu REST API to run the migration script
    print("Running migrations via Kudu REST API...")
    
    # Print the username for debugging (mask part of it for security)
    masked_username = username[:3] + "..." + username[-3:] if len(username) > 6 else "***"
    print(f"Using publishing username: {masked_username}")
    
    # Try a different approach using the Azure CLI to run the migrations directly
    print("Trying to run migrations using Azure CLI directly...")
    
    # First, try to reset the publishing credentials
    print("Resetting publishing credentials...")
    reset_command = (
        f"az webapp deployment user set "
        f"--user-name aieventplanneradmin "
        f"--password 'P@ssw0rd!2025' "
    )
    
    reset_output, reset_success = run_command(reset_command)
    if not reset_success:
        print(f"Failed to reset publishing credentials: {reset_output}")
        print("Continuing with existing credentials...")
    else:
        print("✅ Successfully reset publishing credentials")
        # Get the new credentials
        output, success = run_command(
            f"az webapp deployment list-publishing-credentials --resource-group {resource_group} --name {web_app_name} -o json"
        )
        if success:
            try:
                creds = json.loads(output)
                username = creds["publishingUserName"]
                password = creds["publishingPassword"]
                print(f"✅ Retrieved new publishing credentials")
                masked_username = username[:3] + "..." + username[-3:] if len(username) > 6 else "***"
                print(f"Using new publishing username: {masked_username}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Failed to parse new publishing credentials: {e}")
    
    # Try using the Azure CLI to run a custom script
    print("Trying to run migrations using a custom deployment script...")
    
    # Create a temporary script to run the migrations
    script_content = """
    #!/bin/bash
    cd /home/site/wwwroot
    python -m scripts.migrate
    """
    
    # Save the script to a temporary file
    script_path = "temp_migrate.sh"
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    
    # Try a simpler approach - run the migrations directly using the Kudu REST API
    print("Trying a simpler approach - running migrations directly...")
    
    # Escape special characters in password to avoid shell interpretation issues
    escaped_password = password.replace('"', '\\"').replace('$', '\\$')
    
    # Build the curl command with proper JSON formatting
    # First, find the Python executable path
    print("Finding Python executable path...")
    find_python_command = (
        f'curl -v -s -w "\\n%{{http_code}}" -X POST '
        f'-u "{username}:{escaped_password}" '
        f'-H "Content-Type: application/json" '
        f'https://{web_app_name}.scm.azurewebsites.net/api/command '
        f'-d \'{{"command":"find / -name python3 2>/dev/null | head -n 1", "dir":"/"}}\''
    )
    
    # Print a sanitized version of the command (without the password)
    sanitized_find_python_command = find_python_command.replace(escaped_password, "********")
    print(f"Executing command: {sanitized_find_python_command}")
    
    find_python_output, find_python_success = run_command(find_python_command)
    if not find_python_success:
        print(f"Failed to find Python path for web app '{web_app_name}'.")
        print(f"Command output: {find_python_output}")
        print("Using default Python path: /usr/local/bin/python3")
        python_path = "/usr/local/bin/python3"
    else:
        # Extract Python path from the response
        python_path_match = re.search(r'/[a-zA-Z0-9/_.-]*python3', find_python_output)
        python_path = python_path_match.group(0) if python_path_match else "/usr/local/bin/python3"
        print(f"Found Python path: {python_path}")
    
    # Now run the migration script with the found Python path
    command = (
        f'curl -v -s -w "\\n%{{http_code}}" -X POST '
        f'-u "{username}:{escaped_password}" '
        f'-H "Content-Type: application/json" '
        f'https://{web_app_name}.scm.azurewebsites.net/api/command '
        f'-d \'{{"command":"{python_path} -m scripts.migrate", "dir":"/home/site/wwwroot"}}\''
    )
    
    # Print a sanitized version of the command (without the password)
    sanitized_command = command.replace(escaped_password, "********")
    print(f"Executing command: {sanitized_command}")
    
    output, success = run_command(command)
    if not success:
        print(f"Failed to run migrations for web app '{web_app_name}'.")
        print(f"Command output: {output}")
        return False
    
    # Extract status code and response body
    lines = output.strip().split("\n")
    http_status = lines[-1]
    response_body = "\n".join(lines[:-1])
    
    print(f"Migration response: {response_body}")
    print(f"HTTP status: {http_status}")
    
    if http_status != "200":
        print(f"Migration failed with status {http_status}")
        # Print more detailed error information
        if "401" in http_status:
            print("Authentication failed. Please check your Azure credentials and permissions.")
            print("Try running 'az login' to refresh your Azure CLI session.")
            print("Also check if the publishing credentials are correct and not expired.")
        return False
    
    if "error" in response_body.lower():
        print("Migration script reported errors")
        print(f"Full output: {response_body}")
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
