"""
Fix for SQLAlchemy model conflict between models.py and models_saas.py.

This script modifies the necessary imports to use models_updated.py instead
of models.py and models_saas.py to resolve the "Multiple classes found for path 'Conversation'"
error.
"""

import os
import re
import sys
from pathlib import Path

def fix_imports(file_path):
    """
    Fix imports in a file to use models_updated instead of models or models_saas.
    
    Args:
        file_path: Path to the file to fix
    
    Returns:
        bool: True if the file was modified, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if the file imports from models.py or models_saas.py
    models_import = re.search(r'from app\.db\.models import', content)
    models_saas_import = re.search(r'from app\.db\.models_saas import', content)
    
    if not (models_import or models_saas_import):
        # No relevant imports found
        return False
    
    # Replace imports
    modified_content = re.sub(
        r'from app\.db\.models import',
        'from app.db.models_updated import',
        content
    )
    modified_content = re.sub(
        r'from app\.db\.models_saas import',
        'from app.db.models_updated import',
        modified_content
    )
    
    # Check if content was modified
    if content == modified_content:
        return False
    
    # Write modified content back to file
    with open(file_path, 'w') as f:
        f.write(modified_content)
    
    print(f"Fixed imports in {file_path}")
    return True

def fix_all_imports():
    """
    Fix imports in all Python files in the app directory.
    """
    app_dir = Path('app')
    if not app_dir.exists():
        print("App directory not found")
        return
    
    # Find all Python files
    python_files = list(app_dir.glob('**/*.py'))
    
    # Add specific files that might be outside the app directory
    additional_files = [
        Path('run_saas_with_agents.py'),
        Path('run_saas.py'),
        Path('create_saas_db.py')
    ]
    
    for file_path in additional_files:
        if file_path.exists() and file_path not in python_files:
            python_files.append(file_path)
    
    # Fix imports in all files
    modified_count = 0
    for file_path in python_files:
        if fix_imports(file_path):
            modified_count += 1
    
    print(f"Fixed imports in {modified_count} files")

if __name__ == "__main__":
    print("Fixing SQLAlchemy model conflicts...")
    fix_all_imports()
    print("Done!")
