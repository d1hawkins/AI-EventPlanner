"""
Test script for verifying the Event-Agent Integration feature.

This script tests the ability to attach events to agent conversations and
ensure that agents have access to event context in their responses.
"""

import os
import sys
import uuid
import json
import requests
from typing import Dict, Any, List, Optional

# Set up test environment
BASE_URL = "http://localhost:8002"
AUTH_HEADERS = {}


def login(email: str, password: str) -> Dict[str, Any]:
    """
    Log in to the SaaS application.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Authentication headers
    """
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={"username": email, "password": password}
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        sys.exit(1)
    
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


def set_tenant_context(organization_id: int) -> Dict[str, Any]:
    """
    Set the tenant context for subsequent requests.
    
    Args:
        organization_id: Organization ID
        
    Returns:
        Updated headers with tenant context
    """
    headers = AUTH_HEADERS.copy()
    headers["X-Tenant-ID"] = str(organization_id)
    return headers


def create_event(organization_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new event.
    
    Args:
        organization_id: Organization ID
        event_data: Event data
        
    Returns:
        Created event data
    """
    headers = set_tenant_context(organization_id)
    
    response = requests.post(
        f"{BASE_URL}/api/events",
        headers=headers,
        json=event_data
    )
    
    print(f"Create event status: {response.status_code}")
    
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error creating event: {response.text}")
        return {"error": response.text}


def get_events(organization_id: int) -> Dict[str, Any]:
    """
    Get events for the organization.
    
    Args:
        organization_id: Organization ID
        
    Returns:
        List of events
    """
    headers = set_tenant_context(organization_id)
    
    response = requests.get(
        f"{BASE_URL}/api/events",
        headers=headers
    )
    
    print(f"Get events status: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting events: {response.text}")
        return {"error": response.text}


def send_agent_message(
    organization_id: int,
    agent_type: str,
    message: str,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a message to an agent.
    
    Args:
        organization_id: Organization ID
        agent_type: Agent type
        message: User message
        conversation_id: Conversation ID (optional)
        
    Returns:
        Agent response
    """
    headers = set_tenant_context(organization_id)
    
    data = {
        "agent_type": agent_type,
        "message": message
    }
    
    if conversation_id:
        data["conversation_id"] = conversation_id
    
    response = requests.post(
        f"{BASE_URL}/api/agents/message",
        headers=headers,
        json=data
    )
    
    print(f"Agent response status: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error sending message: {response.text}")
        return {"error": response.text}


def attach_event_to_conversation(
    organization_id: int,
    conversation_id: str,
    event_id: int
) -> Dict[str, Any]:
    """
    Attach an event to a conversation.
    
    Args:
        organization_id: Organization ID
        conversation_id: Conversation ID
        event_id: Event ID
        
    Returns:
        Attachment result
    """
    headers = set_tenant_context(organization_id)
    
    data = {
        "conversation_id": conversation_id,
        "event_id": event_id
    }
    
    response = requests.post(
        f"{BASE_URL}/api/agents/attach-event",
        headers=headers,
        json=data
    )
    
    print(f"Attach event status: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error attaching event: {response.text}")
        return {"error": response.text}


def run_tests():
    """Run the Event-Agent Integration tests."""
    global AUTH_HEADERS
    
    print("Starting Event-Agent Integration Tests")
    print("=====================================")
    
    # Log in as admin user
    print("\nLogging in...")
    AUTH_HEADERS = login("admin@example.com", "password123")
    
    # Use organization ID 1 for testing
    organization_id = 1
    
    # Test 1: Create a test event
    print("\nTest 1: Creating a test event...")
    event_data = {
        "title": "Test Conference",
        "event_type": "conference",
        "description": "A test conference for Event-Agent Integration",
        "start_date": "2025-06-15T09:00:00",
        "end_date": "2025-06-17T17:00:00",
        "location": "Test Convention Center",
        "budget": 50000,
        "attendee_count": 200
    }
    
    event = create_event(organization_id, event_data)
    
    if "error" in event:
        print("Failed to create event. Exiting tests.")
        sys.exit(1)
    
    event_id = event["id"]
    print(f"Created event with ID: {event_id}")
    
    # Test 2: Start a conversation with the coordinator agent
    print("\nTest 2: Starting a conversation with the coordinator agent...")
    coordinator_response = send_agent_message(
        organization_id=organization_id,
        agent_type="coordinator",
        message="I need help planning my conference."
    )
    
    if "error" in coordinator_response:
        print("Failed to start conversation. Exiting tests.")
        sys.exit(1)
    
    conversation_id = coordinator_response["conversation_id"]
    print(f"Started conversation with ID: {conversation_id}")
    
    # Test 3: Attach the event to the conversation
    print("\nTest 3: Attaching the event to the conversation...")
    attach_result = attach_event_to_conversation(
        organization_id=organization_id,
        conversation_id=conversation_id,
        event_id=event_id
    )
    
    if "error" in attach_result:
        print("Failed to attach event to conversation. Exiting tests.")
        sys.exit(1)
    
    print(f"Attached event {event_id} to conversation {conversation_id}")
    
    # Test 4: Send a message that references the event to verify context
    print("\nTest 4: Sending a message that references the event...")
    context_response = send_agent_message(
        organization_id=organization_id,
        agent_type="coordinator",
        message="What is the budget for this event?",
        conversation_id=conversation_id
    )
    
    if "error" in context_response:
        print("Failed to get response with event context. Exiting tests.")
        sys.exit(1)
    
    print(f"Agent response with event context: {context_response['response']}")
    
    # Check if the response contains the budget information
    if "$50,000" in context_response["response"] or "50000" in context_response["response"] or "50,000" in context_response["response"]:
        print("SUCCESS: Agent response includes budget information from the attached event!")
    else:
        print("WARNING: Agent response does not seem to include budget information from the attached event.")
    
    print("\nTests completed!")


if __name__ == "__main__":
    run_tests()
