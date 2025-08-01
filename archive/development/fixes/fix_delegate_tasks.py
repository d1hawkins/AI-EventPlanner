#!/usr/bin/env python3
"""
Script to fix the delegate_tasks function in coordinator_graph.py to handle the case where state['proposal'] is None.
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
    """Fix the delegate_tasks function in coordinator_graph.py to handle the case where state['proposal'] is None."""
    file_path = "app/graphs/coordinator_graph.py"
    
    # Backup the file
    if not backup_file(file_path):
        return False
    
    # Read the file
    with open(file_path, "r") as f:
        content = f.read()
    
    # Find the line with the error
    error_line = "Proposal: {state['proposal']['content'] if 'proposal' in state else 'Not yet generated'}"
    if error_line not in content:
        print("Error: Could not find the line with the error.")
        return False
    
    # Replace the line with a fixed version
    fixed_line = "Proposal: {state['proposal']['content'] if 'proposal' in state and state['proposal'] is not None else 'Not yet generated'}"
    content = content.replace(error_line, fixed_line)
    
    # Write the updated content back to the file
    with open(file_path, "w") as f:
        f.write(content)
    
    print(f"Successfully updated {file_path} to handle the case where state['proposal'] is None.")
    return True

if __name__ == "__main__":
    fix_delegate_tasks()
