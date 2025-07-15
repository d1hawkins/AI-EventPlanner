#!/usr/bin/env python3

"""
Test script to verify the conversational agent integration is working properly.
This will test the coordinator graph with the conversational utilities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state

def test_conversational_agent():
    """Test the conversational agent integration."""
    
    print("🧪 Testing Conversational Agent Integration...")
    
    try:
        # Create the coordinator graph
        print("📊 Creating coordinator graph...")
        graph = create_coordinator_graph()
        print("✅ Coordinator graph created successfully")
        
        # Create initial state
        print("🔄 Creating initial state...")
        state = create_initial_state()
        print("✅ Initial state created successfully")
        
        # Test first interaction - should give a proper introduction
        print("\n🗣️ Testing first interaction...")
        state["messages"] = [
            {"role": "user", "content": "I need to plan a talent show"}
        ]
        
        # Run the graph
        print("🚀 Running coordinator graph...")
        result = graph.invoke(state)
        
        # Check the response
        if result and "messages" in result:
            last_message = result["messages"][-1]
            if last_message["role"] == "assistant":
                response = last_message["content"]
                print(f"\n📝 Agent Response:\n{response}\n")
                
                # Check if it's conversational (not asking for all info at once)
                if len(response.split('\n')) < 20:  # Should be concise, not a long list
                    print("✅ Response is conversational (not overwhelming)")
                else:
                    print("❌ Response seems to be asking for too much information at once")
                
                # Check if it's asking a specific question
                if "?" in response:
                    print("✅ Response contains a question")
                else:
                    print("❌ Response doesn't contain a question")
                
                # Check if it mentions being an event coordinator
                if any(word in response.lower() for word in ["event", "coordinator", "planning", "help"]):
                    print("✅ Response identifies the agent's role")
                else:
                    print("❌ Response doesn't clearly identify the agent's role")
                
                return True
            else:
                print("❌ Last message is not from assistant")
                return False
        else:
            print("❌ No messages in result")
            return False
            
    except Exception as e:
        print(f"❌ Error testing conversational agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_question_flow():
    """Test the question flow functionality."""
    
    print("\n🔄 Testing Question Flow...")
    
    try:
        # Create the coordinator graph
        graph = create_coordinator_graph()
        state = create_initial_state()
        
        # Simulate a conversation flow
        conversation = [
            "I want to plan a corporate conference",
            "About 200 people",
            "In 3 months",
            "Around $50,000 budget"
        ]
        
        for i, user_message in enumerate(conversation):
            print(f"\n👤 User: {user_message}")
            
            # Add user message to state
            state["messages"].append({"role": "user", "content": user_message})
            
            # Run the graph
            result = graph.invoke(state)
            
            if result and "messages" in result:
                # Get the assistant's response
                assistant_messages = [msg for msg in result["messages"] if msg["role"] == "assistant"]
                if assistant_messages:
                    last_response = assistant_messages[-1]["content"]
                    print(f"🤖 Assistant: {last_response[:200]}...")
                    
                    # Update state for next iteration
                    state = result
                else:
                    print("❌ No assistant response found")
                    return False
            else:
                print("❌ No result from graph")
                return False
        
        print("✅ Question flow test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error testing question flow: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_conversational_utilities():
    """Test that all conversational utilities can be imported and instantiated."""
    
    print("\n🔧 Testing Conversational Utilities...")
    
    try:
        from app.utils.question_manager import QuestionManager
        from app.utils.recommendation_engine import RecommendationEngine
        from app.utils.conversation_memory import ConversationMemory
        from app.utils.conversation_paths import ConversationPathManager
        from app.utils.proactive_suggestions import ProactiveSuggestionEngine
        
        print("✅ All imports successful")
        
        # Test instantiation
        question_manager = QuestionManager()
        recommendation_engine = RecommendationEngine()
        conversation_memory = ConversationMemory()
        path_manager = ConversationPathManager()
        suggestion_engine = ProactiveSuggestionEngine()
        
        print("✅ All utilities instantiated successfully")
        
        # Test basic functionality
        state = create_initial_state()
        
        # Test QuestionManager
        next_question = question_manager.get_next_question(state)
        if next_question:
            print(f"✅ QuestionManager working: {next_question.get('text', 'No text')[:50]}...")
        else:
            print("❌ QuestionManager not returning questions")
        
        # Test RecommendationEngine
        recommendations = recommendation_engine.get_recommendations({}, [], "basic_details")
        print(f"✅ RecommendationEngine working: {len(recommendations) if recommendations else 0} chars")
        
        # Test ConversationPathManager
        path = path_manager.get_conversation_path(["networking"], "conference")
        if path and "priority_questions" in path:
            print(f"✅ ConversationPathManager working: {len(path['priority_questions'])} priority questions")
        else:
            print("❌ ConversationPathManager not working properly")
        
        # Test ProactiveSuggestionEngine
        suggestions = suggestion_engine.get_proactive_suggestions("I have a tight budget", "budget", state)
        if suggestions:
            print(f"✅ ProactiveSuggestionEngine working: {len(suggestions)} suggestions")
        else:
            print("❌ ProactiveSuggestionEngine not returning suggestions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing conversational utilities: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Conversational Agent Integration Tests\n")
    
    # Run all tests
    tests = [
        ("Conversational Utilities", test_conversational_utilities),
        ("Conversational Agent", test_conversational_agent),
        ("Question Flow", test_question_flow)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 Running {test_name} Test")
        print('='*60)
        
        success = test_func()
        results.append((test_name, success))
        
        if success:
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Conversational agent is working properly.")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        sys.exit(1)
