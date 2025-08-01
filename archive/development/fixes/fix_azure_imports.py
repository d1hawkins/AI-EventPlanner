#!/usr/bin/env python3
"""
Fix Azure import issues by ensuring all modules are properly accessible.
This script creates missing __init__.py files and fixes import paths.
"""
import os
import sys

def create_init_files():
    """Create __init__.py files in all necessary directories."""
    directories = [
        'app',
        'app/services',
        'app/middleware', 
        'app/state',
        'app/auth',
        'app/subscription',
        'app/tools',
        'app/graphs',
        'app/schemas',
        'app/db',
        'app/utils',
        'app/agents',
        'app/web'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            init_file = os.path.join(directory, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write(f'# Package initialization file for {directory}\n')
                print(f"Created {init_file}")
            else:
                print(f"✅ {init_file} already exists")
        else:
            print(f"⚠️ Directory {directory} does not exist")

def fix_conversation_memory_import():
    """Ensure conversation_memory module is accessible."""
    conversation_memory_path = 'app/utils/conversation_memory.py'
    if os.path.exists(conversation_memory_path):
        print(f"✅ {conversation_memory_path} exists")
        
        # Check if it has the required classes
        with open(conversation_memory_path, 'r') as f:
            content = f.read()
            if 'class ConversationMemory' in content:
                print("✅ ConversationMemory class found")
            else:
                print("⚠️ ConversationMemory class not found")
    else:
        print(f"❌ {conversation_memory_path} does not exist")

if __name__ == "__main__":
    print("🔧 Fixing Azure import issues...")
    create_init_files()
    fix_conversation_memory_import()
    print("✅ Import fixes completed")
