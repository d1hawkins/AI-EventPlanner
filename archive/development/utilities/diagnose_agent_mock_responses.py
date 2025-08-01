#!/usr/bin/env python3
"""
Comprehensive diagnostic script to identify why agents are returning mock responses.

This script will check:
1. Environment variables and LLM configuration
2. Agent graph imports and creation
3. LLM provider connectivity
4. Database connectivity
5. State management functionality
"""

import os
import sys
import traceback
from typing import Dict, Any, Optional
import json

def check_environment_variables() -> Dict[str, Any]:
    """Check all required environment variables."""
    print("=" * 60)
    print("CHECKING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    results = {
        "status": "success",
        "issues": [],
        "details": {}
    }
    
    # Required environment variables
    required_vars = [
        "LLM_PROVIDER",
        "DATABASE_URL",
        "ENVIRONMENT"
    ]
    
    # LLM provider specific variables
    llm_vars = {
        "openai": ["OPENAI_API_KEY"],
        "google": ["GOOGLE_API_KEY"],
        "azure_openai": ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]
    }
    
    # Check basic required variables
    for var in required_vars:
        value = os.getenv(var)
        if value:
            results["details"][var] = "SET" if var != "LLM_PROVIDER" else value
            print(f"✓ {var}: {results['details'][var]}")
        else:
            results["details"][var] = "MISSING"
            results["issues"].append(f"Missing required environment variable: {var}")
            results["status"] = "error"
            print(f"✗ {var}: MISSING")
    
    # Check LLM provider specific variables
    llm_provider = os.getenv("LLM_PROVIDER", "").lower()
    if llm_provider in llm_vars:
        print(f"\nChecking {llm_provider.upper()} specific variables:")
        for var in llm_vars[llm_provider]:
            value = os.getenv(var)
            if value:
                results["details"][var] = "SET"
                print(f"✓ {var}: SET")
            else:
                results["details"][var] = "MISSING"
                results["issues"].append(f"Missing {llm_provider} API key: {var}")
                results["status"] = "error"
                print(f"✗ {var}: MISSING")
    elif llm_provider:
        results["issues"].append(f"Unknown LLM provider: {llm_provider}")
        results["status"] = "error"
        print(f"✗ Unknown LLM provider: {llm_provider}")
    
    # Check optional but important variables
    optional_vars = [
        "APPINSIGHTS_INSTRUMENTATIONKEY",
        "APP_VERSION",
        "HOST",
        "PORT"
    ]
    
    print(f"\nOptional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            results["details"][var] = "SET" if var != "APP_VERSION" else value
            print(f"✓ {var}: {results['details'][var]}")
        else:
            results["details"][var] = "NOT SET"
            print(f"- {var}: NOT SET")
    
    return results

def check_llm_factory() -> Dict[str, Any]:
    """Check LLM factory functionality."""
    print("\n" + "=" * 60)
    print("CHECKING LLM FACTORY")
    print("=" * 60)
    
    results = {
        "status": "success",
        "issues": [],
        "details": {}
    }
    
    try:
        # Try to import LLM factory
        from app.utils.llm_factory import get_llm
        print("✓ LLM factory imported successfully")
        results["details"]["import"] = "success"
        
        # Try to create an LLM instance
        try:
            llm = get_llm()
            if llm:
                print("✓ LLM instance created successfully")
                results["details"]["llm_creation"] = "success"
                results["details"]["llm_type"] = str(type(llm))
                
                # Try a simple test call
                try:
                    # This is a very basic test - just check if the LLM can be invoked
                    test_response = llm.invoke("Hello")
                    if test_response and "mock" not in test_response.lower():
                        print("✓ LLM test call successful")
                        results["details"]["llm_test"] = "success"
                    else:
                        print("✗ LLM returned mock or empty response")
                        results["details"]["llm_test"] = "mock_response"
                        results["issues"].append("LLM is returning mock responses")
                        results["status"] = "error"
                except Exception as e:
                    print(f"✗ LLM test call failed: {str(e)}")
                    results["details"]["llm_test"] = f"error: {str(e)}"
                    results["issues"].append(f"LLM test call failed: {str(e)}")
                    results["status"] = "error"
            else:
                print("✗ LLM instance is None")
                results["details"]["llm_creation"] = "none"
                results["issues"].append("LLM factory returned None")
                results["status"] = "error"
        except Exception as e:
            print(f"✗ Failed to create LLM instance: {str(e)}")
            results["details"]["llm_creation"] = f"error: {str(e)}"
            results["issues"].append(f"Failed to create LLM instance: {str(e)}")
            results["status"] = "error"
            
    except Exception as e:
        print(f"✗ Failed to import LLM factory: {str(e)}")
        results["details"]["import"] = f"error: {str(e)}"
        results["issues"].append(f"Failed to import LLM factory: {str(e)}")
        results["status"] = "error"
    
    return results

def check_agent_graphs() -> Dict[str, Any]:
    """Check agent graph imports and creation."""
    print("\n" + "=" * 60)
    print("CHECKING AGENT GRAPHS")
    print("=" * 60)
    
    results = {
        "status": "success",
        "issues": [],
        "details": {}
    }
    
    # List of agent graphs to check
    agent_graphs = [
        ("coordinator", "app.graphs.coordinator_graph", "create_coordinator_graph"),
        ("resource_planning", "app.graphs.resource_planning_graph", "create_resource_planning_graph"),
        ("financial", "app.graphs.financial_graph", "create_financial_graph"),
        ("stakeholder_management", "app.graphs.stakeholder_management_graph", "create_stakeholder_management_graph"),
        ("marketing_communications", "app.graphs.marketing_communications_graph", "create_marketing_communications_graph"),
        ("project_management", "app.graphs.project_management_graph", "create_project_management_graph"),
        ("analytics", "app.graphs.analytics_graph", "create_analytics_graph"),
        ("compliance_security", "app.graphs.compliance_security_graph", "create_compliance_security_graph")
    ]
    
    for agent_name, module_name, function_name in agent_graphs:
        try:
            # Try to import the module
            module = __import__(module_name, fromlist=[function_name])
            print(f"✓ {agent_name}: Module imported")
            
            # Try to get the function
            create_function = getattr(module, function_name)
            print(f"✓ {agent_name}: Function found")
            
            # Try to create the graph
            graph = create_function()
            if graph:
                print(f"✓ {agent_name}: Graph created successfully")
                results["details"][agent_name] = "success"
            else:
                print(f"✗ {agent_name}: Graph creation returned None")
                results["details"][agent_name] = "none"
                results["issues"].append(f"{agent_name} graph creation returned None")
                results["status"] = "error"
                
        except Exception as e:
            print(f"✗ {agent_name}: {str(e)}")
            results["details"][agent_name] = f"error: {str(e)}"
            results["issues"].append(f"{agent_name} graph error: {str(e)}")
            results["status"] = "error"
    
    return results

def check_database_connectivity() -> Dict[str, Any]:
    """Check database connectivity."""
    print("\n" + "=" * 60)
    print("CHECKING DATABASE CONNECTIVITY")
    print("=" * 60)
    
    results = {
        "status": "success",
        "issues": [],
        "details": {}
    }
    
    try:
        from app.db.session import get_db
        from app.db.base import engine
        
        print("✓ Database modules imported")
        results["details"]["import"] = "success"
        
        # Test database connection
        try:
            with engine.connect() as connection:
                result = connection.execute("SELECT 1")
                if result:
                    print("✓ Database connection successful")
                    results["details"]["connection"] = "success"
                else:
                    print("✗ Database connection failed")
                    results["details"]["connection"] = "failed"
                    results["issues"].append("Database connection test failed")
                    results["status"] = "error"
        except Exception as e:
            print(f"✗ Database connection error: {str(e)}")
            results["details"]["connection"] = f"error: {str(e)}"
            results["issues"].append(f"Database connection error: {str(e)}")
            results["status"] = "error"
            
    except Exception as e:
        print(f"✗ Failed to import database modules: {str(e)}")
        results["details"]["import"] = f"error: {str(e)}"
        results["issues"].append(f"Failed to import database modules: {str(e)}")
        results["status"] = "error"
    
    return results

def check_agent_factory() -> Dict[str, Any]:
    """Check agent factory functionality."""
    print("\n" + "=" * 60)
    print("CHECKING AGENT FACTORY")
    print("=" * 60)
    
    results = {
        "status": "success",
        "issues": [],
        "details": {}
    }
    
    try:
        from app.agents.agent_factory import get_agent_factory
        from app.db.session import get_db
        
        print("✓ Agent factory imported")
        results["details"]["import"] = "success"
        
        # Try to create agent factory
        try:
            # Get a database session
            db = next(get_db())
            
            # Create agent factory
            agent_factory = get_agent_factory(db=db, organization_id=1)
            
            if agent_factory:
                print("✓ Agent factory created successfully")
                results["details"]["creation"] = "success"
                
                # Try to create a test agent
                try:
                    test_conversation_id = "test-diagnostic-conversation"
                    agent = agent_factory.create_agent("coordinator", test_conversation_id)
                    
                    if agent and "graph" in agent:
                        print("✓ Test agent created successfully")
                        results["details"]["agent_creation"] = "success"
                    else:
                        print("✗ Test agent creation failed")
                        results["details"]["agent_creation"] = "failed"
                        results["issues"].append("Test agent creation failed")
                        results["status"] = "error"
                        
                except Exception as e:
                    print(f"✗ Test agent creation error: {str(e)}")
                    results["details"]["agent_creation"] = f"error: {str(e)}"
                    results["issues"].append(f"Test agent creation error: {str(e)}")
                    results["status"] = "error"
            else:
                print("✗ Agent factory creation returned None")
                results["details"]["creation"] = "none"
                results["issues"].append("Agent factory creation returned None")
                results["status"] = "error"
                
        except Exception as e:
            print(f"✗ Agent factory creation error: {str(e)}")
            results["details"]["creation"] = f"error: {str(e)}"
            results["issues"].append(f"Agent factory creation error: {str(e)}")
            results["status"] = "error"
            
    except Exception as e:
        print(f"✗ Failed to import agent factory: {str(e)}")
        results["details"]["import"] = f"error: {str(e)}"
        results["issues"].append(f"Failed to import agent factory: {str(e)}")
        results["status"] = "error"
    
    return results

def main():
    """Run all diagnostic checks."""
    print("AI Event Planner Agent Mock Response Diagnostic")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print()
    
    # Run all checks
    checks = {
        "environment": check_environment_variables(),
        "llm_factory": check_llm_factory(),
        "agent_graphs": check_agent_graphs(),
        "database": check_database_connectivity(),
        "agent_factory": check_agent_factory()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    all_issues = []
    for check_name, check_result in checks.items():
        status = check_result["status"]
        issues = check_result["issues"]
        
        if status == "success":
            print(f"✓ {check_name.upper()}: PASSED")
        else:
            print(f"✗ {check_name.upper()}: FAILED")
            all_issues.extend(issues)
    
    if all_issues:
        print(f"\nISSUES FOUND ({len(all_issues)}):")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
        
        print(f"\nRECOMMENDED ACTIONS:")
        
        # Provide specific recommendations based on issues
        if any("Missing" in issue for issue in all_issues):
            print("- Set missing environment variables in Azure App Settings")
        
        if any("LLM" in issue for issue in all_issues):
            print("- Check LLM provider configuration and API keys")
            print("- Verify network connectivity to LLM provider")
        
        if any("graph" in issue.lower() for issue in all_issues):
            print("- Check agent graph imports and dependencies")
            print("- Verify LangGraph installation")
        
        if any("Database" in issue for issue in all_issues):
            print("- Check database connection string")
            print("- Verify database is accessible from Azure")
        
        print("\nFor detailed error information, check the output above.")
    else:
        print("\n🎉 ALL CHECKS PASSED!")
        print("The mock response issue may be in the specific agent logic.")
        print("Check the agent graph implementations for fallback logic.")
    
    # Save detailed results to file
    try:
        with open("diagnostic_results.json", "w") as f:
            json.dump(checks, f, indent=2)
        print(f"\nDetailed results saved to: diagnostic_results.json")
    except Exception as e:
        print(f"\nFailed to save results: {str(e)}")

if __name__ == "__main__":
    main()
