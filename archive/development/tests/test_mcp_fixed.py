#!/usr/bin/env python3
"""
Fixed test script for MCP servers.

This script tests the SendGrid and OpenWeather MCP servers by:
1. Starting the MCP servers
2. Sending test requests to the servers with the correct method names
3. Verifying the responses

Usage:
    python test_mcp_fixed.py

Environment variables:
    SENDGRID_API_KEY: SendGrid API key
    OPENWEATHER_API_KEY: OpenWeather API key
"""

import os
import sys
import json
import time
import subprocess
import signal
import tempfile
from datetime import datetime

# Check if API keys are set
sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
openweather_api_key = os.environ.get('OPENWEATHER_API_KEY')

if not sendgrid_api_key:
    print("Warning: SENDGRID_API_KEY environment variable is not set.")
    print("SendGrid tests will be skipped.")

if not openweather_api_key:
    print("Warning: OPENWEATHER_API_KEY environment variable is not set.")
    print("OpenWeather tests will be skipped.")

# Define MCP server paths
sendgrid_server_path = os.path.join('/Users/paulhawkins/Documents/Cline/MCP', 'sendgrid-mcp', 'build', 'index.js')
openweather_server_path = os.path.join('/Users/paulhawkins/Documents/Cline/MCP', 'openweather-mcp', 'build', 'index.js')

# Check if MCP server files exist
if not os.path.exists(sendgrid_server_path):
    print(f"Error: SendGrid MCP server not found at {sendgrid_server_path}")
    sys.exit(1)

if not os.path.exists(openweather_server_path):
    print(f"Error: OpenWeather MCP server not found at {openweather_server_path}")
    sys.exit(1)

# Function to create a JSON-RPC request
def create_jsonrpc_request(method, params, request_id=1):
    return {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id
    }

# Function to send a request to an MCP server
def send_request_to_mcp_server(server_path, request, env_vars=None):
    print(f"Sending request to MCP server: {server_path}")
    print(f"Request: {json.dumps(request, indent=2)}")
    
    # Set up environment variables
    env = os.environ.copy()
    if env_vars:
        print(f"Environment variables: {env_vars}")
        env.update(env_vars)

    # Start the MCP server process
    print("Starting MCP server process...")
    process = subprocess.Popen(
        ['node', server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )

    # Send the request
    request_data = json.dumps(request) + '\n'
    print(f"Sending request data: {request_data}")
    
    try:
        stdout, stderr = process.communicate(input=request_data, timeout=10)
        print(f"Process completed with return code: {process.returncode}")
    except subprocess.TimeoutExpired:
        process.kill()
        print("Error: MCP server process timed out")
        return None
    
    # Parse the response
    if process.returncode != 0:
        print(f"Error: MCP server process failed with code {process.returncode}")
        print(f"Stderr: {stderr}")
        print(f"Stdout: {stdout}")
        return None
    
    print(f"Raw response: {stdout}")
    
    try:
        response = json.loads(stdout.strip())
        print(f"Parsed response: {json.dumps(response, indent=2)}")
        return response
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON response")
        print(f"Response: {stdout}")
        return None

# Function to test the SendGrid MCP server
def test_sendgrid_mcp_server():
    print("\n=== Testing SendGrid MCP Server ===\n")
    
    if not sendgrid_api_key:
        print("Skipping SendGrid tests (no API key)")
        return False
    
    # Test 1: List tools
    print("Test 1: List tools")
    # Try different method names
    request = create_jsonrpc_request("listTools", {})
    response = send_request_to_mcp_server(
        sendgrid_server_path,
        request,
        {"SENDGRID_API_KEY": sendgrid_api_key}
    )
    
    if not response or "result" not in response or "tools" not in response["result"]:
        print("Failed to list tools")
        return False
    
    tools = response["result"]["tools"]
    tool_names = [tool["name"] for tool in tools]
    print(f"Available tools: {', '.join(tool_names)}")
    
    # Test 2: Create email template
    print("\nTest 2: Create email template")
    template_name = f"Test Template {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    # Try different method names
    request = create_jsonrpc_request("callTool", {
        "name": "create_email_template",
        "arguments": {
            "name": template_name,
            "subject": "Test Subject",
            "content": "<h1>Hello {{name}}!</h1><p>This is a test email.</p>"
        }
    })
    response = send_request_to_mcp_server(
        sendgrid_server_path,
        request,
        {"SENDGRID_API_KEY": sendgrid_api_key}
    )
    
    if not response or "result" not in response:
        print("Failed to create email template")
        return False
    
    print("Email template created successfully")
    
    # Test 3: List email templates
    print("\nTest 3: List email templates")
    # Try different method names
    request = create_jsonrpc_request("callTool", {
        "name": "list_email_templates",
        "arguments": {}
    })
    response = send_request_to_mcp_server(
        sendgrid_server_path,
        request,
        {"SENDGRID_API_KEY": sendgrid_api_key}
    )
    
    if not response or "result" not in response:
        print("Failed to list email templates")
        return False
    
    templates = response["result"]["content"]
    if isinstance(templates, list) and len(templates) > 0 and isinstance(templates[0], dict) and "text" in templates[0]:
        templates_data = json.loads(templates[0]["text"])
        print(f"Found {len(templates_data)} email templates")
    else:
        print("No email templates found or unexpected response format")
    
    print("\nSendGrid MCP server tests completed successfully")
    return True

# Function to test the OpenWeather MCP server
def test_openweather_mcp_server():
    print("\n=== Testing OpenWeather MCP Server ===\n")
    
    if not openweather_api_key:
        print("Skipping OpenWeather tests (no API key)")
        return False
    
    # Test 1: List tools
    print("Test 1: List tools")
    # Try different method names
    request = create_jsonrpc_request("listTools", {})
    response = send_request_to_mcp_server(
        openweather_server_path,
        request,
        {"OPENWEATHER_API_KEY": openweather_api_key}
    )
    
    if not response or "result" not in response or "tools" not in response["result"]:
        print("Failed to list tools")
        return False
    
    tools = response["result"]["tools"]
    tool_names = [tool["name"] for tool in tools]
    print(f"Available tools: {', '.join(tool_names)}")
    
    # Test 2: Get weather forecast
    print("\nTest 2: Get weather forecast")
    # Try different method names
    request = create_jsonrpc_request("callTool", {
        "name": "get_forecast",
        "arguments": {
            "city": "New York",
            "days": 1
        }
    })
    response = send_request_to_mcp_server(
        openweather_server_path,
        request,
        {"OPENWEATHER_API_KEY": openweather_api_key}
    )
    
    if not response or "result" not in response:
        print("Failed to get weather forecast")
        return False
    
    print("Weather forecast retrieved successfully")
    
    # Test 3: List resources
    print("\nTest 3: List resources")
    # Try different method names
    request = create_jsonrpc_request("listResources", {})
    response = send_request_to_mcp_server(
        openweather_server_path,
        request,
        {"OPENWEATHER_API_KEY": openweather_api_key}
    )
    
    if not response or "result" not in response or "resources" not in response["result"]:
        print("Failed to list resources")
        return False
    
    resources = response["result"]["resources"]
    resource_uris = [resource["uri"] for resource in resources]
    print(f"Available resources: {', '.join(resource_uris)}")
    
    # Test 4: Access resource
    if resource_uris:
        print("\nTest 4: Access resource")
        # Try different method names
        request = create_jsonrpc_request("readResource", {
            "uri": resource_uris[0]
        })
        response = send_request_to_mcp_server(
            openweather_server_path,
            request,
            {"OPENWEATHER_API_KEY": openweather_api_key}
        )
        
        if not response or "result" not in response:
            print("Failed to access resource")
            return False
        
        print("Resource accessed successfully")
    
    print("\nOpenWeather MCP server tests completed successfully")
    return True

# Main function
def main():
    print("=== MCP Server Tests ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"SendGrid MCP server path: {sendgrid_server_path}")
    print(f"OpenWeather MCP server path: {openweather_server_path}")
    
    # Test SendGrid MCP server
    sendgrid_success = test_sendgrid_mcp_server()
    
    # Test OpenWeather MCP server
    openweather_success = test_openweather_mcp_server()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"SendGrid MCP server: {'PASS' if sendgrid_success else 'FAIL'}")
    print(f"OpenWeather MCP server: {'PASS' if openweather_success else 'FAIL'}")
    
    # Return exit code
    if sendgrid_success and openweather_success:
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
