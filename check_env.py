#!/usr/bin/env python3
"""
Script to check the environment variables loaded from .env file.
"""
import os
from dotenv import load_dotenv

# Force reload of environment variables from .env file
load_dotenv(override=True)

# Print the environment variables
print("LLM_PROVIDER:", os.getenv("LLM_PROVIDER"))
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY")[:10] + "..." if os.getenv("OPENAI_API_KEY") else None)
print("LLM_MODEL:", os.getenv("LLM_MODEL"))
print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY")[:10] + "..." if os.getenv("GOOGLE_API_KEY") else None)
print("GOOGLE_MODEL:", os.getenv("GOOGLE_MODEL"))
