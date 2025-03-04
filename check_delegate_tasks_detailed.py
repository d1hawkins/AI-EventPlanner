#!/usr/bin/env python3
"""
Script to check the delegate_tasks function in coordinator_graph.py in more detail.
"""
import os
import re

def check_delegate_tasks_detailed():
    """Check the delegate_tasks function in coordinator_graph.py in more detail."""
    file_path = "app/graphs/coordinator_graph.py"
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
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
    
    # Check if the function creates agent assignments
    create_assignments = re.search(r"state\[\"agent_assignments\"\]", delegate_tasks_content)
    if not create_assignments:
        print("Error: The delegate_tasks function does not create agent assignments.")
        return False
    
    print("The delegate_tasks function creates agent assignments.")
    
    # Check if the function calls any agent tools
    agent_tools = [
        "ResourcePlanningTaskTool",
        "FinancialTaskTool",
        "StakeholderManagementTaskTool",
        "MarketingCommunicationsTaskTool",
        "ProjectManagementTaskTool"
    ]
    
    for tool in agent_tools:
        if tool in delegate_tasks_content:
            print(f"The delegate_tasks function calls the {tool}.")
        else:
            print(f"Warning: The delegate_tasks function does not call the {tool}.")
    
    # Check if the function handles errors
    error_handling = re.search(r"except Exception as e", delegate_tasks_content)
    if not error_handling:
        print("Error: The delegate_tasks function does not handle errors.")
        return False
    
    print("The delegate_tasks function handles errors.")
    
    # Check if the function creates tasks
    create_tasks = re.search(r"task=assignment\[\"task\"\]", delegate_tasks_content)
    if not create_tasks:
        print("Error: The delegate_tasks function does not create tasks.")
        return False
    
    print("The delegate_tasks function creates tasks.")
    
    # Check if the function is actually creating any agent assignments
    create_agent_assignments = re.search(r"state\[\"agent_assignments\"\]\.append", delegate_tasks_content)
    if not create_agent_assignments:
        print("Error: The delegate_tasks function does not append to agent_assignments.")
        return False
    
    print("The delegate_tasks function appends to agent_assignments.")
    
    # Check if the function is initializing agent_assignments if it doesn't exist
    init_agent_assignments = re.search(r"if \"agent_assignments\" not in state", delegate_tasks_content)
    if not init_agent_assignments:
        print("Warning: The delegate_tasks function does not initialize agent_assignments if it doesn't exist.")
    else:
        print("The delegate_tasks function initializes agent_assignments if it doesn't exist.")
    
    # Check if the function is actually creating any tasks
    create_tasks = re.search(r"tasks = \[", delegate_tasks_content)
    if not create_tasks:
        print("Error: The delegate_tasks function does not create any tasks.")
        return False
    
    print("The delegate_tasks function creates tasks.")
    
    # Print the tasks that are being created
    tasks_match = re.search(r"tasks = \[(.*?)\]", delegate_tasks_content, re.DOTALL)
    if tasks_match:
        tasks = tasks_match.group(1)
        print("\nTasks being created:")
        print(tasks)
    
    return True

if __name__ == "__main__":
    check_delegate_tasks_detailed()
