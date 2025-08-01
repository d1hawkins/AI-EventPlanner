#!/usr/bin/env python3
"""
Comprehensive Azure Agent Testing Script

This script tests each agent individually to identify and fix issues causing
"mock responses" in the Azure environment.
"""

import os
import sys
import traceback
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment_variables():
    """Test that all required environment variables are present."""
    print("=" * 60)
    print("TESTING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    required_vars = [
        'GOOGLE_API_KEY',
        'TAVILY_API_KEY',
        'DATABASE_URL',
        'LLM_PROVIDER',
        'LLM_MODEL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 10}{value[-4:] if len(value) > 4 else value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ All required environment variables are set")
        return True

def test_database_connection():
    """Test database connectivity."""
    print("\n" + "=" * 60)
    print("TESTING DATABASE CONNECTION")
    print("=" * 60)
    
    try:
        from app.db.session import get_db
        from app.db.base import engine
        from sqlalchemy import text
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database connection failed - unexpected result")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_llm_factory():
    """Test LLM factory and Google AI connectivity."""
    print("\n" + "=" * 60)
    print("TESTING LLM FACTORY")
    print("=" * 60)
    
    try:
        from app.utils.llm_factory import get_llm
        
        # Test LLM creation
        llm = get_llm(temperature=0.1)
        print("✅ LLM factory created successfully")
        
        # Test LLM invocation
        test_prompt = "Hello, this is a test. Please respond with 'Test successful'."
        result = llm.invoke(test_prompt)
        
        if hasattr(result, 'content'):
            response = result.content
        else:
            response = str(result)
            
        print(f"✅ LLM response: {response[:100]}...")
        
        if "test" in response.lower():
            print("✅ LLM is responding correctly")
            return True
        else:
            print("⚠️  LLM response seems unusual")
            return False
            
    except Exception as e:
        print(f"❌ LLM factory test failed: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_agent_graph_imports():
    """Test that all agent graphs can be imported and created."""
    print("\n" + "=" * 60)
    print("TESTING AGENT GRAPH IMPORTS")
    print("=" * 60)
    
    agent_modules = [
        ('Resource Planning', 'app.graphs.resource_planning_graph', 'create_resource_planning_graph', 'create_initial_state'),
        ('Financial', 'app.graphs.financial_graph', 'create_financial_graph', 'create_initial_state'),
        ('Stakeholder Management', 'app.graphs.stakeholder_management_graph', 'create_stakeholder_management_graph', 'create_initial_state'),
        ('Marketing Communications', 'app.graphs.marketing_communications_graph', 'create_marketing_communications_graph', 'create_initial_state'),
        ('Project Management', 'app.graphs.project_management_graph', 'create_project_management_graph', 'create_initial_state'),
        ('Analytics', 'app.graphs.analytics_graph', 'create_analytics_graph', 'create_initial_state'),
        ('Compliance Security', 'app.graphs.compliance_security_graph', 'create_compliance_security_graph', 'create_initial_state'),
    ]
    
    results = {}
    
    for agent_name, module_name, graph_func, state_func in agent_modules:
        print(f"\nTesting {agent_name} Agent:")
        
        try:
            # Test module import
            module = __import__(module_name, fromlist=[graph_func, state_func])
            print(f"  ✅ Module imported: {module_name}")
            
            # Test graph function
            if hasattr(module, graph_func):
                graph_function = getattr(module, graph_func)
                print(f"  ✅ Graph function found: {graph_func}")
                
                # Test graph creation
                graph = graph_function()
                print(f"  ✅ Graph created successfully")
                
            else:
                print(f"  ❌ Graph function not found: {graph_func}")
                results[agent_name] = False
                continue
            
            # Test state function
            if hasattr(module, state_func):
                state_function = getattr(module, state_func)
                print(f"  ✅ State function found: {state_func}")
                
                # Test state creation
                state = state_function()
                print(f"  ✅ Initial state created successfully")
                
            else:
                print(f"  ❌ State function not found: {state_func}")
                results[agent_name] = False
                continue
                
            results[agent_name] = True
            print(f"  ✅ {agent_name} Agent: ALL TESTS PASSED")
            
        except Exception as e:
            print(f"  ❌ {agent_name} Agent failed: {str(e)}")
            print(f"  Traceback: {traceback.format_exc()}")
            results[agent_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("AGENT IMPORT TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for agent_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{agent_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} agents passed import tests")
    return passed == total

def test_individual_agent_invocation():
    """Test individual agent invocation with simple tasks."""
    print("\n" + "=" * 60)
    print("TESTING INDIVIDUAL AGENT INVOCATION")
    print("=" * 60)
    
    # Test Resource Planning Agent
    print("\nTesting Resource Planning Agent invocation:")
    try:
        from app.graphs.resource_planning_graph import create_resource_planning_graph, create_initial_state
        
        # Create graph and state
        graph = create_resource_planning_graph()
        state = create_initial_state()
        
        # Add test event details
        state["event_details"] = {
            "event_type": "conference",
            "title": "Test Conference",
            "attendee_count": 100,
            "location": "New York",
            "timeline_start": "2025-07-01",
            "budget": 50000
        }
        
        # Add test message
        state["messages"] = [
            {
                "role": "user",
                "content": "Please help me find a venue for a 100-person conference in New York."
            }
        ]
        
        print("  ✅ State prepared")
        
        # Invoke the graph
        result = graph.invoke(state)
        print("  ✅ Graph invocation successful")
        
        # Check for response
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        if assistant_messages:
            response = assistant_messages[-1]["content"]
            print(f"  ✅ Response received: {response[:100]}...")
            
            # Check if it's a real AI response (not a mock)
            if len(response) > 50 and not response.startswith("Mock") and not response.startswith("Error"):
                print("  ✅ Response appears to be real AI-generated content")
                return True
            else:
                print("  ⚠️  Response appears to be mock or error content")
                return False
        else:
            print("  ❌ No assistant response found")
            return False
            
    except Exception as e:
        print(f"  ❌ Resource Planning Agent invocation failed: {str(e)}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def test_agent_communication_tools():
    """Test the agent communication tools."""
    print("\n" + "=" * 60)
    print("TESTING AGENT COMMUNICATION TOOLS")
    print("=" * 60)
    
    try:
        from app.tools.agent_communication_tools import ResourcePlanningTaskTool
        
        # Create the tool
        tool = ResourcePlanningTaskTool()
        print("  ✅ ResourcePlanningTaskTool created")
        
        # Test tool invocation
        result = tool._run(
            task="Find a venue for a corporate meeting",
            event_details={
                "event_type": "corporate meeting",
                "attendee_count": 50,
                "location": "San Francisco",
                "budget": 25000
            },
            requirements={"special_requirements": ["projector", "catering"]}
        )
        
        print("  ✅ Tool invocation successful")
        
        # Check result
        if isinstance(result, dict) and "response" in result:
            response = result["response"]
            print(f"  ✅ Tool response: {response[:100]}...")
            
            # Check if it's a real response
            if "error" in result and result["error"]:
                print(f"  ⚠️  Tool returned error: {result['error']}")
                return False
            elif len(response) > 50 and not response.startswith("Mock"):
                print("  ✅ Tool response appears to be real AI-generated content")
                return True
            else:
                print("  ⚠️  Tool response appears to be mock content")
                return False
        else:
            print(f"  ❌ Unexpected tool result format: {type(result)}")
            return False
            
    except Exception as e:
        print(f"  ❌ Agent communication tools test failed: {str(e)}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def run_comprehensive_test():
    """Run all tests and provide a comprehensive report."""
    print("🚀 STARTING COMPREHENSIVE AZURE AGENT TESTING")
    print("=" * 80)
    
    test_results = {}
    
    # Run all tests
    test_results["Environment Variables"] = test_environment_variables()
    test_results["Database Connection"] = test_database_connection()
    test_results["LLM Factory"] = test_llm_factory()
    test_results["Agent Graph Imports"] = test_agent_graph_imports()
    test_results["Individual Agent Invocation"] = test_individual_agent_invocation()
    test_results["Agent Communication Tools"] = test_agent_communication_tools()
    
    # Generate final report
    print("\n" + "=" * 80)
    print("🎯 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\nOverall Score: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Agents should work correctly in Azure.")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Issues need to be fixed.")
        
        # Provide recommendations
        print("\n📋 RECOMMENDATIONS:")
        
        if not test_results["Environment Variables"]:
            print("- Fix missing environment variables in Azure App Service")
        
        if not test_results["Database Connection"]:
            print("- Fix database connectivity issues")
            print("- Check DATABASE_URL format and credentials")
        
        if not test_results["LLM Factory"]:
            print("- Fix LLM configuration issues")
            print("- Verify Google AI API key and permissions")
        
        if not test_results["Agent Graph Imports"]:
            print("- Fix missing imports in agent graphs")
            print("- Ensure all agent modules are properly structured")
        
        if not test_results["Individual Agent Invocation"]:
            print("- Fix agent graph execution issues")
            print("- Check for runtime errors in agent logic")
        
        if not test_results["Agent Communication Tools"]:
            print("- Fix agent communication tool issues")
            print("- Ensure proper error handling and response formatting")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    
    # Try to load Azure environment variables
    if os.path.exists('.env.azure'):
        load_dotenv('.env.azure')
        print("📁 Loaded .env.azure")
    elif os.path.exists('.env'):
        load_dotenv('.env')
        print("📁 Loaded .env")
    else:
        print("⚠️  No environment file found")
    
    # Run the comprehensive test
    success = run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
