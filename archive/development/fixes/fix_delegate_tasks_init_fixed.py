#!/usr/bin/env python3
"""
Script to fix the initialization of agent_assignments in the delegate_tasks function.
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

def fix_delegate_tasks_init():
    """Fix the initialization of agent_assignments in the delegate_tasks function."""
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
    
    # Check if the function already initializes agent_assignments
    if 'if "agent_assignments" not in state:' in delegate_tasks_content:
        print("The delegate_tasks function already initializes agent_assignments.")
        return True
    
    # Find where to add the initialization code
    # Add it after the docstring
    docstring_match = re.search(r'""".*?"""', delegate_tasks_content, re.DOTALL)
    if not docstring_match:
        print("Error: Could not find the docstring in the delegate_tasks function.")
        return False
    
    docstring_end = docstring_match.end()
    
    # Add the initialization code with proper indentation
    init_code = """
        # Initialize agent_assignments if it doesn't exist
        if "agent_assignments" not in state:
            state["agent_assignments"] = []
            
"""
    
    # Insert the initialization code after the docstring
    new_delegate_tasks_content = delegate_tasks_content[:docstring_end] + init_code + delegate_tasks_content[docstring_end:]
    
    # Replace the delegate_tasks function
    new_content = content.replace(delegate_tasks_content, new_delegate_tasks_content)
    
    # Write the updated content back to the file
    with open(file_path, "w") as f:
        f.write(new_content)
    
    print(f"Successfully updated {file_path} to initialize agent_assignments.")
    return True

if __name__ == "__main__":
    fix_delegate_tasks_init()
