#!/usr/bin/env python3
"""
Test script for SendGrid MCP server's send_email functionality.

This script tests the SendGrid MCP server by:
1. Starting the MCP server
2. Sending a request to send an email
3. Verifying the response

Usage:
    python test_sendgrid_send_email.py

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
        print(f"Stderr: {stderr}")
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

# Function to test sending an email
def test_send_email():
    print("\n=== Testing send_email functionality ===\n")
    
    # Try different method names for calling the send_email tool
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
    
    # Email parameters
    email_params = {
        "name": "send_email",
        "arguments": {
            "to": {
                "email": "test@example.com",
                "name": "Test Recipient"
            },
            "from": {
                "email": "noreply@example.com",
                "name": "Test Sender"
            },
            "subject": "Test Email",
            "content": "<h1>Hello!</h1><p>This is a test email.</p>"
        }
    }
    
    for method_name in method_names:
        print(f"\nTrying method name: {method_name}")
        request = create_jsonrpc_request(method_name, email_params)
        response = send_request_to_mcp_server(request)
        
        if response and "result" in response:
            print(f"Success! Method name '{method_name}' works for sending an email.")
            return method_name
        else:
            print(f"Method name '{method_name}' failed.")
    
    print("\nAll method names failed for sending an email.")
    return None

# Main function
def main():
    print("=== SendGrid MCP Server Test (Send Email) ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"SendGrid MCP server path: {sendgrid_server_path}")
    print(f"SendGrid API key: {sendgrid_api_key[:5]}...{sendgrid_api_key[-5:]}")
    
    # Test sending an email
    working_method = test_send_email()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Working method for send_email: {working_method or 'Not found'}")
    
    if working_method:
        print("\nSuccess! Found a working method name for sending emails.")
        print(f"Use '{working_method}' for calling the send_email tool.")
        return 0
    else:
        print("\nFailed to find a working method name for sending emails.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
