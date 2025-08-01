#!/usr/bin/env python3
"""
Comprehensive fix for agent mock responses issue.

This script will:
1. Run diagnostics to identify the exact problem
2. Fix the LLM factory to handle errors gracefully
3. Update agent graphs to use fallback mechanisms
4. Create a test script to verify the fix
5. Deploy the fix to Azure
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, Optional

def run_diagnostics():
    """Run the diagnostic script to identify issues."""
    print("=" * 60)
    print("RUNNING DIAGNOSTICS")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "diagnose_agent_mock_responses.py"], 
                              capture_output=True, text=True, timeout=300)
        
        print("DIAGNOSTIC OUTPUT:")
        print(result.stdout)
        
        if result.stderr:
            print("DIAGNOSTIC ERRORS:")
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Diagnostic script timed out")
        return False
    except Exception as e:
        print(f"Error running diagnostics: {str(e)}")
        return False

def create_improved_llm_factory():
    """Create an improved LLM factory with proper error handling."""
    print("\n" + "=" * 60)
    print("CREATING IMPROVED LLM FACTORY")
    print("=" * 60)
    
    improved_factory_content = '''"""
LLM Factory module for creating LLM instances based on configuration.
Enhanced version with proper error handling and fallback mechanisms.
"""
from typing import Optional, Union
import importlib.util
import os
import logging

from langchain_core.language_models.base import BaseLanguageModel
from langchain_openai import ChatOpenAI

from app import config

# Set up logger
logger = logging.getLogger(__name__)

class MockLLM(BaseLanguageModel):
    """
    Mock LLM for fallback when real LLM providers are unavailable.
    This should only be used as a last resort.
    """
    
    def __init__(self):
        super().__init__()
        self.model_name = "mock-llm"
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """Generate a mock response."""
        from langchain_core.outputs import LLMResult, Generation
        
        # Create a helpful mock response that indicates the issue
        mock_content = """I apologize, but I'm currently operating in mock mode due to a configuration issue. 
        
This typically means:
1. The LLM provider (OpenAI/Google) API key is missing or invalid
2. There's a network connectivity issue
3. The LLM provider service is temporarily unavailable

To resolve this:
1. Check that your API keys are properly set in Azure App Settings
2. Verify network connectivity to the LLM provider
3. Check the application logs for specific error details

Please contact your system administrator to resolve this configuration issue."""
        
        generation = Generation(text=mock_content)
        return LLMResult(generations=[[generation]])
    
    def _llm_type(self) -> str:
        return "mock"
    
    def invoke(self, input, config=None, **kwargs):
        """Invoke the mock LLM."""
        from langchain_core.messages import AIMessage
        
        if isinstance(input, str):
            content = input
        elif hasattr(input, 'content'):
            content = input.content
        else:
            content = str(input)
        
        # Create a contextual mock response
        mock_response = f"""I'm currently in mock mode due to a configuration issue. 

Your message: "{content[:100]}{'...' if len(content) > 100 else ''}"

This is a mock response. To get real AI assistance, please ensure:
1. LLM provider API keys are properly configured
2. Network connectivity is available
3. The LLM service is accessible

Please contact your administrator to resolve this issue."""
        
        return AIMessage(content=mock_response)


def get_llm(temperature: float = 0.2) -> BaseLanguageModel:
    """
    Get the appropriate LLM based on configuration with proper error handling.
    
    Args:
        temperature: Temperature setting for the LLM (default: 0.2)
        
    Returns:
        Configured LLM instance or MockLLM as fallback
    """
    provider = getattr(config, 'LLM_PROVIDER', 'openai').lower()
    
    # Log the attempt
    logger.info(f"Attempting to create LLM with provider: {provider}")
    
    try:
        if provider == "openai":
            return _create_openai_llm(temperature)
        elif provider == "google":
            return _create_google_llm(temperature)
        elif provider == "azure_openai":
            return _create_azure_openai_llm(temperature)
        else:
            logger.error(f"Unsupported LLM provider: {provider}")
            return _create_fallback_llm(f"Unsupported LLM provider: {provider}")
            
    except Exception as e:
        logger.error(f"Failed to create LLM with provider {provider}: {str(e)}")
        return _create_fallback_llm(f"LLM creation failed: {str(e)}")


def _create_openai_llm(temperature: float) -> BaseLanguageModel:
    """Create OpenAI LLM with error handling."""
    api_key = getattr(config, 'OPENAI_API_KEY', '')
    model = getattr(config, 'LLM_MODEL', 'gpt-4')
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured")
    
    try:
        llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=temperature
        )
        
        # Test the LLM with a simple call
        test_response = llm.invoke("Hello")
        if test_response and hasattr(test_response, 'content'):
            logger.info("OpenAI LLM created and tested successfully")
            return llm
        else:
            raise ValueError("OpenAI LLM test call failed")
            
    except Exception as e:
        logger.error(f"OpenAI LLM creation failed: {str(e)}")
        raise


def _create_google_llm(temperature: float) -> BaseLanguageModel:
    """Create Google LLM with error handling."""
    # Check if the module is available
    if importlib.util.find_spec("langchain_google_genai") is None:
        raise ImportError(
            "langchain_google_genai is not installed. "
            "Install it with: pip install langchain-google-genai"
        )
    
    api_key = getattr(config, 'GOOGLE_API_KEY', '')
    model = getattr(config, 'GOOGLE_MODEL', 'gemini-pro')
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not configured")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        llm = ChatGoogleGenerativeAI(
            api_key=api_key,
            model=model,
            temperature=temperature
        )
        
        # Test the LLM with a simple call
        test_response = llm.invoke("Hello")
        if test_response and hasattr(test_response, 'content'):
            logger.info("Google LLM created and tested successfully")
            return llm
        else:
            raise ValueError("Google LLM test call failed")
            
    except Exception as e:
        logger.error(f"Google LLM creation failed: {str(e)}")
        raise


def _create_azure_openai_llm(temperature: float) -> BaseLanguageModel:
    """Create Azure OpenAI LLM with error handling."""
    api_key = getattr(config, 'AZURE_OPENAI_API_KEY', '')
    endpoint = getattr(config, 'AZURE_OPENAI_ENDPOINT', '')
    model = getattr(config, 'LLM_MODEL', 'gpt-4')
    
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY is not configured")
    
    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT is not configured")
    
    try:
        from langchain_openai import AzureChatOpenAI
        
        llm = AzureChatOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            model=model,
            temperature=temperature,
            api_version="2024-02-15-preview"
        )
        
        # Test the LLM with a simple call
        test_response = llm.invoke("Hello")
        if test_response and hasattr(test_response, 'content'):
            logger.info("Azure OpenAI LLM created and tested successfully")
            return llm
        else:
            raise ValueError("Azure OpenAI LLM test call failed")
            
    except Exception as e:
        logger.error(f"Azure OpenAI LLM creation failed: {str(e)}")
        raise


def _create_fallback_llm(error_message: str) -> MockLLM:
    """Create a fallback mock LLM."""
    logger.warning(f"Creating fallback MockLLM due to: {error_message}")
    return MockLLM()


def test_llm_creation() -> bool:
    """Test LLM creation and return success status."""
    try:
        llm = get_llm()
        
        # Test with a simple invocation
        response = llm.invoke("Test message")
        
        if isinstance(llm, MockLLM):
            logger.warning("LLM test completed but using MockLLM fallback")
            return False
        else:
            logger.info("LLM test completed successfully with real LLM")
            return True
            
    except Exception as e:
        logger.error(f"LLM test failed: {str(e)}")
        return False


def get_llm_status() -> Dict[str, Any]:
    """Get detailed status of LLM configuration."""
    status = {
        "provider": getattr(config, 'LLM_PROVIDER', 'not_set'),
        "api_key_configured": False,
        "llm_creation_success": False,
        "llm_type": "unknown",
        "error_message": None
    }
    
    provider = status["provider"].lower()
    
    # Check API key configuration
    if provider == "openai":
        status["api_key_configured"] = bool(getattr(config, 'OPENAI_API_KEY', ''))
    elif provider == "google":
        status["api_key_configured"] = bool(getattr(config, 'GOOGLE_API_KEY', ''))
    elif provider == "azure_openai":
        status["api_key_configured"] = bool(getattr(config, 'AZURE_OPENAI_API_KEY', '')) and bool(getattr(config, 'AZURE_OPENAI_ENDPOINT', ''))
    
    # Test LLM creation
    try:
        llm = get_llm()
        status["llm_creation_success"] = True
        status["llm_type"] = llm._llm_type() if hasattr(llm, '_llm_type') else str(type(llm))
        
        if isinstance(llm, MockLLM):
            status["llm_creation_success"] = False
            status["error_message"] = "Using MockLLM fallback"
            
    except Exception as e:
        status["error_message"] = str(e)
    
    return status
'''
    
    # Write the improved LLM factory
    with open("app/utils/llm_factory_improved.py", "w") as f:
        f.write(improved_factory_content)
    
    print("✓ Created improved LLM factory: app/utils/llm_factory_improved.py")
    return True

def backup_and_replace_llm_factory():
    """Backup the original LLM factory and replace it with the improved version."""
    print("\n" + "=" * 60)
    print("BACKING UP AND REPLACING LLM FACTORY")
    print("=" * 60)
    
    try:
        # Create backup
        if os.path.exists("app/utils/llm_factory.py"):
            backup_path = "app/utils/llm_factory.py.backup"
            with open("app/utils/llm_factory.py", "r") as original:
                with open(backup_path, "w") as backup:
                    backup.write(original.read())
            print(f"✓ Backed up original LLM factory to: {backup_path}")
        
        # Replace with improved version
        if os.path.exists("app/utils/llm_factory_improved.py"):
            with open("app/utils/llm_factory_improved.py", "r") as improved:
                with open("app/utils/llm_factory.py", "w") as original:
                    original.write(improved.read())
            print("✓ Replaced LLM factory with improved version")
            
            # Clean up temporary file
            os.remove("app/utils/llm_factory_improved.py")
            print("✓ Cleaned up temporary files")
            
            return True
        else:
            print("✗ Improved LLM factory not found")
            return False
            
    except Exception as e:
        print(f"✗ Error replacing LLM factory: {str(e)}")
        return False

def create_test_script():
    """Create a test script to verify the fix."""
    print("\n" + "=" * 60)
    print("CREATING TEST SCRIPT")
    print("=" * 60)
    
    test_script_content = '''#!/usr/bin/env python3
"""
Test script to verify that the agent mock response fix is working.
"""

import os
import sys
import json
from typing import Dict, Any

def test_llm_factory():
    """Test the LLM factory."""
    print("Testing LLM factory...")
    
    try:
        from app.utils.llm_factory import get_llm, get_llm_status
        
        # Get LLM status
        status = get_llm_status()
        print(f"LLM Status: {json.dumps(status, indent=2)}")
        
        # Test LLM creation
        llm = get_llm()
        print(f"LLM created: {type(llm)}")
        
        # Test LLM invocation
        response = llm.invoke("Hello, this is a test message.")
        print(f"LLM response: {response.content[:100]}...")
        
        # Check if it's a mock response
        if "mock mode" in response.content.lower():
            print("⚠️  LLM is using mock responses")
            return False
        else:
            print("✅ LLM is working correctly")
            return True
            
    except Exception as e:
        print(f"❌ LLM factory test failed: {str(e)}")
        return False

def test_agent_creation():
    """Test agent creation."""
    print("\\nTesting agent creation...")
    
    try:
        from app.agents.agent_factory import get_agent_factory
        from app.db.session import get_db
        
        # Get database session
        db = next(get_db())
        
        # Create agent factory
        agent_factory = get_agent_factory(db=db, organization_id=1)
        
        # Test creating a coordinator agent
        agent = agent_factory.create_agent("coordinator", "test-conversation-123")
        
        if agent and "graph" in agent:
            print("✅ Agent created successfully")
            return True
        else:
            print("❌ Agent creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Agent creation test failed: {str(e)}")
        return False

def test_agent_response():
    """Test getting a response from an agent."""
    print("\\nTesting agent response...")
    
    try:
        from app.agents.agent_factory import get_agent_factory
        from app.db.session import get_db
        
        # Get database session
        db = next(get_db())
        
        # Create agent factory
        agent_factory = get_agent_factory(db=db, organization_id=1)
        
        # Create coordinator agent
        agent = agent_factory.create_agent("coordinator", "test-conversation-456")
        
        # Add a test message
        state = agent["state"]
        state["messages"].append({
            "role": "user",
            "content": "Hello, I need help planning a corporate event."
        })
        
        # Get response from agent
        result = agent["graph"].invoke(state)
        
        # Check the response
        assistant_messages = [
            msg for msg in result.get("messages", [])
            if msg.get("role") == "assistant"
        ]
        
        if assistant_messages:
            last_response = assistant_messages[-1]["content"]
            print(f"Agent response: {last_response[:100]}...")
            
            # Check if it's a mock response
            if "mock mode" in last_response.lower():
                print("⚠️  Agent is returning mock responses")
                return False
            else:
                print("✅ Agent is working correctly")
                return True
        else:
            print("❌ No response from agent")
            return False
            
    except Exception as e:
        print(f"❌ Agent response test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("AI Event Planner Agent Fix Verification")
    print("=" * 50)
    
    tests = [
        ("LLM Factory", test_llm_factory),
        ("Agent Creation", test_agent_creation),
        ("Agent Response", test_agent_response)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\\n{test_name} Test:")
        print("-" * 30)
        results[test_name] = test_func()
    
    # Summary
    print("\\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\\n🎉 All tests passed! Agents should be working correctly.")
    else:
        print("\\n⚠️  Some tests failed. Check the configuration and logs.")
        
        # Provide troubleshooting guidance
        print("\\nTroubleshooting:")
        print("1. Check environment variables (LLM_PROVIDER, API keys)")
        print("2. Verify network connectivity to LLM provider")
        print("3. Check Azure Application Insights for detailed errors")
        print("4. Run the diagnostic script: python diagnose_agent_mock_responses.py")
    
    return all_passed

if __name__ == "__main__":
    main()
'''
    
    with open("test_agent_fix.py", "w") as f:
        f.write(test_script_content)
    
    print("✓ Created test script: test_agent_fix.py")
    return True

def create_azure_deployment_script():
    """Create a script to deploy the fix to Azure."""
    print("\n" + "=" * 60)
    print("CREATING AZURE DEPLOYMENT SCRIPT")
    print("=" * 60)
    
    deployment_script_content = '''#!/bin/bash
# Script to deploy the agent mock response fix to Azure

set -e

echo "Deploying Agent Mock Response Fix to Azure"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "app/utils/llm_factory.py" ]; then
    echo "Error: Not in the correct directory. Please run from the project root."
    exit 1
fi

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed. Please install it first."
    exit 1
fi

# Get the resource group and app name
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"

echo "Resource Group: $RESOURCE_GROUP"
echo "App Name: $APP_NAME"

# Check if the app exists
if ! az webapp show --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" &> /dev/null; then
    echo "Error: Azure Web App $APP_NAME not found in resource group $RESOURCE_GROUP"
    exit 1
fi

echo "✓ Azure Web App found"

# Deploy the updated code
echo "Deploying updated code..."
az webapp deployment source config-zip \\
    --resource-group "$RESOURCE_GROUP" \\
    --name "$APP_NAME" \\
    --src deployment.zip

if [ $? -eq 0 ]; then
    echo "✓ Code deployed successfully"
else
    echo "✗ Code deployment failed"
    exit 1
fi

# Restart the app to ensure changes take effect
echo "Restarting the application..."
az webapp restart --resource-group "$RESOURCE_GROUP" --name "$APP_NAME"

if [ $? -eq 0 ]; then
    echo "✓ Application restarted successfully"
else
    echo "✗ Application restart failed"
    exit 1
fi

# Wait a moment for the app to start
echo "Waiting for application to start..."
sleep 30

# Test the deployment
echo "Testing the deployment..."
APP_URL="https://$APP_NAME.azurewebsites.net"

# Test health endpoint
HEALTH_RESPONSE=$(curl -s "$APP_URL/health" || echo "ERROR")
if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed: $HEALTH_RESPONSE"
fi

# Test agent endpoint
echo "Testing agent endpoint..."
AGENT_RESPONSE=$(curl -s -X POST "$APP_URL/api/agents/message" \\
    -H "Content-Type: application/json" \\
    -d '{"agent_type":"coordinator","message":"Hello, test message"}' || echo "ERROR")

if [[ "$AGENT_RESPONSE" == *"mock mode"* ]]; then
    echo "⚠️  Agent is still returning mock responses"
    echo "Response: $AGENT_RESPONSE"
    echo ""
    echo "This may indicate:"
    echo "1. Environment variables are not properly set"
    echo "2. LLM provider API keys are missing or invalid"
    echo "3. Network connectivity issues"
    echo ""
    echo "Please check Azure App Settings and logs for more details."
elif [[ "$AGENT_RESPONSE" == *"ERROR"* ]]; then
    echo "✗ Agent endpoint test failed"
    echo "Response: $AGENT_RESPONSE"
else
    echo "✅ Agent endpoint is working correctly"
    echo "Response preview: ${AGENT_RESPONSE:0:100}..."
fi

echo ""
echo "Deployment completed!"
echo "Application URL: $APP_URL"
echo ""
echo "Next steps:"
echo "1. Check Azure Application Insights for any errors"
echo "2. Verify environment variables are properly set"
echo "3. Test the application thoroughly"
'''
    
    with open("deploy_agent_fix.sh", "w") as f:
        f.write(deployment_script_content)
    
    # Make the script executable
    os.chmod("deploy_agent_fix.sh", 0o755)
    
    print("✓ Created deployment script: deploy_agent_fix.sh")
    return True

def create_environment_check_script():
    """Create a script to check and set environment variables."""
    print("\n" + "=" * 60)
    print("CREATING ENVIRONMENT CHECK SCRIPT")
    print("=" * 60)
    
    env_check_content = '''#!/usr/bin/env python3
"""
Script to check and help configure environment variables for the AI Event Planner.
"""

import os
import json
from typing import Dict, Any, List

def check_environment_variables() -> Dict[str, Any]:
    """Check all required environment variables."""
    
    results = {
        "status": "success",
        "issues": [],
        "recommendations": [],
        "details": {}
    }
    
    # Required environment variables
    required_vars = {
        "LLM_PROVIDER": {
            "description": "LLM provider (openai, google, azure_openai)",
            "required": True,
            "current": os.getenv("LLM_PROVIDER", ""),
            "example": "openai"
        },
        "DATABASE_URL": {
            "description": "Database connection string",
            "required": True,
            "current": os.getenv("DATABASE_URL", ""),
            "example": "postgresql://user:pass@host:5432/dbname"
        }
    }
    
    # LLM provider specific variables
    llm_provider = os.getenv("LLM_PROVIDER", "").lower()
    
    if llm_provider == "openai":
        required_vars.update({
            "OPENAI_API_KEY": {
                "description": "OpenAI API key",
                "required": True,
                "current": os.getenv("OPENAI_API_KEY", ""),
                "example": "sk-..."
            },
            "LLM_MODEL": {
                "description": "OpenAI model name",
                "required": False,
                "current": os.getenv("LLM_MODEL", "gpt-4"),
                "example": "gpt-4"
            }
        })
    elif llm_provider == "google":
        required_vars.update({
            "GOOGLE_API_KEY": {
                "description": "Google AI API key",
                "required": True,
                "current": os.getenv("GOOGLE_API_KEY", ""),
                "example": "AI..."
            },
            "GOOGLE_MODEL": {
                "description": "Google AI model name",
                "required": False,
                "current": os.getenv("GOOGLE_MODEL", "gemini-pro"),
                "example": "gemini-pro"
            }
        })
    elif llm_provider == "azure_openai":
        required_vars.update({
            "AZURE_OPENAI_API_KEY": {
                "description": "Azure OpenAI API key",
                "required": True,
                "current": os.getenv("AZURE_OPENAI_API_KEY", ""),
                "example": "abc123..."
            },
            "AZURE_OPENAI_ENDPOINT": {
                "description": "Azure OpenAI endpoint URL",
                "required": True,
                "current": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
                "example": "https://your-resource.openai.azure.com/"
            }
        })
    
    # Optional but recommended variables
    optional_vars = {
        "SECRET_KEY": {
            "description": "JWT secret key for authentication",
            "required": False,
            "current": os.getenv("SECRET_KEY", ""),
            "example": "your-secret-key-here"
        },
        "APPINSIGHTS_INSTRUMENTATIONKEY": {
            "description": "Azure Application Insights instrumentation key",
            "required": False,
            "current": os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY", ""),
            "example": "12345678-1234-1234-1234-123456789012"
        },
        "TAVILY_API_KEY": {
            "description": "Tavily API key for web search functionality",
            "required": False,
            "current": os.getenv("TAVILY_API_KEY", ""),
            "example": "tvly-..."
        }
    }
    
    # Check required variables
    print("REQUIRED ENVIRONMENT VARIABLES:")
    print("=" * 40)
    
    for var_name, var_info in required_vars.items():
        current_value = var_info["current"]
        is_set = bool(current_value)
        
        status = "✓" if is_set else "✗"
        display_value = "SET" if is_set else "NOT SET"
        
        print(f"{status} {var_name}: {display_value}")
        print(f"   Description: {var_info['description']}")
        print(f"   Example: {var_info['example']}")
        
        results["details"][var_name] = {
            "set": is_set,
            "description": var_info["description"],
            "example": var_info["example"]
        }
        
        if var_info["required"] and not is_set:
            results["issues"].append(f"Missing required variable: {var_name}")
            results["recommendations"].append(f"Set {var_name} to {var_info['example']}")
            results["status"] = "error"
        
        print()
    
    # Check optional variables
    print("OPTIONAL ENVIRONMENT VARIABLES:")
    print("=" * 40)
    
    for var_name, var_info in optional_vars.items():
        current_value = var_info["current"]
        is_set = bool(current_value)
        
        status = "✓" if is_set else "-"
        display_value = "SET" if is_set else "NOT SET"
        
        print(f"{status} {var_name}: {display_value}")
        print(f"   Description: {var_info['description']}")
        print(f"   Example: {var_info['example']}")
        
        results["details"][var_name] = {
            "set": is_set,
            "description": var_info["description"],
            "example": var_info["example"]
        }
        
        print()
    
    return results

def generate_azure_cli_commands(results: Dict[str, Any]) -> List[str]:
    """Generate Azure CLI commands to set missing environment variables."""
    
    commands = []
    resource_group = "ai-event-planner-rg"
    app_name = "ai-event-planner-saas-py"
    
    for var_name, var_details in results["details"].items():
        if not var_details["set"]:
            example_value = var_details["example"]
            command = f'az webapp config appsettings set --resource-group "{resource_group}" --name "{app_name}" --settings {var_name}="{example_value}"'
            commands.append(command)
    
    return commands

def main():
    """Main function."""
    print("AI Event Planner Environment Variable Check")
    print("=" * 50)
    print()
    
    # Check environment variables
    results = check_environment_variables()
    
    # Summary
    print("SUMMARY:")
    print("=" * 20)
    
    if results["status"] == "success":
        print("✅ All required environment variables are set!")
    else:
        print("❌ Some required environment variables are missing.")
        print()
        print("ISSUES:")
        for issue in results["issues"]:
            print(f"  - {issue}")
        
        print()
        print("RECOMMENDATIONS:")
        for rec in results["recommendations"]:
            print(f"  - {rec}")
        
        print()
        print("AZURE CLI COMMANDS:")
        print("To set the missing variables in Azure, run these
