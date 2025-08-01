#!/usr/bin/env python3
"""
Script to fix the coordinator_graph.py file to ensure that it transitions to the implementation phase
when the user approves the proposal.
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

def fix_coordinator_graph():
    """Fix the coordinator_graph.py file to ensure that it transitions to the implementation phase."""
    file_path = "app/graphs/coordinator_graph.py"
    
    # Backup the file
    if not backup_file(file_path):
        return False
    
    # Read the file
    with open(file_path, "r") as f:
        content = f.read()
    
    # Find the generate_proposal function
    generate_proposal_match = re.search(r"def generate_proposal\(state:.*?\):(.*?)def", content, re.DOTALL)
    if not generate_proposal_match:
        print("Error: Could not find generate_proposal function.")
        return False
    
    generate_proposal_content = generate_proposal_match.group(1)
    print("=== generate_proposal function ===")
    print(generate_proposal_content)
    print("==============================")
    
    # Find the generate_response function
    generate_response_match = re.search(r"def generate_response\(state:.*?\):", content)
    if not generate_response_match:
        print("Error: Could not find generate_response function.")
        return False
    
    # Find the start of the function
    function_start = generate_response_match.start()
    
    # Find the end of the function (the next function definition or the end of the file)
    next_function_match = re.search(r"def \w+\(", content[function_start + 20:])
    if next_function_match:
        function_end = function_start + 20 + next_function_match.start()
    else:
        function_end = len(content)
    
    generate_response_content = content[function_start:function_end]
    print("=== generate_response function ===")
    print(generate_response_content[:200] + "...")  # Print just the beginning to avoid too much output
    print("==============================")
    
    # Add code to transition to implementation phase when the user approves the proposal
    if "approve" not in generate_response_content.lower() or "proposal" not in generate_response_content.lower():
        # Add code to check for proposal approval
        updated_generate_response = generate_response_content.replace(
            "# Generate a response based on the current state",
            """# Generate a response based on the current state
            
            # Check if the user is approving a proposal
            if state["messages"] and state["messages"][-1]["role"] == "user":
                user_message = state["messages"][-1]["content"].lower()
                if "approve" in user_message and "proposal" in user_message:
                    print("User approved the proposal. Transitioning to implementation phase.")
                    state["current_phase"] = "implementation"
                    
                    # Add a message about transitioning to implementation
                    state["messages"].append({
                        "role": "assistant",
                        "content": "Thank you for approving the proposal! I'll now begin implementing the plan by delegating tasks to our specialized agents."
                    })
                    
                    # Delegate tasks to specialized agents
                    return delegate_tasks(state)"""
        )
        
        # Replace the generate_response function
        content = content.replace(generate_response_content, updated_generate_response)
        
        print("Added code to transition to implementation phase when the user approves the proposal.")
    else:
        print("The generate_response function already checks for proposal approval.")
    
    # Write the updated content back to the file
    with open(file_path, "w") as f:
        f.write(content)
    
    print(f"Successfully updated {file_path} to transition to implementation phase when the user approves the proposal.")
    return True

if __name__ == "__main__":
    fix_coordinator_graph()
