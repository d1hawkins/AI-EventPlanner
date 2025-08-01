#!/usr/bin/env python3
"""
Script to check if the changes to the coordinator_graph.py file were applied correctly.
"""
import os
import re

def check_coordinator_graph():
    """Check if the changes to the coordinator_graph.py file were applied correctly."""
    file_path = "app/graphs/coordinator_graph.py"
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False
    
    # Read the file
    with open(file_path, "r") as f:
        content = f.read()
    
    # Check if the code to check for proposal approval was added
    approval_check = re.search(r"# Check if the user is approving a proposal", content)
    if not approval_check:
        print("Error: Could not find the code to check for proposal approval.")
        return False
    
    print("Found the code to check for proposal approval.")
    
    # Check if the code to transition to the implementation phase was added
    implementation_transition = re.search(r"state\[\"current_phase\"\] = \"implementation\"", content)
    if not implementation_transition:
        print("Error: Could not find the code to transition to the implementation phase.")
        return False
    
    print("Found the code to transition to the implementation phase.")
    
    # Check if the code to set the next_action to delegate_tasks was added
    delegate_tasks = re.search(r"state\[\"next_action\"\] = \"delegate_tasks\"", content)
    if not delegate_tasks:
        print("Error: Could not find the code to set the next_action to delegate_tasks.")
        return False
    
    print("Found the code to set the next_action to delegate_tasks.")
    
    # Check if the code to add a message about transitioning to implementation was added
    implementation_message = re.search(r"Thank you for approving the proposal! I'll now begin implementing the plan by delegating tasks to our specialized agents.", content)
    if not implementation_message:
        print("Error: Could not find the code to add a message about transitioning to implementation.")
        return False
    
    print("Found the code to add a message about transitioning to implementation.")
    
    print("All changes to the coordinator_graph.py file were applied correctly.")
    return True

if __name__ == "__main__":
    check_coordinator_graph()
