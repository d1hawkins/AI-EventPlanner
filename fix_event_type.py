#!/usr/bin/env python3
"""
Script to fix the event_type issue in the resource_planning_graph.py file.
"""

def fix_event_type():
    """
    Fix the event_type issue in the resource_planning_graph.py file.
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
    
    # Find the event_type line
    event_type_line = "        event_type = state[\"event_details\"].get(\"event_type\", \"conference\")"
    event_type_fixed = "        # Ensure event_type is a string with a default value\n        event_type = state[\"event_details\"].get(\"event_type\", \"conference\") or \"conference\""
    
    # Replace the event_type line
    new_content = content.replace(event_type_line, event_type_fixed)
    
    # Also fix the if statements in the _run method of EquipmentPlanningTool
    # Find the EquipmentPlanningTool._run method
    run_method_start = content.find("    def _run(self, event_type: str, attendee_count: int, venue_type: str,")
    
    if run_method_start == -1:
        print("Could not find the EquipmentPlanningTool._run method in the file.")
        return
    
    # Find the if statements with missing commas
    if_statement1 = "if event_type.lower() in [\"conference\", \"corporate\", \"meeting\"]:"
    if_statement2 = "elif event_type.lower() in [\"wedding\", \"gala\", \"social\"]:"
    
    # Check if these statements already have commas
    if if_statement1 not in content or if_statement2 not in content:
        # Find the incorrect if statements
        incorrect_if1 = "if event_type.lower() in [\"conference\" \"corporate\" \"meeting\"]:"
        incorrect_if2 = "elif event_type.lower() in [\"wedding\" \"gala\" \"social\"]:"
        
        # Replace with correct if statements
        new_content = new_content.replace(incorrect_if1, if_statement1)
        new_content = new_content.replace(incorrect_if2, if_statement2)
    
    # Write the new content to the file
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Fixed event_type issue in {file_path}")

if __name__ == "__main__":
    fix_event_type()
