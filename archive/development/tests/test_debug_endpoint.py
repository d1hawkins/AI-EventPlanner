#!/usr/bin/env python3
"""
Test script to verify the debug endpoint is working.
"""

import requests
import json

def test_debug_endpoint():
    """Test the debug endpoint with a sample conversation ID."""
    
    # Test URL - adjust for Azure deployment
    base_url = "https://ai-event-planner-saas-py.azurewebsites.net"
    test_conversation_id = "test-conversation-123"
    debug_url = f"{base_url}/api/agents/debug/memory/{test_conversation_id}"
    
    print(f"Testing debug endpoint: {debug_url}")
    
    try:
        # Make request with mock auth token
        headers = {
            'Authorization': 'Bearer mock-auth-token',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(debug_url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Debug endpoint is working!")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        elif response.status_code == 404:
            print("❌ Debug endpoint not found (404)")
            print("This means the server needs to be restarted or the endpoint isn't registered")
        elif response.status_code == 401:
            print("🔒 Authentication required (401)")
            print("This is expected - the endpoint exists but requires proper auth")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running on port 8002?")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_health_endpoint():
    """Test the health endpoint to verify server is running."""
    
    base_url = "http://localhost:8002"
    health_url = f"{base_url}/health"
    
    print(f"Testing health endpoint: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=5)
        print(f"Health Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Server is running!")
            data = response.json()
            print(f"Server Status: {data.get('status')}")
            print(f"Version: {data.get('version')}")
        else:
            print(f"⚠️  Health check failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running on port 8002")
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")

if __name__ == "__main__":
    print("=== Debug Endpoint Test ===")
    test_health_endpoint()
    print()
    test_debug_endpoint()
