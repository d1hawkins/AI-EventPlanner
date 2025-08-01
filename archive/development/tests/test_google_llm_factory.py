#!/usr/bin/env python3
"""
Test script to test the Google LLM factory specifically
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing Google LLM Factory...")

# Set up environment for Google provider
os.environ['LLM_PROVIDER'] = 'google'
os.environ['GOOGLE_MODEL'] = 'gemini-pro'

# Check if Google API key is set
google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    print("❌ GOOGLE_API_KEY is not set in environment variables")
    print("Please set your Google API key to test the Google LLM provider")
    exit(1)
else:
    print(f"✓ GOOGLE_API_KEY is set (length: {len(google_api_key)})")

try:
    print("1. Testing LLM factory import...")
    from app.utils.llm_factory import get_llm
    print("   ✓ LLM factory imported successfully")
    
    print("2. Testing Google LLM creation...")
    llm = get_llm(temperature=0.2)
    print(f"   ✓ Google LLM created successfully: {type(llm)}")
    
    print("3. Testing simple LLM call...")
    response = llm.invoke("Hello, this is a test. Please respond with 'Test successful'.")
    print(f"   ✓ LLM call successful: {response.content}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nDone testing Google LLM factory.")
