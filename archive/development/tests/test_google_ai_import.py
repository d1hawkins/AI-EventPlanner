#!/usr/bin/env python3
"""
Test script to diagnose Google AI import issues
"""

print("Testing Google AI imports...")

try:
    print("1. Testing google.generativeai import...")
    import google.generativeai as genai
    print("   ✓ google.generativeai imported successfully")
except Exception as e:
    print(f"   ✗ Error importing google.generativeai: {e}")

try:
    print("2. Testing langchain_google_genai import...")
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("   ✓ langchain_google_genai imported successfully")
except Exception as e:
    print(f"   ✗ Error importing langchain_google_genai: {e}")

try:
    print("3. Testing google.ai.generativelanguage_v1beta.types import...")
    from google.ai.generativelanguage_v1beta.types import FileData
    print("   ✓ FileData imported successfully")
except Exception as e:
    print(f"   ✗ Error importing FileData: {e}")

try:
    print("4. Testing alternative FileData import...")
    from google.ai.generativelanguage import FileData
    print("   ✓ FileData imported from alternative location")
except Exception as e:
    print(f"   ✗ Error importing FileData from alternative location: {e}")

try:
    print("5. Testing google.ai.generativelanguage import...")
    import google.ai.generativelanguage as genai_lang
    print("   ✓ google.ai.generativelanguage imported successfully")
    print(f"   Available attributes: {[attr for attr in dir(genai_lang) if not attr.startswith('_')]}")
except Exception as e:
    print(f"   ✗ Error importing google.ai.generativelanguage: {e}")

try:
    print("6. Testing our LLM factory...")
    from app.utils.llm_factory import get_llm
    print("   ✓ LLM factory imported successfully")
except Exception as e:
    print(f"   ✗ Error importing LLM factory: {e}")

print("\nDone testing imports.")
