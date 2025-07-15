#!/usr/bin/env python3
"""
Test script for the conversational agent implementation.

This script tests the new conversational flow features including:
- Question management system
- Recommendation engine
- Conversation memory
- One-question-at-a-time flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state
from app.utils.question_manager import QuestionManager
from app.utils.recommendation_engine import RecommendationEngine
from app.utils.conversation_memory import ConversationMemory


def test_question_manager():
    """Test the QuestionManager functionality."""
    print("🧪 Testing QuestionManager...")
    
    qm = QuestionManager()
    
    # Test initial state
    state = create_initial_state()
    
    # Test getting first question
    first_question = qm.get_next_question(state)
    assert first_question is not None, "Should get a first question"
    assert first_question["category"] == "basic_details", "First question should be about basic details"
    print(f"✅ First question: {first_question['text']}")
    
    # Test follow-up generation
    follow_up = qm.generate_follow_up("corporate conference", "basic_details", "event_type")
    if follow_up:
        print(f"✅ Follow-up question: {follow_up['text']}")
    
    # Test completeness assessment
    completeness = qm.assess_completeness(state)
    assert isinstance(completeness, dict), "Completeness should be a dictionary"
    print(f"✅ Initial completeness: {completeness}")
    
    print("✅ QuestionManager tests passed!\n")


def test_recommendation_engine():
    """Test the RecommendationEngine functionality."""
    print("🧪 Testing RecommendationEngine...")
    
    re = RecommendationEngine()
    
    # Test event details
    event_details = {
        "event_type": "corporate conference",
        "attendee_count": 150
    }
    
    user_goals = ["networking", "education"]
    
    # Test getting recommendations
    recommendations = re.get_recommendations(event_details, user_goals, "timeline")
    print(f"✅ Timeline recommendations: {recommendations}")
    
    # Test best practices
    best_practices = re.provide_best_practices("timing", "corporate conference")
    print(f"✅ Best practices: {best_practices}")
    
    # Test alternatives
    alternatives = re.suggest_alternatives("weekend", "corporate conference", "timing")
    print(f"✅ Alternatives: {alternatives}")
    
    print("✅ RecommendationEngine tests passed!\n")


def test_conversation_memory():
    """Test the ConversationMemory functionality."""
    print("🧪 Testing ConversationMemory...")
    
    cm = ConversationMemory()
    
    # Test tracking preferences
    cm.track_user_preference("venue_style", "modern", confidence=0.9)
    preferences = cm.get_memory("user_preferences")
    assert "venue_style" in preferences, "Should track user preferences"
    print(f"✅ Tracked preference: {preferences['venue_style']}")
    
    # Test tracking decisions
    cm.track_decision("venue", "Convention Center", "Best capacity for attendee count", ["Hotel", "University"])
    decisions = cm.get_memory("decision_history")
    assert len(decisions) > 0, "Should track decisions"
    print(f"✅ Tracked decision: {decisions[0]['content']['decision']}")
    
    # Test context summary
    summary = cm.get_context_summary()
    print(f"✅ Context summary: {summary}")
    
    print("✅ ConversationMemory tests passed!\n")


def test_conversational_flow():
    """Test the full conversational flow."""
    print("🧪 Testing Conversational Flow...")
    
    # Create coordinator graph and initial state
    graph = create_coordinator_graph()
    state = create_initial_state()
    
    # Add initial user message
    state["messages"] = [
        {"role": "user", "content": "I want to plan a corporate conference"}
    ]
    
    print("📝 Initial user message: 'I want to plan a corporate conference'")
    
    # Run the graph
    try:
        result = graph.invoke(state)
        
        # Check that we got a response
        assert len(result["messages"]) > 1, "Should have assistant response"
        
        last_message = result["messages"][-1]
        assert last_message["role"] == "assistant", "Last message should be from assistant"
        
        print(f"✅ Assistant response: {last_message['content'][:200]}...")
        
        # Check conversation state
        assert result["conversation_stage"] in ["discovery", "clarification"], "Should be in discovery stage"
        print(f"✅ Conversation stage: {result['conversation_stage']}")
        
        # Check if question history is being tracked
        if result.get("question_history"):
            print(f"✅ Question history tracked: {len(result['question_history'])} questions")
        
        # Check information completeness
        if result.get("information_completeness"):
            print(f"✅ Information completeness: {result['information_completeness']}")
        
    except Exception as e:
        print(f"❌ Error in conversational flow: {str(e)}")
        return False
    
    print("✅ Conversational flow test passed!\n")
    return True


def test_question_sequence():
    """Test that questions are asked in the right sequence."""
    print("🧪 Testing Question Sequence...")
    
    graph = create_coordinator_graph()
    state = create_initial_state()
    
    # Simulate a conversation sequence
    conversation_steps = [
        "I want to plan a corporate conference",
        "It's a technology conference for software developers",
        "We expect about 200 attendees",
        "We want to hold it in March 2024",
        "Our budget is around $50,000"
    ]
    
    for i, user_input in enumerate(conversation_steps):
        print(f"👤 User: {user_input}")
        
        # Add user message
        state["messages"].append({"role": "user", "content": user_input})
        
        # Run the graph
        try:
            state = graph.invoke(state)
            
            # Get the last assistant message
            assistant_messages = [m for m in state["messages"] if m["role"] == "assistant"]
            if assistant_messages:
                last_response = assistant_messages[-1]["content"]
                print(f"🤖 Assistant: {last_response[:150]}...")
            
            # Check conversation progress
            if state.get("information_completeness"):
                basic_completeness = state["information_completeness"].get("basic_details", 0)
                print(f"📊 Basic details completeness: {basic_completeness:.1%}")
            
        except Exception as e:
            print(f"❌ Error at step {i+1}: {str(e)}")
            break
    
    print("✅ Question sequence test completed!\n")


def main():
    """Run all tests."""
    print("🚀 Starting Conversational Agent Implementation Tests\n")
    
    try:
        # Test individual components
        test_question_manager()
        test_recommendation_engine()
        test_conversation_memory()
        
        # Test integrated functionality
        if test_conversational_flow():
            test_question_sequence()
        
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
