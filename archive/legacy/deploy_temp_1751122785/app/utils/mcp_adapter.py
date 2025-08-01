"""
MCP Adapter for AI-EventPlanner

This module provides an adapter for communicating with MCP servers from Python code.
It supports both local development (using stdio) and Azure deployment (using localhost).
"""

import os
import json
import subprocess
import socket
import logging
from typing import Dict, Any, Optional, List, Union

# Set up logger
logger = logging.getLogger(__name__)

class McpConnectionError(Exception):
    """Exception raised for errors in the MCP connection."""
    pass

class McpToolError(Exception):
    """Exception raised for errors in MCP tool execution."""
    pass

class McpConnection:
    """Base class for MCP connections."""
    
    def __init__(self, server_name: str):
        """Initialize the MCP connection."""
        self.server_name = server_name
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool."""
        raise NotImplementedError("Subclasses must implement call_tool")
    
    def access_resource(self, uri: str) -> Any:
        """Access an MCP resource."""
        raise NotImplementedError("Subclasses must implement access_resource")


class McpStdioConnection(McpConnection):
    """MCP connection using stdio (for local development)."""
    
    def __init__(self, server_name: str, command: List[str]):
        """Initialize the MCP stdio connection."""
        super().__init__(server_name)
        self.command = command
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool using stdio."""
        try:
            # Create the request
            request = {
                "jsonrpc": "2.0",
                "method": "callTool",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 1
            }
            
            # Execute the MCP server process
            process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send the request
            request_json = json.dumps(request) + "\n"
            stdout, stderr = process.communicate(input=request_json)
            
            if process.returncode != 0:
                logger.error(f"MCP server process failed: {stderr}")
                raise McpConnectionError(f"MCP server process failed: {stderr}")
            
            # Parse the response
            response = json.loads(stdout.strip())
            
            if "error" in response:
                logger.error(f"MCP tool error: {response['error']}")
                raise McpToolError(f"MCP tool error: {response['error']}")
            
            return response["result"]["content"]
        
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {str(e)}")
            raise McpConnectionError(f"Error calling MCP tool {tool_name}: {str(e)}")
    
    def access_resource(self, uri: str) -> Any:
        """Access an MCP resource using stdio."""
        try:
            # Create the request
            request = {
                "jsonrpc": "2.0",
                "method": "readResource",
                "params": {
                    "uri": uri
                },
                "id": 1
            }
            
            # Execute the MCP server process
            process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send the request
            request_json = json.dumps(request) + "\n"
            stdout, stderr = process.communicate(input=request_json)
            
            if process.returncode != 0:
                logger.error(f"MCP server process failed: {stderr}")
                raise McpConnectionError(f"MCP server process failed: {stderr}")
            
            # Parse the response
            response = json.loads(stdout.strip())
            
            if "error" in response:
                logger.error(f"MCP resource error: {response['error']}")
                raise McpToolError(f"MCP resource error: {response['error']}")
            
            return response["result"]["contents"][0]["text"]
        
        except Exception as e:
            logger.error(f"Error accessing MCP resource {uri}: {str(e)}")
            raise McpConnectionError(f"Error accessing MCP resource {uri}: {str(e)}")


class McpTcpConnection(McpConnection):
    """MCP connection using TCP (for Azure deployment)."""
    
    def __init__(self, server_name: str, host: str, port: int):
        """Initialize the MCP TCP connection."""
        super().__init__(server_name)
        self.host = host
        self.port = port
    
    def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server and receive the response."""
        try:
            # Create a socket connection
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                
                # Send the request
                request_json = json.dumps(request) + "\n"
                sock.sendall(request_json.encode())
                
                # Receive the response
                response_data = b""
                while True:
                    data = sock.recv(4096)
                    if not data:
                        break
                    response_data += data
                
                # Parse the response
                response = json.loads(response_data.decode().strip())
                
                return response
        
        except Exception as e:
            logger.error(f"Error communicating with MCP server: {str(e)}")
            raise McpConnectionError(f"Error communicating with MCP server: {str(e)}")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool using TCP."""
        try:
            # Create the request
            request = {
                "jsonrpc": "2.0",
                "method": "callTool",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 1
            }
            
            # Send the request and get the response
            response = self._send_request(request)
            
            if "error" in response:
                logger.error(f"MCP tool error: {response['error']}")
                raise McpToolError(f"MCP tool error: {response['error']}")
            
            return response["result"]["content"]
        
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {str(e)}")
            raise McpConnectionError(f"Error calling MCP tool {tool_name}: {str(e)}")
    
    def access_resource(self, uri: str) -> Any:
        """Access an MCP resource using TCP."""
        try:
            # Create the request
            request = {
                "jsonrpc": "2.0",
                "method": "readResource",
                "params": {
                    "uri": uri
                },
                "id": 1
            }
            
            # Send the request and get the response
            response = self._send_request(request)
            
            if "error" in response:
                logger.error(f"MCP resource error: {response['error']}")
                raise McpToolError(f"MCP resource error: {response['error']}")
            
            return response["result"]["contents"][0]["text"]
        
        except Exception as e:
            logger.error(f"Error accessing MCP resource {uri}: {str(e)}")
            raise McpConnectionError(f"Error accessing MCP resource {uri}: {str(e)}")


# MCP server configuration
MCP_SERVER_CONFIG = {
    "sendgrid-mcp": {
        "command": ["node", "/Users/paulhawkins/Documents/Cline/MCP/sendgrid-mcp/build/index.js"],
        "port": 8001
    },
    "openweather-mcp": {
        "command": ["node", "/Users/paulhawkins/Documents/Cline/MCP/openweather-mcp/build/index.js"],
        "port": 8002
    }
}

def get_mcp_connection(server_name: str) -> McpConnection:
    """
    Get an MCP connection for the specified server.
    
    In Azure, this will use a TCP connection to localhost.
    In local development, this will use a stdio connection.
    
    Args:
        server_name: The name of the MCP server
        
    Returns:
        An MCP connection
    """
    if server_name not in MCP_SERVER_CONFIG:
        raise ValueError(f"Unknown MCP server: {server_name}")
    
    # Check if running in Azure
    running_in_azure = os.environ.get("WEBSITE_SITE_NAME") is not None
    
    if running_in_azure:
        # In Azure, use TCP connection to localhost
        return McpTcpConnection(
            server_name=server_name,
            host="localhost",
            port=MCP_SERVER_CONFIG[server_name]["port"]
        )
    else:
        # In local development, use stdio connection
        return McpStdioConnection(
            server_name=server_name,
            command=MCP_SERVER_CONFIG[server_name]["command"]
        )


# Convenience functions for calling MCP tools and accessing resources

def call_mcp_tool(server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """
    Call an MCP tool.
    
    Args:
        server_name: The name of the MCP server
        tool_name: The name of the tool to call
        arguments: The arguments to pass to the tool
        
    Returns:
        The tool result
    """
    connection = get_mcp_connection(server_name)
    return connection.call_tool(tool_name, arguments)


def access_mcp_resource(server_name: str, uri: str) -> Any:
    """
    Access an MCP resource.
    
    Args:
        server_name: The name of the MCP server
        uri: The URI of the resource to access
        
    Returns:
        The resource content
    """
    connection = get_mcp_connection(server_name)
    return connection.access_resource(uri)


# Email-specific convenience functions

def send_email(to_email: str, to_name: Optional[str], subject: str, content: str,
               from_email: Optional[str] = None, from_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Send an email using the SendGrid MCP server.
    
    Args:
        to_email: The recipient's email address
        to_name: The recipient's name (optional)
        subject: The email subject
        content: The email content (HTML supported)
        from_email: The sender's email address (optional, uses default if not provided)
        from_name: The sender's name (optional)
        
    Returns:
        The result of the send_email tool
    """
    # Prepare the arguments
    to = {"email": to_email}
    if to_name:
        to["name"] = to_name
    
    from_obj = {}
    if from_email:
        from_obj["email"] = from_email
    if from_name:
        from_obj["name"] = from_name
    
    arguments = {
        "to": to,
        "subject": subject,
        "content": content
    }
    
    if from_obj:
        arguments["from"] = from_obj
    
    # Call the send_email tool
    return call_mcp_tool("sendgrid-mcp", "send_email", arguments)


def send_bulk_emails(to_list: List[Dict[str, str]], subject: str, content: str,
                    from_email: Optional[str] = None, from_name: Optional[str] = None,
                    is_personalized: bool = False) -> Dict[str, Any]:
    """
    Send bulk emails using the SendGrid MCP server.
    
    Args:
        to_list: A list of recipient objects, each with "email" and optionally "name"
        subject: The email subject
        content: The email content (HTML supported)
        from_email: The sender's email address (optional, uses default if not provided)
        from_name: The sender's name (optional)
        is_personalized: Whether each recipient should receive a personalized email
        
    Returns:
        The result of the send_bulk_emails tool
    """
    # Prepare the arguments
    from_obj = {}
    if from_email:
        from_obj["email"] = from_email
    if from_name:
        from_obj["name"] = from_name
    
    arguments = {
        "to": to_list,
        "subject": subject,
        "content": content,
        "is_personalized": is_personalized
    }
    
    if from_obj:
        arguments["from"] = from_obj
    
    # Call the send_bulk_emails tool
    return call_mcp_tool("sendgrid-mcp", "send_bulk_emails", arguments)


# Weather-specific convenience functions

def get_weather_forecast(city: str, days: int = 3) -> Dict[str, Any]:
    """
    Get a weather forecast using the OpenWeather MCP server.
    
    Args:
        city: The city name
        days: The number of days (1-5)
        
    Returns:
        The weather forecast
    """
    # Call the get_forecast tool
    result = call_mcp_tool("openweather-mcp", "get_forecast", {
        "city": city,
        "days": days
    })
    
    # Parse the JSON result
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and "text" in result[0]:
        return json.loads(result[0]["text"])
    
    return result


def check_weather_risks(location: str, event_date: str, event_type: str,
                       attendee_count: Optional[int] = None) -> Dict[str, Any]:
    """
    Check weather-related risks for an event using the OpenWeather MCP server.
    
    Args:
        location: The event location (city name)
        event_date: The event date (YYYY-MM-DD)
        event_type: The type of event (e.g., outdoor, indoor, sports)
        attendee_count: The expected number of attendees (optional)
        
    Returns:
        The weather risk assessment
    """
    # Prepare the arguments
    arguments = {
        "location": location,
        "event_date": event_date,
        "event_type": event_type
    }
    
    if attendee_count is not None:
        arguments["attendee_count"] = attendee_count
    
    # Call the check_weather_risks tool
    result = call_mcp_tool("openweather-mcp", "check_weather_risks", arguments)
    
    # Parse the JSON result
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and "text" in result[0]:
        return json.loads(result[0]["text"])
    
    return result


def get_current_weather(city: str) -> Dict[str, Any]:
    """
    Get current weather data using the OpenWeather MCP server.
    
    Args:
        city: The city name
        
    Returns:
        The current weather data
    """
    # Access the weather resource
    uri = f"weather://{city}/current"
    result = access_mcp_resource("openweather-mcp", uri)
    
    # Parse the JSON result
    return json.loads(result)
