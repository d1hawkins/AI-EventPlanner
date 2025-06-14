"""
Script to run the SaaS application with integrated agent system locally without Application Insights.

This script starts the FastAPI application with the tenant-aware agent system
using a local SQLite database and without requiring Application Insights.
It uses the fixed main_saas_local.py file that doesn't try to access request.user.
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv
import shutil

# Load environment variables from local config
load_dotenv(".env.saas.local")

# Force OpenAI as the LLM provider
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "gpt-4"

# Print startup information
print("Starting AI Event Planner SaaS with Agent Integration (Local - No App Insights)")
print("===========================================================")
print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
print(f"Version: {os.getenv('APP_VERSION', '1.0.0')}")
print(f"LLM Provider: {os.getenv('LLM_PROVIDER', 'openai')}")
print(f"Host: {os.getenv('HOST', '0.0.0.0')}")
print(f"Port: {os.getenv('PORT', '8006')}")
print(f"Database: {os.getenv('DATABASE_URL', 'sqlite:///./saas.db')}")
print("-----------------------------------------------------------")

# Create a temporary modified version of coordinator_graph.py that uses our local tools
def patch_coordinator_graph():
    """Create a patched version of coordinator_graph.py that uses our local tools."""
    coordinator_graph_path = "app/graphs/coordinator_graph.py"
    coordinator_graph_backup_path = "app/graphs/coordinator_graph.py.backup"
    
    # Backup the original file if not already backed up
    if not os.path.exists(coordinator_graph_backup_path):
        shutil.copy2(coordinator_graph_path, coordinator_graph_backup_path)
        print(f"Backed up original coordinator_graph.py to {coordinator_graph_backup_path}")
    
    # Read the original file
    with open(coordinator_graph_path, 'r') as f:
        content = f.read()
    
    # Replace the import for agent_communication_tools
    modified_content = content.replace(
        "from app.tools.agent_communication_tools import",
        "from app.tools.agent_communication_tools_local import"
    )
    
    # Write the modified content
    with open(coordinator_graph_path, 'w') as f:
        f.write(modified_content)
    
    print("Patched coordinator_graph.py to use local tools")

def restore_coordinator_graph():
    """Restore the original coordinator_graph.py."""
    coordinator_graph_path = "app/graphs/coordinator_graph.py"
    coordinator_graph_backup_path = "app/graphs/coordinator_graph.py.backup"
    
    if os.path.exists(coordinator_graph_backup_path):
        shutil.copy2(coordinator_graph_backup_path, coordinator_graph_path)
        print(f"Restored original coordinator_graph.py from backup")

# Run the application
if __name__ == "__main__":
    try:
        # Patch the coordinator graph to use our local tools
        patch_coordinator_graph()
        
        # Create the database tables if they don't exist
        print("Setting up database...")
        from app.db.base import Base, engine
        Base.metadata.create_all(bind=engine)
        print("Database setup complete.")
        
        # Run the application with our fixed main_saas_local.py
        uvicorn.run(
            "app.main_saas_local:app",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8006")),
            reload=True
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
        # Restore the original coordinator graph
        restore_coordinator_graph()
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {str(e)}")
        # Restore the original coordinator graph
        restore_coordinator_graph()
        sys.exit(1)
    finally:
        # Ensure we restore the original coordinator graph
        restore_coordinator_graph()
