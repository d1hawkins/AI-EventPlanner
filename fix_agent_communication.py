#!/usr/bin/env python3
"""
Script to fix the agent communication tools to improve error handling and visibility.
This script modifies the agent_communication_tools.py file to add better error handling,
logging, and to make error messages visible to users.
"""
import os
import re
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
        content = re.sub(
            r"import json",
            "import json\nimport logging\nfrom datetime import datetime",
            content
        )
    
    # Add logging setup
    if "logger = logging.getLogger" not in content:
        content = re.sub(
            r"class ResourcePlanningTaskTool\(BaseTool\):",
            "# Set up logger\nlogger = logging.getLogger(__name__)\n\nclass ResourcePlanningTaskTool(BaseTool):",
            content
        )
    
    # Add _handle_error method to ResourcePlanningTaskTool class
    if "_handle_error" not in content:
        content = re.sub(
            r"(\s+)def _run\(self, \*\*kwargs\):",
            r"""\1def _handle_error(self, error, task_type, task_description):
        \"\"\"Handle errors in a standardized way.\"\"\"
        error_type = type(error).__name__
        error_message = str(error)
        
        # Log the error
        logger.error(f"Error in {task_type} task: {error_message}")
        logger.error(f"Task description: {task_description}")
        logger.error(f"Error type: {error_type}")
        logger.error(f"Error details: {error}")
        
        # Categorize the error
        if "timeout" in error_message.lower():
            category = "Timeout Error"
            suggestion = "The specialized agent took too long to respond. Try simplifying the task or breaking it into smaller parts."
        elif "token limit" in error_message.lower() or "context length" in error_message.lower():
            category = "Token Limit Error"
            suggestion = "The task is too complex for the model's token limit. Try simplifying the task or breaking it into smaller parts."
        elif "rate limit" in error_message.lower():
            category = "Rate Limit Error"
            suggestion = "The API rate limit was exceeded. Try again later or reduce the frequency of requests."
        elif "permission" in error_message.lower() or "access" in error_message.lower():
            category = "Permission Error"
            suggestion = "The specialized agent doesn't have permission to perform this task. Check API keys and permissions."
        elif "not found" in error_message.lower():
            category = "Not Found Error"
            suggestion = "A resource required for this task was not found. Check that all required resources exist."
        else:
            category = "General Error"
            suggestion = "An unexpected error occurred. Check the logs for more details."
        
        # Create a detailed error message for the user
        user_message = f"""
**Error in {task_type} Task**

**Category:** {category}
**Message:** {error_message}
**Suggestion:** {suggestion}

The system was unable to complete the requested task. Please try again with a simplified request or contact support if the issue persists.
"""
        
        # Return a standardized error object
        return {
            "error_type": error_type,
            "error_message": error_message,
            "error_category": category,
            "suggestion": suggestion,
            "user_message": user_message,
            "timestamp": datetime.now().isoformat()
        }

\1def _run(self, **kwargs):",
            content
        )
    
    # Update the _run method to use _handle_error and remove ephemeral flag
    content = re.sub(
        r'(\s+)except Exception as e:(\s+)return \{\s+"result": f"Error: \{str\(e\)\}",\s+"ephemeral": True\s+\}',
        r'\1except Exception as e:\1    error_info = self._handle_error(e, self.task_type, task_description)\1    return {\1        "result": error_info["user_message"],\1        "error": error_info\1    }',
        content
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
    
    # Update the delegate_tasks function to better handle errors
    if "Handle errors from specialized agents" not in content:
        # Find the delegate_tasks function
        delegate_tasks_match = re.search(r"def delegate_tasks\(state:.*?\):", content, re.DOTALL)
        if delegate_tasks_match:
            # Find the end of the function
            function_start = delegate_tasks_match.start()
            # Look for the next function definition after delegate_tasks
            next_function_match = re.search(r"def \w+\(", content[function_start + 10:])
            if next_function_match:
                function_end = function_start + 10 + next_function_match.start()
                function_content = content[function_start:function_end]
                
                # Update the function to better handle errors
                updated_function = function_content.replace(
                    'if "error" in result:',
                    'if "error" in result:\n        # Handle errors from specialized agents\n        error_info = result.get("error", {})\n        error_message = error_info.get("user_message", result.get("result", "Unknown error"))\n        \n        # Update the assignment status\n        for assignment in state["agent_assignments"]:\n            if assignment["agent_type"] == agent_type and assignment["task"] == task and assignment["status"] == "pending":\n                assignment["status"] = "failed"\n                assignment["error"] = error_info\n                assignment["completed_at"] = datetime.now().isoformat()\n        \n        # Add the error message to the conversation\n        state["messages"].append({\n            "role": "assistant",\n            "content": f"I encountered an issue while working with the {agent_type} agent: {error_message}"\n        })'
                )
                
                # Replace the function in the content
                content = content[:function_start] + updated_function + content[function_end:]
    
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
