#!/usr/bin/env python3
"""
Script to fix the issue with empty messages in the resource_planning_graph.py file.
"""

def fix_empty_messages():
    """
    Fix the resource_planning_graph.py file to filter out empty messages.
    """
    file_path = 'app/graphs/resource_planning_graph.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Find the analyze_requirements function
    for i, line in enumerate(lines):
        if "result = chain.invoke({\"messages\":" in line:
            # Replace the line with a version that filters out empty messages
            lines[i] = line.replace(
                "result = chain.invoke({\"messages\": [",
                "result = chain.invoke({\"messages\": ["
            ).replace(
                "{\"role\": m[\"role\"], \"content\": m[\"content\"]} for m in state[\"messages\"]]",
                "{\"role\": m[\"role\"], \"content\": m[\"content\"]} for m in state[\"messages\"] if m[\"content\"]]"
            )
    
    # Write the modified file
    with open(file_path, 'w') as f:
        f.writelines(lines)
    
    print(f"Fixed empty messages issue in {file_path}")

if __name__ == "__main__":
    fix_empty_messages()
