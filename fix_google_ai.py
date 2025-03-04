#!/usr/bin/env python3
"""
Script to install the missing langchain_google_genai package.
"""

import subprocess
import sys

def install_package():
    """
    Install the missing langchain_google_genai package.
    """
    print("Installing langchain_google_genai package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "langchain_google_genai"])
    print("Successfully installed langchain_google_genai package.")

if __name__ == "__main__":
    install_package()
