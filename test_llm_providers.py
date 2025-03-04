"""
Test script to verify that both OpenAI and Google AI models can be used.
"""
import os
from dotenv import load_dotenv
from app.utils.llm_factory import get_llm

# Load environment variables
load_dotenv()

def test_openai_llm():
    """Test OpenAI LLM."""
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
