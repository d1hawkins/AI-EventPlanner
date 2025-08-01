#!/usr/bin/env python3
"""
Simple script to fix the agent communication tools to improve error handling and visibility.
"""
import os
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the file."""
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{file_path}.backup_{timestamp}"
        shutil.copy2(file_path, backup_file)
        print(f"Created backup of {file_path}: {backup_file}")
        return True
    else:
        print(f"Error: File {file_path} not found.")
        return False

def fix_agent_communication_tools():
    """Fix the agent_communication_tools.py file."""
    file_path = "app/tools/agent_communication_tools.py"
    
    # Backup the file
    if not backup_file(file_path):
        return False
    
    # Read the file
    with open(file_path, "r") as f:
        content = f.read()
    
    # Add imports for logging
    if "import logging" not in content:
        content = content.replace(
            "import json",
            "import json\nimport logging\nfrom datetime import datetime"
        )
    
    # Add logging setup
    if "logger = logging.getLogger" not in content:
        content = content.replace(
            "class ResourcePlanningTaskTool(BaseTool):",
            "# Set up logger\nlogger = logging.getLogger(__name__)\n\nclass ResourcePlanningTaskTool(BaseTool):"
        )
    
    # Remove ephemeral flag from error messages
    content = content.replace(
        '"result": f"Error: {str(e)}", "ephemeral": True',
        '"result": f"Error: {str(e)}", "error": {"error_type": type(e).__name__, "error_message": str(e)}'
    )
    
    # Write the updated content back to the file
    with open(file_path, "w") as f:
        f.write(content)
    
    print(f"Successfully updated {file_path} with improved error handling.")
    return True

def fix_coordinator_graph():
    """Fix the coordinator_graph.py file to better handle errors from specialized agents."""
    file_path = "app/graphs/coordinator_graph.py"
    
    # Backup the file
    if not backup_file(file_path):
        return False
    
    # Read the file
    with open(file_path, "r") as f:
        content = f.read()
    
    # Add import for datetime if not already present
    if "from datetime import datetime" not in content:
        content = content.replace(
            "import json",
            "import json\nfrom datetime import datetime"
        )
    
    # Update the delegate_tasks function to better handle errors
    if 'if "error" in result:' in content:
        content = content.replace(
            'if "error" in result:',
            'if "error" in result:\n        # Handle errors from specialized agents\n        error_info = result.get("error", {})\n        error_message = result.get("result", "Unknown error")\n        \n        # Update the assignment status\n        for assignment in state["agent_assignments"]:\n            if assignment["agent_type"] == agent_type and assignment["task"] == task and assignment["status"] == "pending":\n                assignment["status"] = "failed"\n                assignment["error"] = error_info\n                assignment["completed_at"] = datetime.now().isoformat()\n        \n        # Add the error message to the conversation\n        state["messages"].append({\n            "role": "assistant",\n            "content": f"I encountered an issue while working with the {agent_type} agent: {error_message}"\n        })'
        )
    
    # Write the updated content back to the file
    with open(file_path, "w") as f:
        f.write(content)
    
    print(f"Successfully updated {file_path} with improved error handling.")
    return True

def main():
    """Main function."""
    print("Fixing agent communication tools...")
    if fix_agent_communication_tools():
        print("Successfully fixed agent_communication_tools.py")
    else:
        print("Failed to fix agent_communication_tools.py")
    
    print("\nFixing coordinator graph...")
    if fix_coordinator_graph():
        print("Successfully fixed coordinator_graph.py")
    else:
        print("Failed to fix coordinator_graph.py")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
