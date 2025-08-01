#!/usr/bin/env python
"""
Fix Agent Mock Responses

This script modifies the agent factory and communication tools to ensure
real agents are used instead of mock responses.
"""

import os
import sys
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the file before modifying it."""
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        shutil.copy2(file_path, backup_path)
        print(f"Created backup: {backup_path}")
        return True
    return False

def fix_agent_factory():
    """Fix the agent factory to use real agents."""
    agent_factory_path = "app/agents/agent_factory.py"
    
    if not os.path.exists(agent_factory_path):
        print(f"Error: {agent_factory_path} not found")
        return False
    
    # Backup the file
    backup_file(agent_factory_path)
    
    with open(agent_factory_path, 'r') as f:
        content = f.read()
    
    # Check if there's a mock_response flag
    if "use_mock_response" in content or "mock_response" in content:
        # Replace any mock response flags with False
        content = re.sub(r'(use_mock_response|mock_response)\s*=\s*True', r'\1 = False', content)
        
        # Ensure the create_agent function uses real agents
        if "def create_agent" in content:
            # Find the create_agent function
            create_agent_pattern = r'def create_agent\([^)]*\):\s*[^{]*{'
            create_agent_match = re.search(create_agent_pattern, content)
            if create_agent_match:
                # Add code to ensure real agents are used
                create_agent_code = """
def create_agent(agent_type, **kwargs):
    \"\"\"Create an agent of the specified type.\"\"\"
    print(f"Creating real agent of type: {agent_type}")
    
    # Force use of real agents
    use_mock = False
    
    # Log the agent creation
    logging.info(f"Creating agent of type: {agent_type}, using real agent: {not use_mock}")
    
    if agent_type == "coordinator":
        return create_coordinator_agent(**kwargs)
    elif agent_type == "resource_planning":
        return create_resource_planning_agent(**kwargs)
    elif agent_type == "financial":
        return create_financial_agent(**kwargs)
    elif agent_type == "stakeholder":
        return create_stakeholder_agent(**kwargs)
    elif agent_type == "marketing":
        return create_marketing_agent(**kwargs)
    elif agent_type == "project_management":
        return create_project_management_agent(**kwargs)
    elif agent_type == "analytics":
        return create_analytics_agent(**kwargs)
    elif agent_type == "compliance":
        return create_compliance_agent(**kwargs)
    else:
        logging.warning(f"Unknown agent type: {agent_type}, falling back to coordinator")
        return create_coordinator_agent(**kwargs)
"""
                # Replace the create_agent function
                content = re.sub(r'def create_agent\([^)]*\):[^}]*}', create_agent_code, content)
    
    # Write the modified content back to the file
    with open(agent_factory_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {agent_factory_path}")
    return True

def fix_agent_communication_tools():
    """Fix the agent communication tools to use real agents."""
    tools_path = "app/tools/agent_communication_tools.py"
    
    if not os.path.exists(tools_path):
        print(f"Error: {tools_path} not found")
        return False
    
    # Backup the file
    backup_file(tools_path)
    
    with open(tools_path, 'r') as f:
        content = f.read()
    
    # Check if there's a mock_response flag
    if "use_mock_response" in content or "mock_response" in content:
        # Replace any mock response flags with False
        content = re.sub(r'(use_mock_response|mock_response)\s*=\s*True', r'\1 = False', content)
        
        # Add a flag to indicate real agents are being used
        if "def get_agent_response" in content:
            # Find the get_agent_response function
            response_pattern = r'def get_agent_response\([^)]*\):\s*[^{]*{'
            response_match = re.search(response_pattern, content)
            if response_match:
                # Add code to ensure real agents are used
                response_code = """
def get_agent_response(agent_type, message, conversation_id=None, user_id=None, organization_id=None):
    \"\"\"Get a response from an agent.\"\"\"
    print(f"Getting real agent response from: {agent_type}")
    
    # Force use of real agents
    use_mock = False
    
    # Log the agent response request
    logging.info(f"Getting response from agent: {agent_type}, using real agent: {not use_mock}")
    
    try:
        # Create the agent
        agent = create_agent(agent_type)
        
        # Get the response
        response = agent.get_response(message)
        
        # Add a flag to indicate this is a real agent response
        if isinstance(response, dict):
            response["using_real_agent"] = True
        else:
            response = {
                "response": response,
                "using_real_agent": True
            }
        
        return response
    except Exception as e:
        logging.error(f"Error getting agent response: {str(e)}")
        return {
            "response": f"Error getting agent response: {str(e)}",
            "using_real_agent": False,
            "error": str(e)
        }
"""
                # Replace the get_agent_response function
                content = re.sub(r'def get_agent_response\([^)]*\):[^}]*}', response_code, content)
    
    # Write the modified content back to the file
    with open(tools_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {tools_path}")
    return True

def fix_app_adapter():
    """Fix the app adapter to use real agents."""
    adapter_path = "app_adapter_with_agents.py"
    
    if not os.path.exists(adapter_path):
        print(f"Error: {adapter_path} not found")
        return False
    
    # Backup the file
    backup_file(adapter_path)
    
    with open(adapter_path, 'r') as f:
        content = f.read()
    
    # Add import statements if they're missing
    imports_to_add = [
        "import logging",
        "import traceback",
        "import importlib",
        "import sys"
    ]
    
    for imp in imports_to_add:
        if imp not in content:
            content = imp + "\n" + content
    
    # Add a setup_logging function if it doesn't exist
    if "def setup_logging" not in content:
        setup_logging = """
def setup_logging():
    \"\"\"Set up logging configuration.\"\"\"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app_adapter.log')
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()
"""
        # Add after imports
        content = re.sub(r'(import [^\n]+\n+)+', r'\g<0>\n' + setup_logging, content)
    
    # Add code to dynamically import agent modules
    if "def get_agent_response" in content:
        # Find the get_agent_response function
        response_pattern = r'def get_agent_response\([^)]*\):\s*[^{]*{'
        response_match = re.search(response_pattern, content)
        if response_match:
            # Add code to ensure real agents are used
            response_code = """
def get_agent_response(agent_type, message, conversation_id=None, user_id=None, organization_id=None):
    \"\"\"Get a response from an agent.\"\"\"
    logger.info(f"Getting response from agent: {agent_type}")
    
    # Try multiple ways to import the agent modules
    try:
        # First try: Direct import
        try:
            logger.info("Trying direct import of agent modules")
            from app.agents.agent_factory import create_agent
            agent = create_agent(agent_type)
            logger.info(f"Successfully created agent using direct import: {agent_type}")
        except ImportError as e:
            logger.warning(f"Direct import failed: {str(e)}")
            
            # Second try: Dynamic import
            try:
                logger.info("Trying dynamic import of agent modules")
                agent_factory = importlib.import_module("app.agents.agent_factory")
                create_agent = getattr(agent_factory, "create_agent")
                agent = create_agent(agent_type)
                logger.info(f"Successfully created agent using dynamic import: {agent_type}")
            except ImportError as e:
                logger.warning(f"Dynamic import failed: {str(e)}")
                
                # Third try: Adjust sys.path and import
                try:
                    logger.info("Trying sys.path adjustment and import")
                    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
                    from app.agents.agent_factory import create_agent
                    agent = create_agent(agent_type)
                    logger.info(f"Successfully created agent using sys.path adjustment: {agent_type}")
                except ImportError as e:
                    logger.error(f"All import attempts failed: {str(e)}")
                    logger.error(f"sys.path: {sys.path}")
                    raise ImportError(f"Could not import agent modules: {str(e)}")
        
        # Get the response
        logger.info(f"Getting response from agent: {agent_type}")
        response = agent.get_response(message)
        
        # Add a flag to indicate this is a real agent response
        if isinstance(response, dict):
            response["using_real_agent"] = True
        else:
            response = {
                "response": response,
                "using_real_agent": True
            }
        
        logger.info(f"Got response from agent: {agent_type}")
        return response
    except Exception as e:
        logger.error(f"Error getting agent response: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "response": f"Error getting agent response: {str(e)}",
            "using_real_agent": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
"""
            # Replace the get_agent_response function
            content = re.sub(r'def get_agent_response\([^)]*\):[^}]*}', response_code, content)
    
    # Write the modified content back to the file
    with open(adapter_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {adapter_path}")
    return True

def main():
    """Main function."""
    print("Fixing agent mock responses...")
    
    # Fix the agent factory
    fix_agent_factory()
    
    # Fix the agent communication tools
    fix_agent_communication_tools()
    
    # Fix the app adapter
    fix_app_adapter()
    
    print("Done fixing agent mock responses.")
    print("Please redeploy the application for the changes to take effect.")

if __name__ == "__main__":
    main()
