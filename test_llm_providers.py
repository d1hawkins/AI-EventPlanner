"""
Test script to verify that both OpenAI and Google AI models can be used.
"""
import os
import pytest
import importlib.util
from dotenv import load_dotenv
from app.utils.llm_factory import get_llm

# Load environment variables
load_dotenv()

# Check if we're running in a CI environment (GitHub Actions)
CI_ENV = os.environ.get("CI", "false").lower() == "true"

# Check if langchain_google_genai is available
google_genai_available = importlib.util.find_spec("langchain_google_genai") is not None

# Check if we have valid API keys
VALID_OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "").startswith("sk-") and len(os.environ.get("OPENAI_API_KEY", "")) > 20
VALID_GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY", "") != "" and os.environ.get("GOOGLE_API_KEY", "") != "not-used-in-tests"

def test_openai_llm():
    """Test OpenAI LLM."""
    # Skip test if running in CI or if we don't have a valid API key
    if CI_ENV or not VALID_OPENAI_KEY:
        pytest.skip("Skipping OpenAI test in CI environment or with invalid API key")
    
    # Set environment variable to use OpenAI
    os.environ["LLM_PROVIDER"] = "openai"
    
    # Get the LLM
    llm = get_llm()
    
    # Test the LLM
    result = llm.invoke("What is the capital of France?")
    
    print("\n=== OpenAI LLM Test ===")
    print(f"Provider: {os.environ['LLM_PROVIDER']}")
    print(f"Model: {os.environ['LLM_MODEL']}")
    print(f"Response: {result.content}")
    print("=======================\n")

def test_google_llm():
    """Test Google AI LLM."""
    # Skip test if running in CI, if Google AI is not available, or if we don't have a valid API key
    if CI_ENV or not google_genai_available or not VALID_GOOGLE_KEY:
        pytest.skip("Skipping Google AI test in CI environment, when not available, or with invalid API key")
    
    # Set environment variable to use Google
    os.environ["LLM_PROVIDER"] = "google"
    
    # Get the LLM
    llm = get_llm()
    
    # Test the LLM
    result = llm.invoke("What is the capital of Germany?")
    
    print("\n=== Google AI LLM Test ===")
    print(f"Provider: {os.environ['LLM_PROVIDER']}")
    print(f"Model: {os.environ['GOOGLE_MODEL']}")
    print(f"Response: {result.content}")
    print("=========================\n")

if __name__ == "__main__":
    # Save original environment variables
    original_provider = os.environ.get("LLM_PROVIDER", "openai")
    
    try:
        # Run tests
        test_openai_llm()
        
        # Check if Google API key is set
        if os.environ.get("GOOGLE_API_KEY") and os.environ.get("GOOGLE_API_KEY") != "your_google_api_key_here":
            test_google_llm()
        else:
            print("\n=== Google AI LLM Test ===")
            print("Skipping Google AI test because GOOGLE_API_KEY is not set.")
            print("To test Google AI, set a valid GOOGLE_API_KEY in your .env file.")
            print("=========================\n")
    
    finally:
        # Restore original environment variables
        os.environ["LLM_PROVIDER"] = original_provider
