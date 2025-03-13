import os
from typing import Optional, Literal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# LLM Provider
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # Default to OpenAI

# OpenAI API Key
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
if LLM_PROVIDER.lower() == "openai" and not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Google AI API Key
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
if LLM_PROVIDER.lower() == "google" and not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# JWT Authentication
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    SECRET_KEY = "development_secret_key"  # Default for development
    print("WARNING: Using default SECRET_KEY. This is insecure for production.")

ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Server
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))

# LLM Configuration
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")  # OpenAI model
GOOGLE_MODEL: str = os.getenv("GOOGLE_MODEL", "gemini-pro")  # Google AI model

# Search API Configuration
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
if not TAVILY_API_KEY:
    print("WARNING: TAVILY_API_KEY environment variable is not set. Internet search functionality will be disabled.")
