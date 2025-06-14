"""
Script to run the SaaS application with integrated agent system locally without Application Insights.

This script:
1. Patches the coordinator_graph.py to use local tools
2. Patches the agent_factory.py to use local logging utilities
3. Starts the FastAPI application with the tenant-aware agent system
4. Restores the original files when done
"""

import os
import sys
import subprocess
import signal
import time

def run_patch_script():
    """Run the patch_agent_factory.py script."""
    print("Patching agent_factory.py...")
    subprocess.run(["python3", "patch_agent_factory.py"], check=True)

def restore_patch():
    """Restore the original agent_factory.py."""
    print("Restoring agent_factory.py...")
    subprocess.run(["python3", "patch_agent_factory.py", "restore"], check=True)

def run_saas_script():
    """Run the run_saas_with_agents_local_no_appinsights.py script."""
    print("Starting SaaS application...")
    process = subprocess.Popen(["python3", "run_saas_with_agents_local_no_appinsights.py"])
    return process

def signal_handler(sig, frame):
    """Handle Ctrl+C to ensure proper cleanup."""
    print("\nShutting down...")
    restore_patch()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Patch the agent_factory.py
        run_patch_script()
        
        # Run the SaaS application
        process = run_saas_script()
        
        # Wait for the process to complete
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        # Ensure we restore the original agent_factory.py
        restore_patch()
