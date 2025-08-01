"""
LLM Factory module for creating LLM instances based on configuration.
"""
from typing import Optional
import importlib.util
import os
import sys

from langchain_openai import ChatOpenAI

# Try to import config from different possible paths
try:
    from app import config
except ImportError:
    try:
        import config
    except ImportError:
        try:
            # Add the parent directory to sys.path to find config
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(os.path.dirname(current_dir))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            import config
        except ImportError:
            try:
                # Try importing from app.config directly
                from app.config import *
                # Create a mock config module
                class MockConfig:
                    pass
                config = MockConfig()
                config.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
                config.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
                config.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
                config.LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
                config.GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-pro")
            except ImportError:
                # Fallback: create config from environment variables
                class MockConfig:
                    pass
                config = MockConfig()
                config.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
                config.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
                config.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
                config.LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
                config.GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-pro")


def get_llm(temperature: float = 0.2):
    """
    Get the appropriate LLM based on configuration.
    
    Args:
        temperature: Temperature setting for the LLM (default: 0.2)
        
    Returns:
        Configured LLM instance
    """
    provider = config.LLM_PROVIDER.lower()
    
    if provider == "openai":
        return ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model=config.LLM_MODEL,
            temperature=temperature
        )
    elif provider == "google":
        # Dynamically import Google AI module only when needed
        if importlib.util.find_spec("langchain_google_genai") is None:
            raise ImportError(
                "langchain_google_genai is not installed. "
                "Install it with: pip install langchain-google-genai"
            )
        
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        return ChatGoogleGenerativeAI(
            api_key=config.GOOGLE_API_KEY,
            model=config.GOOGLE_MODEL,
            temperature=temperature
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
