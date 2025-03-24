"""
Test script for verifying the integration of AI agents with the SaaS application.

This script tests the tenant-aware agent system to ensure that:
1. Agents are properly isolated by tenant
2. Subscription-based access controls are enforced
3. Agent state is properly maintained with tenant context
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


def create_organization(name: str, slug: str, plan_id: str) -> Dict[str, Any]:
    """
    Create a new organization.
    
    Args:
        name: Organization name
        slug: Organization slug
        plan_id: Subscription plan ID
        
    Returns:
        Organization data
    """
    response = requests.post(
        f"{BASE_URL}/subscription/organizations",
        headers=AUTH_HEADERS,
        json={"name": name, "slug": slug, "plan_id": plan_id}
    )
    
    if response.status_code != 201:
        print(f"Failed to create organization: {response.text}")
        sys.exit(1)
    
    return response.json()


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


def test_agent_message(
    organization_id: int,
    agent_type: str,
    message: str,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Test sending a message to an agent.
    
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
    elif response.status_code == 403:
        print(f"Access denied: {response.json()['detail']}")
        return {"error": response.json()['detail']}
    else:
        print(f"Error: {response.text}")
        return {"error": response.text}


def test_conversation_history(organization_id: int, conversation_id: str) -> Dict[str, Any]:
    """
    Test retrieving conversation history.
    
    Args:
        organization_id: Organization ID
        conversation_id: Conversation ID
        
    Returns:
        Conversation history
    """
    headers = set_tenant_context(organization_id)
    
    response = requests.get(
        f"{BASE_URL}/api/agents/conversations/{conversation_id}",
        headers=headers
    )
    
    print(f"Conversation history status: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return {"error": response.text}


def test_list_conversations(organization_id: int) -> Dict[str, Any]:
    """
    Test listing conversations.
    
    Args:
        organization_id: Organization ID
        
    Returns:
        List of conversations
    """
    headers = set_tenant_context(organization_id)
    
    response = requests.get(
        f"{BASE_URL}/api/agents/conversations",
        headers=headers
    )
    
    print(f"List conversations status: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return {"error": response.text}


def test_delete_conversation(organization_id: int, conversation_id: str) -> Dict[str, Any]:
    """
    Test deleting a conversation.
    
    Args:
        organization_id: Organization ID
        conversation_id: Conversation ID
        
    Returns:
        Deletion result
    """
    headers = set_tenant_context(organization_id)
    
    response = requests.delete(
        f"{BASE_URL}/api/agents/conversations/{conversation_id}",
        headers=headers
    )
    
    print(f"Delete conversation status: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return {"error": response.text}


def run_tests():
    """Run the integration tests."""
    global AUTH_HEADERS
    
    print("Starting SaaS Agent Integration Tests")
    print("=====================================")
    
    # Log in as admin user
    print("\nLogging in...")
    AUTH_HEADERS = login("admin@example.com", "password123")
    
    # Create test organizations with different subscription plans
    print("\nCreating test organizations...")
    org1 = create_organization("Test Org Free", "test-org-free", "price_free")
    org2 = create_organization("Test Org Pro", "test-org-pro", "price_professional")
    org3 = create_organization("Test Org Enterprise", "test-org-enterprise", "price_enterprise")
    
    print(f"Created organizations: {org1['id']}, {org2['id']}, {org3['id']}")
    
    # Test 1: Free tier organization should only have access to coordinator and resource planning agents
    print("\nTest 1: Free tier agent access...")
    
    # Should work - coordinator agent
    coordinator_response = test_agent_message(
        organization_id=org1["id"],
        agent_type="coordinator",
        message="Hello, I need help planning an event."
    )
    
    print(f"Coordinator response: {coordinator_response.get('response', '')[:100]}...")
    conversation_id = coordinator_response.get("conversation_id")
    
    # Should work - resource planning agent
    resource_response = test_agent_message(
        organization_id=org1["id"],
        agent_type="resource_planning",
        message="I need a venue for 100 people."
    )
    
    print(f"Resource planning response: {resource_response.get('response', '')[:100]}...")
    
    # Should fail - financial agent (not available in free tier)
    financial_response = test_agent_message(
        organization_id=org1["id"],
        agent_type="financial",
        message="I need help with budgeting."
    )
    
    print(f"Financial agent access: {'Denied as expected' if 'error' in financial_response else 'Unexpectedly allowed'}")
    
    # Test 2: Professional tier organization should have access to most agents
    print("\nTest 2: Professional tier agent access...")
    
    # Should work - financial agent
    pro_financial_response = test_agent_message(
        organization_id=org2["id"],
        agent_type="financial",
        message="I need help with budgeting for a conference."
    )
    
    print(f"Pro tier financial response: {pro_financial_response.get('response', '')[:100]}...")
    pro_conversation_id = pro_financial_response.get("conversation_id")
    
    # Should fail - analytics agent (not available in professional tier)
    analytics_response = test_agent_message(
        organization_id=org2["id"],
        agent_type="analytics",
        message="I need help with event analytics."
    )
    
    print(f"Analytics agent access: {'Denied as expected' if 'error' in analytics_response else 'Unexpectedly allowed'}")
    
    # Test 3: Enterprise tier organization should have access to all agents
    print("\nTest 3: Enterprise tier agent access...")
    
    # Should work - analytics agent
    enterprise_analytics_response = test_agent_message(
        organization_id=org3["id"],
        agent_type="analytics",
        message="I need comprehensive analytics for my event."
    )
    
    print(f"Enterprise analytics response: {enterprise_analytics_response.get('response', '')[:100]}...")
    enterprise_conversation_id = enterprise_analytics_response.get("conversation_id")
    
    # Test 4: Tenant isolation - conversation history
    print("\nTest 4: Tenant isolation - conversation history...")
    
    # Get conversation history for org1
    org1_history = test_conversation_history(org1["id"], conversation_id)
    print(f"Org1 conversation count: {len(org1_history.get('messages', []))}")
    
    # Try to access org1's conversation from org2 (should fail)
    org2_accessing_org1 = test_conversation_history(org2["id"], conversation_id)
    print(f"Org2 accessing Org1 conversation: {'Denied as expected' if 'error' in org2_accessing_org1 else 'Unexpectedly allowed'}")
    
    # Test 5: Tenant isolation - list conversations
    print("\nTest 5: Tenant isolation - list conversations...")
    
    # List conversations for org1
    org1_conversations = test_list_conversations(org1["id"])
    print(f"Org1 conversation count: {org1_conversations.get('total', 0)}")
    
    # List conversations for org2
    org2_conversations = test_list_conversations(org2["id"])
    print(f"Org2 conversation count: {org2_conversations.get('total', 0)}")
    
    # Test 6: Tenant isolation - delete conversation
    print("\nTest 6: Tenant isolation - delete conversation...")
    
    # Try to delete org1's conversation from org2 (should fail)
    org2_deleting_org1 = test_delete_conversation(org2["id"], conversation_id)
    print(f"Org2 deleting Org1 conversation: {'Denied as expected' if 'error' in org2_deleting_org1 else 'Unexpectedly allowed'}")
    
    # Delete org2's own conversation (should succeed)
    org2_deleting_own = test_delete_conversation(org2["id"], pro_conversation_id)
    print(f"Org2 deleting own conversation: {'Succeeded' if 'message' in org2_deleting_own else 'Failed'}")
    
    print("\nTests completed!")


if __name__ == "__main__":
    run_tests()
