#!/usr/bin/env python3
"""
Fix for agent communication issue with system messages.

This script fixes the issue with system messages in the coordinator graph
causing errors when processing the second prompt.
"""

import os
import sys
from pathlib import Path

def fix_coordinator_graph():
    """Fix the coordinator graph to properly handle system messages."""
    coordinator_graph_path = Path("app/graphs/coordinator_graph.py")
    
    if not coordinator_graph_path.exists():
        print(f"Error: {coordinator_graph_path} not found.")
        return False
    
    # Read the file
    with open(coordinator_graph_path, "r") as f:
        content = f.read()
    
    # Find the section that converts message dicts to message objects
    target_section = """    # Convert message dicts to message objects
    message_objects = []
    for m in state["messages"]:
        role = m.get("role")
        content = m.get("content")
        if role == "user":
            message_objects.append(HumanMessage(content=content))
        elif role == "assistant":
            message_objects.append(AIMessage(content=content))
        # Avoid adding system messages from history here, as the template adds one
        # elif role == "system":
        #     message_objects.append(SystemMessage(content=content))"""
    
    # Create the fixed section
    fixed_section = """    # Convert message dicts to message objects
    message_objects = []
    for m in state["messages"]:
        role = m.get("role")
        content = m.get("content")
        # Skip system messages to avoid conflicts with the template
        if role == "system":
            continue
        elif role == "user":
            message_objects.append(HumanMessage(content=content))
        elif role == "assistant":
            message_objects.append(AIMessage(content=content))"""
    
    # Replace the section
    updated_content = content.replace(target_section, fixed_section)
    
    # Write the updated content back to the file
    with open(coordinator_graph_path, "w") as f:
        f.write(updated_content)
    
    print(f"Fixed {coordinator_graph_path}")
    return True

def main():
    """Main function."""
    print("Fixing agent communication issue with system messages...")
    
    # Fix the coordinator graph
    if not fix_coordinator_graph():
        print("Failed to fix coordinator graph.")
        return 1
    
    print("Fix completed successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
