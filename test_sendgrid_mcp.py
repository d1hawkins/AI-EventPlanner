#!/usr/bin/env python3
"""
Test script for SendGrid MCP server.

This script tests the SendGrid MCP server by:
1. Starting the MCP server
2. Sending test requests to the server with different method names
3. Verifying the responses

Usage:
    python test_sendgrid_mcp.py

Environment variables:
    SENDGRID_API_KEY: SendGrid API key
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# Check if API key is set
sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')

if not sendgrid_api_key:
    print("Error: SENDGRID_API_KEY environment variable is not set.")
    sys.exit(1)

# Define MCP server path
sendgrid_server_path = os.path.join('/Users/paulhawkins/Documents/Cline/MCP', 'sendgrid-mcp', 'build', 'index.js')

# Check if MCP server file exists
if not os.path.exists(sendgrid_server_path):
    print(f"Error: SendGrid MCP server not found at {sendgrid_server_path}")
    sys.exit(1)

# Function to create a JSON-RPC request
def create_jsonrpc_request(method, params, request_id=1):
    return {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id
    }

# Function to send a request to the MCP server
def send_request_to_mcp_server(request):
    print(f"Sending request to MCP server: {sendgrid_server_path}")
    print(f"Request: {json.dumps(request, indent=2)}")
    
    # Set up environment variables
    env = os.environ.copy()
    env["SENDGRID_API_KEY"] = sendgrid_api_key
    
    # Start the MCP server process
    print("Starting MCP server process...")
    process = subprocess.Popen(
        ['node', sendgrid_server_path],
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

# Function to test different method names for listing tools
def test_list_tools_methods():
    print("\n=== Testing different method names for listing tools ===\n")
    
    method_names = [
        "listTools",
        "list_tools",
        "ListTools",
        "list-tools",
        "mcp.listTools",
        "mcp.list_tools",
        "mcp.ListTools",
        "mcp.list-tools",
        "tools.list",
        "tools.listAll",
        "tools.getAll",
        "tools.get",
        "get_tools",
        "getTools",
        "get-tools",
        "mcp.get_tools",
        "mcp.getTools",
        "mcp.get-tools"
    ]
    
    for method_name in method_names:
        print(f"\nTrying method name: {method_name}")
        request = create_jsonrpc_request(method_name, {})
        response = send_request_to_mcp_server(request)
        
        if response and "result" in response and "tools" in response["result"]:
            print(f"Success! Method name '{method_name}' works for listing tools.")
            tools = response["result"]["tools"]
            tool_names = [tool["name"] for tool in tools]
            print(f"Available tools: {', '.join(tool_names)}")
            return method_name
        else:
            print(f"Method name '{method_name}' failed.")
    
    print("\nAll method names failed for listing tools.")
    return None

# Function to test different method names for calling a tool
def test_call_tool_methods(list_tools_method):
    print("\n=== Testing different method names for calling a tool ===\n")
    
    # First, get the list of available tools
    if list_tools_method:
        request = create_jsonrpc_request(list_tools_method, {})
        response = send_request_to_mcp_server(request)
        
        if response and "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            tool_names = [tool["name"] for tool in tools]
            print(f"Available tools: {', '.join(tool_names)}")
        else:
            print("Failed to get list of tools.")
            tool_names = ["list_email_templates"]
    else:
        print("Using default tool name: list_email_templates")
        tool_names = ["list_email_templates"]
    
    # Use the first tool for testing
    tool_name = tool_names[0] if tool_names else "list_email_templates"
    
    method_names = [
        "callTool",
        "call_tool",
        "CallTool",
        "call-tool",
        "mcp.callTool",
        "mcp.call_tool",
        "mcp.CallTool",
        "mcp.call-tool",
        "tools.call",
        "tools.execute",
        "tools.run",
        "execute_tool",
        "executeTool",
        "execute-tool",
        "run_tool",
        "runTool",
        "run-tool",
        "mcp.execute_tool",
        "mcp.executeTool",
        "mcp.execute-tool",
        "mcp.run_tool",
        "mcp.runTool",
        "mcp.run-tool"
    ]
    
    for method_name in method_names:
        print(f"\nTrying method name: {method_name}")
        request = create_jsonrpc_request(method_name, {
            "name": tool_name,
            "arguments": {}
        })
        response = send_request_to_mcp_server(request)
        
        if response and "result" in response:
            print(f"Success! Method name '{method_name}' works for calling a tool.")
            return method_name
        else:
            print(f"Method name '{method_name}' failed.")
    
    print("\nAll method names failed for calling a tool.")
    return None

# Main function
def main():
    print("=== SendGrid MCP Server Test ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"SendGrid MCP server path: {sendgrid_server_path}")
    print(f"SendGrid API key: {sendgrid_api_key[:5]}...{sendgrid_api_key[-5:]}")
    
    # Test different method names for listing tools
    list_tools_method = test_list_tools_methods()
    
    # Test different method names for calling a tool
    call_tool_method = test_call_tool_methods(list_tools_method)
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"List tools method: {list_tools_method or 'Not found'}")
    print(f"Call tool method: {call_tool_method or 'Not found'}")
    
    if list_tools_method and call_tool_method:
        print("\nSuccess! Found working method names for the SendGrid MCP server.")
        print(f"Use '{list_tools_method}' for listing tools.")
        print(f"Use '{call_tool_method}' for calling tools.")
        return 0
    else:
        print("\nFailed to find working method names for the SendGrid MCP server.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
