#!/usr/bin/env python3
"""
Script to fix the attendee_count issue in the resource_planning_graph.py file.
"""

def fix_attendee_count():
    """
    Fix the attendee_count issue in the resource_planning_graph.py file.
    """
    file_path = 'app/graphs/resource_planning_graph.py'
    
    # Read the existing file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the plan_equipment function
    start_marker = "def plan_equipment(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:"
    plan_equipment_start = content.find(start_marker)
    
    if plan_equipment_start == -1:
        print("Could not find the plan_equipment function in the file.")
        return
    
    # Find the attendee_count line
    attendee_count_line = "        attendee_count = state[\"event_details\"].get(\"attendee_count\", 100)"
    attendee_count_fixed = "        # Ensure attendee_count is an integer with a default value of 100\n        attendee_count = int(state[\"event_details\"].get(\"attendee_count\", 100) or 100)"
    
    # Replace the attendee_count line
    new_content = content.replace(attendee_count_line, attendee_count_fixed)
    
    # Write the new content to the file
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Fixed attendee_count issue in {file_path}")

if __name__ == "__main__":
    fix_attendee_count()
