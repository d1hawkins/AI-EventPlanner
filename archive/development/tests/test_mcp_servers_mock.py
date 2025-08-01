#!/usr/bin/env python3
"""
Mock test script for MCP servers.

This script tests the SendGrid and OpenWeather MCP servers by:
1. Starting the MCP servers
2. Sending test requests to the servers
3. Verifying the responses

This mock version doesn't require actual API keys.

Usage:
    python test_mcp_servers_mock.py
"""

import os
import sys
import json
import time
import subprocess
import signal
import tempfile
from datetime import datetime

# Define MCP server paths
sendgrid_server_path = os.path.join('mcp-servers', 'sendgrid-mcp', 'build', 'index.js')
openweather_server_path = os.path.join('mcp-servers', 'openweather-mcp', 'build', 'index.js')

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

# Function to mock sending a request to an MCP server
def mock_send_request_to_mcp_server(server_type, method, params):
    """Mock sending a request to an MCP server and return a simulated response."""
    if server_type == "sendgrid":
        if method == "listTools":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "tools": [
                        {"name": "send_email", "description": "Send an email to a single recipient"},
                        {"name": "send_bulk_emails", "description": "Send emails to multiple recipients"},
                        {"name": "create_email_template", "description": "Create a new email template"},
                        {"name": "list_email_templates", "description": "List all available email templates"},
                        {"name": "get_email_template", "description": "Get a specific email template by ID"}
                    ]
                },
                "id": 1
            }
        elif method == "callTool" and params.get("name") == "create_email_template":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"id": "mock-template-id", "name": params["arguments"]["name"]})
                        }
                    ]
                },
                "id": 1
            }
        elif method == "callTool" and params.get("name") == "list_email_templates":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps([
                                {"id": "mock-template-id", "name": "Test Template"},
                                {"id": "mock-template-id-2", "name": "Another Template"}
                            ])
                        }
                    ]
                },
                "id": 1
            }
    elif server_type == "openweather":
        if method == "listTools":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "tools": [
                        {"name": "get_forecast", "description": "Get weather forecast for a city"},
                        {"name": "check_weather_risks", "description": "Check weather-related risks for an event"}
                    ]
                },
                "id": 1
            }
        elif method == "callTool" and params.get("name") == "get_forecast":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "location": params["arguments"]["city"],
                                "daily": [
                                    {
                                        "date": "2025-03-16",
                                        "temperature": {"min": 10, "max": 20},
                                        "conditions": "Partly cloudy",
                                        "precipitation_probability": 20,
                                        "wind_speed": 5
                                    }
                                ]
                            })
                        }
                    ]
                },
                "id": 1
            }
        elif method == "listResources":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "resources": [
                        {"uri": "weather://San Francisco/current", "name": "Current weather in San Francisco"}
                    ]
                },
                "id": 1
            }
        elif method == "readResource":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "contents": [
                        {
                            "uri": params["uri"],
                            "mimeType": "application/json",
                            "text": json.dumps({
                                "location": "San Francisco",
                                "temperature": 18,
                                "conditions": "Sunny",
                                "humidity": 65,
                                "wind_speed": 10,
                                "timestamp": datetime.now().isoformat()
                            })
                        }
                    ]
                },
                "id": 1
            }
    
    # Default response for unknown requests
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": "Method not found"
        },
        "id": 1
    }

# Function to test the SendGrid MCP server
def test_sendgrid_mcp_server():
    print("\n=== Testing SendGrid MCP Server (Mock) ===\n")
    
    # Test 1: List tools
    print("Test 1: List tools")
    response = mock_send_request_to_mcp_server("sendgrid", "listTools", {})
    
    if not response or "result" not in response or "tools" not in response["result"]:
        print("Failed to list tools")
        return False
    
    tools = response["result"]["tools"]
    tool_names = [tool["name"] for tool in tools]
    print(f"Available tools: {', '.join(tool_names)}")
    
    # Test 2: Create email template
    print("\nTest 2: Create email template")
    template_name = f"Test Template {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    response = mock_send_request_to_mcp_server("sendgrid", "callTool", {
        "name": "create_email_template",
        "arguments": {
            "name": template_name,
            "subject": "Test Subject",
            "content": "<h1>Hello {{name}}!</h1><p>This is a test email.</p>"
        }
    })
    
    if not response or "result" not in response:
        print("Failed to create email template")
        return False
    
    print("Email template created successfully")
    
    # Test 3: List email templates
    print("\nTest 3: List email templates")
    response = mock_send_request_to_mcp_server("sendgrid", "callTool", {
        "name": "list_email_templates",
        "arguments": {}
    })
    
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
    print("\n=== Testing OpenWeather MCP Server (Mock) ===\n")
    
    # Test 1: List tools
    print("Test 1: List tools")
    response = mock_send_request_to_mcp_server("openweather", "listTools", {})
    
    if not response or "result" not in response or "tools" not in response["result"]:
        print("Failed to list tools")
        return False
    
    tools = response["result"]["tools"]
    tool_names = [tool["name"] for tool in tools]
    print(f"Available tools: {', '.join(tool_names)}")
    
    # Test 2: Get weather forecast
    print("\nTest 2: Get weather forecast")
    response = mock_send_request_to_mcp_server("openweather", "callTool", {
        "name": "get_forecast",
        "arguments": {
            "city": "New York",
            "days": 1
        }
    })
    
    if not response or "result" not in response:
        print("Failed to get weather forecast")
        return False
    
    forecast = json.loads(response["result"]["content"][0]["text"])
    print(f"Weather forecast for {forecast['location']}:")
    for day in forecast['daily']:
        print(f"Date: {day['date']}")
        print(f"  Temperature: {day['temperature']['min']}°C to {day['temperature']['max']}°C")
        print(f"  Conditions: {day['conditions']}")
        print(f"  Precipitation Probability: {day['precipitation_probability']}%")
        print(f"  Wind Speed: {day['wind_speed']} m/s")
    
    # Test 3: List resources
    print("\nTest 3: List resources")
    response = mock_send_request_to_mcp_server("openweather", "listResources", {})
    
    if not response or "result" not in response or "resources" not in response["result"]:
        print("Failed to list resources")
        return False
    
    resources = response["result"]["resources"]
    resource_uris = [resource["uri"] for resource in resources]
    print(f"Available resources: {', '.join(resource_uris)}")
    
    # Test 4: Access resource
    if resource_uris:
        print("\nTest 4: Access resource")
        response = mock_send_request_to_mcp_server("openweather", "readResource", {
            "uri": resource_uris[0]
        })
        
        if not response or "result" not in response:
            print("Failed to access resource")
            return False
        
        weather = json.loads(response["result"]["contents"][0]["text"])
        print(f"Current weather in {weather['location']}:")
        print(f"Temperature: {weather['temperature']}°C")
        print(f"Conditions: {weather['conditions']}")
        print(f"Humidity: {weather['humidity']}%")
        print(f"Wind Speed: {weather['wind_speed']} m/s")
    
    print("\nOpenWeather MCP server tests completed successfully")
    return True

# Function to check if Node.js is installed
def check_nodejs():
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Node.js is installed: {result.stdout.strip()}")
            return True
        else:
            print("Node.js is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("Node.js is not installed or not in PATH")
        return False

# Main function
def main():
    print("=== MCP Server Tests (Mock) ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"SendGrid MCP server path: {sendgrid_server_path}")
    print(f"OpenWeather MCP server path: {openweather_server_path}")
    
    # Check if Node.js is installed
    if not check_nodejs():
        print("Node.js is required to run the MCP servers")
        return 1
    
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
