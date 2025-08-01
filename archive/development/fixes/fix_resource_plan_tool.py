#!/usr/bin/env python3
"""
Script to fix the attendee_count issue in the ResourcePlanGenerationTool._run method.
"""

def fix_resource_plan_tool():
    """
    Fix the attendee_count issue in the ResourcePlanGenerationTool._run method.
    """
    file_path = 'app/graphs/resource_planning_graph.py'
    
    # Read the existing file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the ResourcePlanGenerationTool._run method
    run_method_start = content.find("    def _run(self, event_details: Dict[str, Any], venue: Dict[str, Any],")
    
    if run_method_start == -1:
        print("Could not find the ResourcePlanGenerationTool._run method in the file.")
        return
    
    # Find the staffing section in the resource plan
    staffing_section = content.find('            "staffing": {', run_method_start)
    
    if staffing_section == -1:
        print("Could not find the staffing section in the ResourcePlanGenerationTool._run method.")
        return
    
    # Find the event_team count line
    event_team_count_line = '                    "count": max(3, event_details.get("attendee_count", 100) // 50),'
    event_team_count_fixed = '                    "count": max(3, int(event_details.get("attendee_count", 100) or 100) // 50),'
    
    # Replace the event_team count line
    new_content = content.replace(event_team_count_line, event_team_count_fixed)
    
    # Find the teardown_team count line
    teardown_team_count_line = '                    "count": max(2, event_details.get("attendee_count", 100) // 100),'
    teardown_team_count_fixed = '                    "count": max(2, int(event_details.get("attendee_count", 100) or 100) // 100),'
    
    # Replace the teardown_team count line
    new_content = new_content.replace(teardown_team_count_line, teardown_team_count_fixed)
    
    # Write the new content to the file
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Fixed attendee_count issues in ResourcePlanGenerationTool._run method in {file_path}")

if __name__ == "__main__":
    fix_resource_plan_tool()
