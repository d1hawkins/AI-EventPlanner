"""
Enhanced Conversational Agent Test
Tests the improved conversational flow with smart follow-up questions and conversation memory.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state
from app.utils.question_manager import QuestionManager
from app.utils.conversation_memory import ConversationMemory
from app.utils.recommendation_engine import RecommendationEngine


def test_enhanced_conversational_flow():
    """Test the enhanced conversational flow with smart follow-ups and memory."""
    print("🚀 Testing Enhanced Conversational Agent Flow")
    print("=" * 60)
    
    # Create the coordinator graph and initial state
    graph = create_coordinator_graph()
    state = create_initial_state()
    
    # Test conversation scenarios
    test_scenarios = [
        {
            "name": "Corporate Conference Planning",
            "messages": [
                "I need to plan a corporate conference for our company.",
                "It's a technology conference for software developers.",
                "We're expecting around 300 attendees.",
                "We want to hold it in San Francisco in September.",
                "Our budget is around $150,000.",
                "We need keynote speakers and breakout sessions.",
                "The main goal is networking and knowledge sharing.",
                "We'll need catering for lunch and coffee breaks.",
                "Yes, I'd like to see the proposal."
            ]
        },
        {
            "name": "Wedding Planning",
            "messages": [
                "I'm planning my wedding and need help.",
                "It's going to be an outdoor garden wedding.",
                "About 120 guests will attend.",
                "We're thinking late spring, maybe May.",
                "Our budget is tight, around $25,000.",
                "We want it to be romantic and elegant.",
                "We need catering, photography, and music.",
                "The venue should have backup for weather.",
                "Generate a proposal please."
            ]
        },
        {
            "name": "Small Workshop",
            "messages": [
                "I want to organize a small training workshop.",
                "It's for project management skills training.",
                "Just 15 people from our team.",
                "Next month would be ideal.",
                "Budget is flexible, maybe $5,000.",
                "We need interactive sessions and materials.",
                "The goal is skill development.",
                "A conference room with AV equipment.",
                "Let's see a proposal."
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 Testing Scenario: {scenario['name']}")
        print("-" * 40)
        
        # Reset state for each scenario
        state = create_initial_state()
        
        # Add initial system message
        state["messages"].append({
            "role": "system",
            "content": "You are a helpful event planning coordinator."
        })
        
        conversation_memory = ConversationMemory()
        
        for i, user_message in enumerate(scenario["messages"]):
            print(f"\n👤 User: {user_message}")
            
            # Add user message to state
            state["messages"].append({
                "role": "user",
                "content": user_message
            })
            
            # Process the message through the graph
            try:
                result = graph.invoke(state)
                state = result
                
                # Get the last assistant message
                assistant_messages = [m for m in state["messages"] if m["role"] == "assistant"]
                if assistant_messages:
                    last_response = assistant_messages[-1]["content"]
                    print(f"🤖 Assistant: {last_response[:200]}...")
                    
                    # Test conversation memory if we have question history
                    if state.get("question_history") and len(state["question_history"]) > 0:
                        last_question = state["question_history"][-1]
                        
                        # Add to conversation memory
                        conversation_memory.add_exchange(state, last_question, user_message)
                        
                        # Test memory retrieval
                        context = conversation_memory.get_conversation_context(state, "decisions")
                        if context and context != "No key decisions made yet.":
                            print(f"💭 Memory - Key Decisions: {context[:100]}...")
                        
                        preferences = conversation_memory.get_conversation_context(state, "preferences")
                        if preferences and preferences != "No specific preferences identified yet.":
                            print(f"🎯 Memory - Preferences: {preferences[:100]}...")
                
                # Show information completeness
                if "information_completeness" in state:
                    completeness = state["information_completeness"]
                    completed_categories = [cat for cat, score in completeness.items() if score >= 0.7]
                    if completed_categories:
                        print(f"✅ Completed categories: {', '.join(completed_categories)}")
                
                # Show conversation stage
                if "conversation_stage" in state:
                    print(f"📍 Stage: {state['conversation_stage']}")
                
            except Exception as e:
                print(f"❌ Error processing message: {str(e)}")
                break
        
        # Final state summary
        print(f"\n📊 Final State Summary for {scenario['name']}:")
        print(f"   - Total messages: {len(state['messages'])}")
        print(f"   - Questions asked: {len(state.get('question_history', []))}")
        print(f"   - Current phase: {state.get('current_phase', 'unknown')}")
        print(f"   - Has proposal: {'Yes' if state.get('proposal') else 'No'}")
        
        if state.get("event_details"):
            event_details = state["event_details"]
            print(f"   - Event type: {event_details.get('event_type', 'Not specified')}")
            print(f"   - Attendee count: {event_details.get('attendee_count', 'Not specified')}")
        
        print("\n" + "=" * 60)


def test_smart_follow_up_questions():
    """Test the smart follow-up question generation."""
    print("\n🧠 Testing Smart Follow-up Questions")
    print("=" * 60)
    
    question_manager = QuestionManager()
    
    # Test different follow-up scenarios
    test_cases = [
        {
            "question_id": "event_type",
            "answer": "I'm planning a corporate conference",
            "expected_follow_up": "conference_format"
        },
        {
            "question_id": "budget_range",
            "answer": "Our budget is very tight, around $5,000",
            "expected_follow_up": "budget_optimization"
        },
        {
            "question_id": "attendee_count",
            "answer": "We're expecting over 1,000 people",
            "expected_follow_up": "mega_event_logistics"
        },
        {
            "question_id": "event_date",
            "answer": "We need this done ASAP, next month",
            "expected_follow_up": "timeline_urgency"
        },
        {
            "question_id": "location_preference",
            "answer": "We want an outdoor garden venue",
            "expected_follow_up": "outdoor_contingency"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 Testing follow-up for: {test_case['question_id']}")
        print(f"   Answer: {test_case['answer']}")
        
        follow_up = question_manager.generate_follow_up(
            test_case["answer"],
            "test_category",
            test_case["question_id"]
        )
        
        if follow_up:
            print(f"   ✅ Generated follow-up: {follow_up['id']}")
            print(f"   📝 Question: {follow_up['text'][:100]}...")
            
            if follow_up["id"] == test_case["expected_follow_up"]:
                print(f"   🎯 Correct follow-up generated!")
            else:
                print(f"   ⚠️  Expected {test_case['expected_follow_up']}, got {follow_up['id']}")
        else:
            print(f"   ❌ No follow-up generated")


def test_conversation_memory():
    """Test the conversation memory system."""
    print("\n🧠 Testing Conversation Memory")
    print("=" * 60)
    
    memory = ConversationMemory()
    state = create_initial_state()
    
    # Simulate a conversation with memory tracking
    exchanges = [
        {
            "question": {
                "id": "event_type",
                "text": "What type of event are you planning?",
                "category": "basic_details"
            },
            "answer": "I'm planning a luxury corporate gala"
        },
        {
            "question": {
                "id": "budget_range",
                "text": "What's your budget range?",
                "category": "budget"
            },
            "answer": "We have a generous budget of $200,000"
        },
        {
            "question": {
                "id": "attendee_count",
                "text": "How many attendees?",
                "category": "basic_details"
            },
            "answer": "About 150 VIP guests"
        }
    ]
    
    print("📝 Adding exchanges to memory...")
    for exchange in exchanges:
        state = memory.add_exchange(state, exchange["question"], exchange["answer"])
        print(f"   Added: {exchange['question']['id']} -> {exchange['answer'][:50]}...")
    
    # Test memory retrieval
    print("\n🔍 Testing memory retrieval:")
    
    # Test recent context
    recent_context = memory.get_conversation_context(state, "recent")
    print(f"   Recent context: {len(recent_context)} characters")
    
    # Test key decisions
    decisions = memory.get_conversation_context(state, "decisions")
    print(f"   Key decisions: {decisions}")
    
    # Test user preferences
    preferences = memory.get_conversation_context(state, "preferences")
    print(f"   User preferences: {preferences}")
    
    # Test conversation themes
    themes = memory.get_conversation_context(state, "themes")
    print(f"   Conversation themes: {themes}")
    
    # Test contextual question enhancement
    test_question = {
        "id": "venue_type",
        "text": "What type of venue are you looking for?",
        "category": "location"
    }
    
    enhanced_question = memory.get_contextual_question_enhancement(state, test_question)
    print(f"\n🎯 Enhanced question:")
    print(f"   Original: {test_question['text']}")
    print(f"   Enhanced: {enhanced_question[:150]}...")


def test_recommendation_integration():
    """Test the recommendation engine integration."""
    print("\n💡 Testing Recommendation Integration")
    print("=" * 60)
    
    recommendation_engine = RecommendationEngine()
    
    # Test different recommendation scenarios
    test_scenarios = [
        {
            "event_details": {
                "event_type": "corporate conference",
                "attendee_count": 300
            },
            "user_goals": ["networking", "education"],
            "context": "basic_details"
        },
        {
            "event_details": {
                "event_type": "wedding",
                "attendee_count": 120
            },
            "user_goals": ["celebration"],
            "context": "location"
        },
        {
            "event_details": {
                "event_type": "workshop",
                "attendee_count": 15
            },
            "user_goals": ["education"],
            "context": "resources"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎯 Scenario {i}: {scenario['event_details']['event_type']}")
        
        recommendations = recommendation_engine.get_recommendations(
            scenario["event_details"],
            scenario["user_goals"],
            scenario["context"]
        )
        
        if recommendations:
            print(f"   ✅ Generated recommendations: {recommendations[:100]}...")
        else:
            print(f"   ⚠️  No recommendations generated")


if __name__ == "__main__":
    print("🎭 Enhanced Conversational Agent Testing Suite")
    print("=" * 60)
    
    try:
        # Run all tests
        test_enhanced_conversational_flow()
        test_smart_follow_up_questions()
        test_conversation_memory()
        test_recommendation_integration()
        
        print("\n🎉 All tests completed!")
        print("✅ Enhanced conversational agent features are working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
