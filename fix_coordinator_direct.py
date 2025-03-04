#!/usr/bin/env python3
"""
Script to directly modify the coordinator_graph.py file to add code to transition to the implementation phase
when the user approves the proposal.
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

def fix_coordinator_graph():
    """Fix the coordinator_graph.py file to ensure that it transitions to the implementation phase."""
    file_path = "app/graphs/coordinator_graph.py"
    
    # Backup the file
    if not backup_file(file_path):
        return False
    
    # Read the file
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    # Find the generate_response function
    generate_response_start = -1
    for i, line in enumerate(lines):
        if "def generate_response" in line:
            generate_response_start = i
            break
    
    if generate_response_start == -1:
        print("Error: Could not find generate_response function.")
        return False
    
    # Find where to insert our code (after the function definition and docstring)
    insert_point = -1
    for i in range(generate_response_start, len(lines)):
        if "# Create the coordinator prompt" in lines[i]:
            insert_point = i
            break
    
    if insert_point == -1:
        print("Error: Could not find insertion point in generate_response function.")
        return False
    
    # Insert our code to check for proposal approval
    new_code = [
        "        # Check if the user is approving a proposal\n",
        "        if state[\"messages\"] and state[\"messages\"][-1][\"role\"] == \"user\":\n",
        "            user_message = state[\"messages\"][-1][\"content\"].lower()\n",
        "            if \"approve\" in user_message and \"proposal\" in user_message:\n",
        "                print(\"User approved the proposal. Transitioning to implementation phase.\")\n",
        "                state[\"current_phase\"] = \"implementation\"\n",
        "                \n",
        "                # Add a message about transitioning to implementation\n",
        "                state[\"messages\"].append({\n",
        "                    \"role\": \"assistant\",\n",
        "                    \"content\": \"Thank you for approving the proposal! I'll now begin implementing the plan by delegating tasks to our specialized agents.\"\n",
        "                })\n",
        "                \n",
        "                # Delegate tasks to specialized agents\n",
        "                return delegate_tasks(state)\n",
        "\n"
    ]
    
    # Insert the new code
    lines = lines[:insert_point] + new_code + lines[insert_point:]
    
    # Write the updated content back to the file
    with open(file_path, "w") as f:
        f.writelines(lines)
    
    print(f"Successfully updated {file_path} to transition to implementation phase when the user approves the proposal.")
    return True

if __name__ == "__main__":
    fix_coordinator_graph()
