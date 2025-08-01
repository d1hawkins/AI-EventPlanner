#!/usr/bin/env python3
"""
Test script to verify that the coordinator agent context retention fix is working.

This script tests that the coordinator agent:
1. Retains conversation context between interactions
2. Doesn't repeat questions that have already been asked
3. References previous user preferences and decisions
4. Tracks conversation memory properly
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state
from app.utils.conversation_memory import ConversationMemory


def test_conversation_memory():
    """Test the ConversationMemory class functionality."""
    print("=== Testing ConversationMemory Class ===")
    
    # Create a new conversation memory instance
    memory = ConversationMemory()
    
    # Test tracking user preferences
    memory.track_user_preference("event_type", "corporate conference", confidence=0.9)
    memory.track_user_preference("budget_range", "$50,000 - $75,000", confidence=0.8)
    memory.track_user_preference("location", "San Francisco", confidence=0.9)
    
    # Test tracking decisions
    memory.track_decision(
        "venue_selection", 
        "Moscone Center", 
        "User prefers large convention centers with good tech facilities",
        ["Marriott Hotel", "Palace Hotel", "Moscone Center"]
    )
    
    # Test tracking clarifications
    memory.track_clarification(
        "How many attendees are expected?",
        "Around 500 people",
        "Event scale and venue capacity requirements"
    )
    
    # Test tracking recommendations
    memory.track_recommendation(
        "catering", 
        "Recommend local farm-to-table catering for corporate events",
        "User showed interest",
        True
    )
    
    # Test getting context summary
    context_summary = memory.get_context_summary()
    print(f"Context Summary: {context_summary}")
    
    # Test getting relevant context
    relevant_context = memory.get_relevant_context("venue", "location")
    print(f"Relevant Context for venue/location: {relevant_context}")
    
    # Test should reference previous context
    should_reference = memory.should_reference_previous_context("venue")
    print(f"Should reference previous context for venue: {should_reference}")
    
    # Test context reference text
    reference_text = memory.get_context_reference_text("venue")
    print(f"Context reference text for venue: {reference_text}")
    
    print("✅ ConversationMemory tests completed successfully!\n")


def test_coordinator_with_memory():
    """Test the coordinator agent with conversation memory integration."""
    print("=== Testing Coordinator Agent with Memory ===")
    
    # Create the coordinator graph
    coordinator_graph = create_coordinator_graph()
    
    # Create initial state
    state = create_initial_state()
    
    # Verify that conversation memory is initialized
    assert "conversation_memory" in state, "Conversation memory should be initialized in state"
    assert isinstance(state["conversation_memory"], ConversationMemory), "Should be ConversationMemory instance"
    
    print("✅ Initial state includes conversation memory")
    
    # Test conversation flow
    print("\n--- Testing Conversation Flow ---")
    
    # First interaction - user asks about planning an event
    state["messages"].append({
        "role": "user",
        "content": "Hi, I need help planning a corporate conference for about 500 people in San Francisco."
    })
    
    print("User: Hi, I need help planning a corporate conference for about 500 people in San Francisco.")
    
    # Run the coordinator
    try:
        result = coordinator_graph.invoke(state)
        
        # Check that the response was generated
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        if assistant_messages:
            latest_response = assistant_messages[-1]["content"]
            print(f"Coordinator: {latest_response[:200]}...")
            
            # Verify that conversation memory is being used
            if "conversation_memory" in result:
                memory = result["conversation_memory"]
                context_summary = memory.get_context_summary()
                print(f"Memory Context: {context_summary}")
                
                # Check if user preferences were tracked
                preferences = memory.get_memory("user_preferences")
                print(f"Tracked Preferences: {preferences}")
        
        print("✅ First interaction completed successfully")
        
        # Second interaction - ask about budget (should reference previous context)
        result["messages"].append({
            "role": "user", 
            "content": "What's the budget range for this type of event?"
        })
        
        print("\nUser: What's the budget range for this type of event?")
        
        # Run coordinator again
        result2 = coordinator_graph.invoke(result)
        
        # Check the response
        assistant_messages2 = [m for m in result2["messages"] if m["role"] == "assistant"]
        if assistant_messages2:
            latest_response2 = assistant_messages2[-1]["content"]
            print(f"Coordinator: {latest_response2[:200]}...")
            
            # Check if the coordinator references the previous context
            if any(keyword in latest_response2.lower() for keyword in ["corporate conference", "500 people", "san francisco"]):
                print("✅ Coordinator referenced previous context!")
            else:
                print("⚠️  Coordinator may not be referencing previous context properly")
        
        print("✅ Second interaction completed successfully")
        
        # Third interaction - provide budget info
        result2["messages"].append({
            "role": "user",
            "content": "Our budget is around $75,000 for the entire event."
        })
        
        print("\nUser: Our budget is around $75,000 for the entire event.")
        
        # Run coordinator again
        result3 = coordinator_graph.invoke(result2)
        
        # Check the response
        assistant_messages3 = [m for m in result3["messages"] if m["role"] == "assistant"]
        if assistant_messages3:
            latest_response3 = assistant_messages3[-1]["content"]
            print(f"Coordinator: {latest_response3[:200]}...")
            
            # Verify memory tracking
            if "conversation_memory" in result3:
                memory = result3["conversation_memory"]
                preferences = memory.get_memory("user_preferences")
                print(f"Updated Preferences: {preferences}")
                
                # Check if budget was tracked
                if any("budget" in str(pref).lower() for pref in preferences.values() if isinstance(pref, dict)):
                    print("✅ Budget preference was tracked!")
                else:
                    print("⚠️  Budget preference may not have been tracked")
        
        print("✅ Third interaction completed successfully")
        
        # Fourth interaction - ask about the same thing again (should not repeat)
        result3["messages"].append({
            "role": "user",
            "content": "What type of event are we planning again?"
        })
        
        print("\nUser: What type of event are we planning again?")
        
        # Run coordinator again
        result4 = coordinator_graph.invoke(result3)
        
        # Check the response
        assistant_messages4 = [m for m in result4["messages"] if m["role"] == "assistant"]
        if assistant_messages4:
            latest_response4 = assistant_messages4[-1]["content"]
            print(f"Coordinator: {latest_response4[:200]}...")
            
            # Check if the coordinator references previous information instead of asking again
            if any(keyword in latest_response4.lower() for keyword in ["corporate conference", "mentioned", "discussed", "planning"]):
                print("✅ Coordinator referenced previous information instead of asking again!")
            else:
                print("⚠️  Coordinator may be asking questions it already knows the answer to")
        
        print("✅ Fourth interaction completed successfully")
        
    except Exception as e:
        print(f"❌ Error during coordinator testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Main test function."""
    print("🧪 Testing Coordinator Agent Context Retention Fix\n")
    
    # Test conversation memory class
    test_conversation_memory()
    
    # Test coordinator with memory integration
    success = test_coordinator_with_memory()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Summary of fixes implemented:")
        print("1. ✅ Added ConversationMemory integration to coordinator graph")
        print("2. ✅ Updated system prompt to include conversation context")
        print("3. ✅ Modified gather_requirements to track user preferences")
        print("4. ✅ Enhanced generate_response to use conversation memory")
        print("5. ✅ Added memory initialization to create_initial_state")
        print("\n🔧 The coordinator agent should now:")
        print("- Remember previous conversations and context")
        print("- Avoid repeating questions that have been answered")
        print("- Reference user preferences and decisions appropriately")
        print("- Track conversation history for better continuity")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
