"""
LLM Factory module for creating LLM instances based on configuration.
"""
from typing import Optional
import importlib.util

from langchain_openai import ChatOpenAI

from app import config


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
