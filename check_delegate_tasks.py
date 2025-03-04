#!/usr/bin/env python3
"""
Script to check the delegate_tasks function in coordinator_graph.py
to see if there's an issue that might be preventing specialized agents from being invoked.
"""
import os
import re

def check_delegate_tasks():
    """Check the delegate_tasks function in coordinator_graph.py."""
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
    print("=== delegate_tasks function ===")
    print(delegate_tasks_content)
    print("==============================")
    
    # Check if the function is called from anywhere
    delegate_tasks_calls = re.findall(r"delegate_tasks\(", content)
    print(f"Number of calls to delegate_tasks: {len(delegate_tasks_calls)}")
    
    # Find where the function is called
    for i, call in enumerate(delegate_tasks_calls):
        call_match = re.search(r"(.*?)delegate_tasks\(", content)
        if call_match:
            print(f"Call {i+1}: {call_match.group(1).strip()}")
    
    # Check if the function is called from the coordinator graph
    coordinator_graph_match = re.search(r"coordinator_graph = .*?\.add_node\(.*?\)", content, re.DOTALL)
    if coordinator_graph_match:
        coordinator_graph_content = coordinator_graph_match.group(0)
        print("\n=== Coordinator Graph Definition ===")
        print(coordinator_graph_content)
        print("===================================")
        
        # Check if delegate_tasks is in the graph
        if "delegate_tasks" in coordinator_graph_content:
            print("delegate_tasks is included in the coordinator graph.")
        else:
            print("WARNING: delegate_tasks is NOT included in the coordinator graph.")
    
    # Check if there's a phase transition to implementation
    phase_transitions = re.findall(r"if state\[\"current_phase\"\] == \"(.*?)\"", content)
    print("\nPhase transitions:")
    for phase in phase_transitions:
        print(f"- {phase}")
    
    # Check if there's a condition that might prevent delegate_tasks from being called
    if "if state[\"current_phase\"] == \"implementation\"" in content:
        print("\nThe delegate_tasks function is called during the implementation phase.")
        
        # Check how the phase is changed to implementation
        implementation_transition = re.search(r"state\[\"current_phase\"\] = \"implementation\"", content)
        if implementation_transition:
            # Find the surrounding context
            start = max(0, implementation_transition.start() - 200)
            end = min(len(content), implementation_transition.end() + 200)
            context = content[start:end]
            print("\n=== Context for transition to implementation phase ===")
            print(context)
            print("====================================================")
        else:
            print("WARNING: Could not find where the phase is changed to implementation.")
    else:
        print("\nWARNING: Could not find a condition for the implementation phase.")
    
    return True

if __name__ == "__main__":
    check_delegate_tasks()
