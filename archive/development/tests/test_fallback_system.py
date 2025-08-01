#!/usr/bin/env python3
"""
Test the fallback system functionality.
"""

import sys
sys.path.append('.')

from agent_fallback_system import AgentFallbackSystem

def test_fallback_system():
    """Test the fallback system responses"""
    
    print("=== Testing Agent Fallback System ===")
    
    # Create fallback system
    fallback = AgentFallbackSystem()
    
    # Test different agent types
    agent_types = [
        'coordinator',
        'resource_planning', 
        'financial',
        'stakeholder_management',
        'marketing_communications',
        'project_management',
        'analytics',
        'compliance_security'
    ]
    
    for agent_type in agent_types:
        print(f"\n--- Testing {agent_type} fallback ---")
        
        # Register as unavailable
        fallback.register_agent_status(agent_type, False)
        
        # Get fallback response
        response = fallback.get_fallback_response(
            agent_type=agent_type,
            message="Help me plan an event",
            conversation_id="test_123"
        )
        
        print(f"Agent: {agent_type}")
        print(f"Using Real Agent: {response['using_real_agent']}")
        print(f"Fallback Reason: {response['fallback_reason']}")
        print(f"Response Preview: {response['response'][:100]}...")
        
        # Test usage tracking
        usage_count = fallback.fallback_usage_count.get(agent_type, 0)
        print(f"Usage Count: {usage_count}")
    
    print(f"\n=== Summary ===")
    print(f"Available agents: {len(fallback.available_agents)}")
    print(f"Unavailable agents: {len(fallback.unavailable_agents)}")
    print(f"Total fallback usage: {sum(fallback.fallback_usage_count.values())}")
    
    print("\n✓ Fallback system test completed successfully!")

if __name__ == "__main__":
    test_fallback_system()
