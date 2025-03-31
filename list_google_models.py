#!/usr/bin/env python3
"""
Script to list available Google AI models.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv(override=True)

# Set up the API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

genai.configure(api_key=api_key)

# List available models
print("Available Google AI models:")
for model in genai.list_models():
    print(f"- {model.name}")
    print(f"  Supported generation methods: {model.supported_generation_methods}")
    print()
