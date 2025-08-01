#!/usr/bin/env python3
"""
Script to switch between LLM providers (OpenAI and Google) for testing.
This script modifies the .env file to change the LLM_PROVIDER setting.
"""
import os
import sys
import re
from datetime import datetime

def backup_env_file():
    """Create a backup of the current .env file."""
    if os.path.exists(".env"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f".env.backup_{timestamp}"
        with open(".env", "r") as src, open(backup_file, "w") as dst:
            dst.write(src.read())
        print(f"Created backup of .env file: {backup_file}")
        return True
    else:
        print("Error: .env file not found.")
        return False

def switch_provider(provider):
    """
    Switch the LLM provider in the .env file.
    
    Args:
        provider: The provider to switch to ("openai" or "google")
    """
    if provider.lower() not in ["openai", "google"]:
        print(f"Error: Invalid provider '{provider}'. Must be 'openai' or 'google'.")
        return False
    
    # Backup the .env file
    if not backup_env_file():
        return False
    
    # Read the current .env file
    with open(".env", "r") as f:
        env_content = f.read()
    
    # Replace the LLM_PROVIDER line
    pattern = r"LLM_PROVIDER=.*"
    replacement = f"LLM_PROVIDER={provider.lower()}"
    
    if re.search(pattern, env_content):
        new_content = re.sub(pattern, replacement, env_content)
        
        # Write the updated content back to the .env file
        with open(".env", "w") as f:
            f.write(new_content)
        
        print(f"Successfully switched LLM provider to {provider}.")
        return True
    else:
        print("Error: LLM_PROVIDER setting not found in .env file.")
        return False

def show_current_provider():
    """Show the current LLM provider setting."""
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("LLM_PROVIDER="):
                    provider = line.strip().split("=")[1]
                    print(f"Current LLM provider: {provider}")
                    return
        print("LLM_PROVIDER setting not found in .env file.")
    else:
        print("Error: .env file not found.")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python switch_llm_provider.py [openai|google|show]")
        print("  openai: Switch to OpenAI provider")
        print("  google: Switch to Google AI provider")
        print("  show: Show current provider setting")
        return
    
    command = sys.argv[1].lower()
    
    if command == "show":
        show_current_provider()
    elif command in ["openai", "google"]:
        switch_provider(command)
    else:
        print(f"Error: Unknown command '{command}'.")
        print("Usage: python switch_llm_provider.py [openai|google|show]")

if __name__ == "__main__":
    main()
