"""
Script to patch agent_factory.py to use local logging utilities without Application Insights.
"""

import os
import shutil

def patch_agent_factory():
    """Create a patched version of agent_factory.py that uses our local logging utilities."""
    agent_factory_path = "app/agents/agent_factory.py"
    agent_factory_backup_path = "app/agents/agent_factory.py.backup"
    
    # Backup the original file if not already backed up
    if not os.path.exists(agent_factory_backup_path):
        shutil.copy2(agent_factory_path, agent_factory_backup_path)
        print(f"Backed up original agent_factory.py to {agent_factory_backup_path}")
    
    # Read the original file
    with open(agent_factory_path, 'r') as f:
        content = f.read()
    
    # Replace the import for logging_utils
    modified_content = content.replace(
        "from app.utils.logging_utils import",
        "from app.utils.logging_utils_local import"
    )
    
    # Replace the enable_app_insights parameter to False
    modified_content = modified_content.replace(
        "enable_app_insights=True",
        "enable_app_insights=False"
    )
    
    # Write the modified content
    with open(agent_factory_path, 'w') as f:
        f.write(modified_content)
    
    print("Patched agent_factory.py to use local logging utilities")

def restore_agent_factory():
    """Restore the original agent_factory.py."""
    agent_factory_path = "app/agents/agent_factory.py"
    agent_factory_backup_path = "app/agents/agent_factory.py.backup"
    
    if os.path.exists(agent_factory_backup_path):
        shutil.copy2(agent_factory_backup_path, agent_factory_path)
        print(f"Restored original agent_factory.py from backup")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_agent_factory()
    else:
        patch_agent_factory()
