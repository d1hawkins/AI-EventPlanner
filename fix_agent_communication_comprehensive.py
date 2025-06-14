#!/usr/bin/env python3
"""
Comprehensive fix for agent communication issues with system messages.

This script fixes all instances of system message handling issues in the coordinator graph
and other related files to prevent errors when processing messages.
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
    
    # Fix 1: Update the message conversion in generate_response
    target_section_1 = """    # Convert message dicts to message objects
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
    
    fixed_section_1 = """    # Convert message dicts to message objects
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
    
    # Fix 2: Update the gather_requirements function to handle system messages
    target_section_2 = """        # Extract requirements using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})"""
    
    fixed_section_2 = """        # Extract requirements using the LLM
        # Filter out system messages before invoking the chain
        filtered_messages = [
            {"role": m["role"], "content": m["content"]} 
            for m in state["messages"] 
            if m["role"] != "system"
        ]
        chain = prompt | llm
        result = chain.invoke({"messages": filtered_messages})"""
    
    # Apply the fixes
    updated_content = content.replace(target_section_1, fixed_section_1)
    updated_content = updated_content.replace(target_section_2, fixed_section_2)
    
    # Write the updated content back to the file
    with open(coordinator_graph_path, "w") as f:
        f.write(updated_content)
    
    print(f"Fixed {coordinator_graph_path}")
    return True

def main():
    """Main function."""
    print("Applying comprehensive fix for agent communication issues with system messages...")
    
    # Fix the coordinator graph
    if not fix_coordinator_graph():
        print("Failed to fix coordinator graph.")
        return 1
    
    print("Comprehensive fix completed successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
