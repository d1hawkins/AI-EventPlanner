#!/usr/bin/env python3
"""
Script to add more logging to the delegate_tasks function in coordinator_graph.py.
"""
import os
import shutil
import re
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

def fix_delegate_tasks_logging():
    """Add more logging to the delegate_tasks function in coordinator_graph.py."""
    file_path = "app/graphs/coordinator_graph.py"
    
    # Backup the file
    if not backup_file(file_path):
        return False
    
    # Read the file
    with open(file_path, "r") as f:
        content = f.read()
    
    # Find the delegate_tasks function
    delegate_tasks_match = re.search(r"def delegate_tasks\(state:.*?\):(.*?)def", content, re.DOTALL)
    if not delegate_tasks_match:
        print("Error: Could not find delegate_tasks function.")
        return False
    
    delegate_tasks_content = delegate_tasks_match.group(1)
    
    # Add initialization of agent_assignments if it doesn't exist
    if 'if "agent_assignments" not in state:' not in delegate_tasks_content:
        # Find where to add the initialization code
        # Add it at the beginning of the function
        init_code = """
        # Initialize agent_assignments if it doesn't exist
        if "agent_assignments" not in state:
            state["agent_assignments"] = []
            print("Initialized agent_assignments list.")
        else:
            print(f"Agent assignments already exist: {state['agent_assignments']}")
        """
        
        # Find the first line after the docstring
        docstring_end = re.search(r'""".*?"""', delegate_tasks_content, re.DOTALL)
        if docstring_end:
            docstring_end = docstring_end.end()
            new_delegate_tasks_content = delegate_tasks_content[:docstring_end] + init_code + delegate_tasks_content[docstring_end:]
        else:
            # If no docstring, add at the beginning of the function
            new_delegate_tasks_content = init_code + delegate_tasks_content
    else:
        new_delegate_tasks_content = delegate_tasks_content
    
    # Add logging before and after the LLM call
    new_delegate_tasks_content = new_delegate_tasks_content.replace(
        "# Determine task delegation using the LLM",
        "# Determine task delegation using the LLM\n        print(\"Calling LLM to determine task delegation.\")"
    )
    
    new_delegate_tasks_content = new_delegate_tasks_content.replace(
        "result = chain.invoke({\"messages\": [",
        "print(\"LLM prompt created.\")\n        result = chain.invoke({\"messages\": ["
    )
    
    new_delegate_tasks_content = new_delegate_tasks_content.replace(
        "# Parse the result",
        "print(f\"LLM result: {result.content}\")\n        # Parse the result"
    )
    
    # Add logging for JSON parsing
    new_delegate_tasks_content = new_delegate_tasks_content.replace(
        "delegation_data = json.loads(result.content)",
        "try:\n            delegation_data = json.loads(result.content)\n            print(f\"Parsed JSON: {delegation_data}\")\n        except Exception as e:\n            print(f\"Error parsing JSON: {e}\")\n            print(f\"Raw content: {result.content}\")\n            raise"
    )
    
    # Add logging for agent assignments
    new_delegate_tasks_content = new_delegate_tasks_content.replace(
        "# Add new assignments",
        "print(f\"Adding new assignments from delegation data: {delegation_data}\")\n            # Add new assignments"
    )
    
    new_delegate_tasks_content = new_delegate_tasks_content.replace(
        "state[\"agent_assignments\"].append({",
        "print(f\"Adding assignment for {assignment['agent_type']}: {assignment['task']}\")\n                    state[\"agent_assignments\"].append({"
    )
    
    # Replace the delegate_tasks function
    new_content = content.replace(delegate_tasks_content, new_delegate_tasks_content)
    
    # Write the updated content back to the file
    with open(file_path, "w") as f:
        f.write(new_content)
    
    print(f"Successfully updated {file_path} to add more logging to the delegate_tasks function.")
    return True

if __name__ == "__main__":
    fix_delegate_tasks_logging()
