#!/usr/bin/env python3
"""
Script to fix the delegate_tasks function in coordinator_graph.py to append to agent_assignments.
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

def fix_delegate_tasks():
    """Fix the delegate_tasks function in coordinator_graph.py to append to agent_assignments."""
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
    
    # Find the tasks list
    tasks_match = re.search(r"tasks = \[(.*?)\]", delegate_tasks_content, re.DOTALL)
    if not tasks_match:
        print("Error: Could not find the tasks list.")
        return False
    
    tasks = tasks_match.group(1)
    
    # Find where to add the code to append to agent_assignments
    after_tasks_match = re.search(r"tasks = \[.*?\]", delegate_tasks_content, re.DOTALL)
    if not after_tasks_match:
        print("Error: Could not find where to add the code to append to agent_assignments.")
        return False
    
    after_tasks = after_tasks_match.end()
    
    # Add code to initialize agent_assignments if it doesn't exist
    init_agent_assignments = """
        # Initialize agent_assignments if it doesn't exist
        if "agent_assignments" not in state:
            state["agent_assignments"] = []
    """
    
    # Add code to append to agent_assignments
    append_agent_assignments = """
        # Create agent assignments for each task
        for task in tasks:
            agent_type = task["agent_type"]
            task_description = task["task"]
            
            # Create a new agent assignment
            assignment = {
                "agent_type": agent_type,
                "task": task_description,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "completed_at": None,
                "result": None,
                "error": None
            }
            
            # Append the assignment to agent_assignments
            state["agent_assignments"].append(assignment)
    """
    
    # Insert the code after the tasks list
    new_delegate_tasks_content = delegate_tasks_content[:after_tasks] + init_agent_assignments + append_agent_assignments + delegate_tasks_content[after_tasks:]
    
    # Replace the delegate_tasks function
    content = content.replace(delegate_tasks_content, new_delegate_tasks_content)
    
    # Write the updated content back to the file
    with open(file_path, "w") as f:
        f.write(content)
    
    print(f"Successfully updated {file_path} to append to agent_assignments.")
    return True

if __name__ == "__main__":
    import re
    fix_delegate_tasks()
