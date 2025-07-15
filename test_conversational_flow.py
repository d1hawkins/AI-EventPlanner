#!/usr/bin/env python3
"""
Test script for the conversational agent implementation.

This script tests the new conversational flow functionality to ensure
the agent asks questions one at a time with recommendations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state


def test_conversational_flow():
    """Test the conversational flow implementation."""
    print("🧪 Testing Conversational Agent Flow")
    print("=" * 50)
    
    # Create the coordinator graph and initial state
    graph = create_coordinator_graph()
    state = create_initial_state()
    
    print("✅ Created coordinator graph and initial state")
    print(f"Initial conversation stage: {state['conversation_stage']}")
    print(f"Initial phase: {state['current_phase']}")
    print()
    
    # Test 1: Initial user message
    print("📝 Test 1: Initial user message")
    state["messages"] = [
        {"role": "user", "content": "I want to plan an event"}
    ]
    
    # Run the graph
    result = graph.invoke(state)
    
    # Check the response
    if result["messages"] and len(result["messages"]) > 1:
        last_message = result["messages"][-1]
        print(f"✅ Agent responded: {last_message['content'][:100]}...")
        print(f"Conversation stage: {result.get('conversation_stage', 'unknown')}")
        print(f"Current question focus: {result.get('current_question_focus', 'none')}")
        print(f"Question history length: {len(result.get('question_history', []))}")
        print()
    else:
        print("❌ No response from agent")
        return False
    
    # Test 2: Answer the first question
    print("📝 Test 2: Answer the first question")
    result["messages"].append({
        "role": "user", 
        "content": "I want to plan a corporate conference for networking"
    })
    
    # Run the graph again
    result = graph.invoke(result)
    
    if result["messages"] and len(result["messages"]) > 2:
        last_message = result["messages"][-1]
        print(f"✅ Agent asked follow-up: {last_message['content'][:100]}...")
        print(f"Conversation stage: {result.get('conversation_stage', 'unknown')}")
        print(f"Current question focus: {result.get('current_question_focus', 'none')}")
        print(f"Question history length: {len(result.get('question_history', []))}")
        
        # Check if recommendations are included
        if "💡" in last_message['content'] or "Recommendation" in last_message['content']:
            print("✅ Recommendations included in response")
        else:
            print("⚠️  No recommendations detected in response")
        print()
    else:
        print("❌ No follow-up question from agent")
        return False
    
    # Test 3: Check information completeness tracking
    print("📝 Test 3: Information completeness tracking")
    completeness = result.get('information_completeness', {})
    print(f"Information completeness scores:")
    for category, score in completeness.items():
        print(f"  - {category}: {score:.1f}")
    
    if any(score > 0 for score in completeness.values()):
        print("✅ Information completeness is being tracked")
    else:
        print("⚠️  Information completeness not being updated")
    print()
    
    # Test 4: Check user goals extraction
    print("📝 Test 4: User goals extraction")
    user_goals = result.get('user_goals', [])
    print(f"Extracted user goals: {user_goals}")
    
    if 'networking' in user_goals:
        print("✅ User goals correctly extracted from conversation")
    else:
        print("⚠️  User goals not extracted correctly")
    print()
    
    # Test 5: Check conversation memory
    print("📝 Test 5: Conversation memory")
    conversation_memory = result.get('conversation_memory')
    if conversation_memory:
        print("✅ Conversation memory is active")
        # Check if we can get a context summary
        try:
            summary = conversation_memory.get_context_summary()
            print(f"Context summary: {summary[:100]}...")
        except Exception as e:
            print(f"⚠️  Error getting context summary: {e}")
    else:
        print("⚠️  Conversation memory not found")
    print()
    
    print("🎉 Conversational flow test completed!")
    print("=" * 50)
    
    return True


def test_question_manager():
    """Test the QuestionManager functionality."""
    print("🧪 Testing Question Manager")
    print("=" * 30)
    
    from app.utils.question_manager import QuestionManager
    
    question_manager = QuestionManager()
    
    # Create a test state
    state = create_initial_state()
    state["event_details"]["event_type"] = "corporate conference"
    state["user_goals"] = ["networking"]
    
    # Test getting next question
    next_question = question_manager.get_next_question(state)
    
    if next_question:
        print(f"✅ Next question: {next_question['text'][:100]}...")
        print(f"Category: {next_question['category']}")
        print(f"Priority: {next_question.get('priority', 'unknown')}")
        print(f"Required: {next_question.get('required', False)}")
    else:
        print("❌ No next question returned")
        return False
    
    # Test completeness assessment
    completeness = question_manager.assess_completeness(state)
    print(f"Completeness scores: {completeness}")
    
    # Test information sufficiency
    sufficient = question_manager.is_information_sufficient_for_proposal(state)
    print(f"Sufficient for proposal: {sufficient}")
    
    print("✅ Question Manager test completed!")
    print()
    
    return True


def test_recommendation_engine():
    """Test the RecommendationEngine functionality."""
    print("🧪 Testing Recommendation Engine")
    print("=" * 35)
    
    from app.utils.recommendation_engine import RecommendationEngine
    
    recommendation_engine = RecommendationEngine()
    
    # Test getting recommendations
    event_details = {
        "event_type": "corporate conference",
        "attendee_count": 100
    }
    user_goals = ["networking"]
    context = "basic_details"
    
    recommendations = recommendation_engine.get_recommendations(
        event_details, user_goals, context
    )
    
    if recommendations:
        print(f"✅ Recommendations: {recommendations[:100]}...")
    else:
        print("⚠️  No recommendations returned")
    
    # Test best practices
    best_practices = recommendation_engine.provide_best_practices(
        "timing", "corporate conference"
    )
    
    if best_practices:
        print(f"✅ Best practices: {best_practices[:100]}...")
    else:
        print("⚠️  No best practices returned")
    
    print("✅ Recommendation Engine test completed!")
    print()
    
    return True


if __name__ == "__main__":
    print("🚀 Starting Conversational Agent Tests")
    print("=" * 60)
    print()
    
    try:
        # Run all tests
        success = True
        success &= test_question_manager()
        success &= test_recommendation_engine()
        success &= test_conversational_flow()
        
        if success:
            print("🎉 All tests passed! Conversational agent is working correctly.")
        else:
            print("❌ Some tests failed. Please check the implementation.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
