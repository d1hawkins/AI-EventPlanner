import os
import sys
import uvicorn
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env.saas.local file
load_dotenv(".env.saas.local", override=True)

# Set OpenAI as the LLM provider
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "gpt-4"

# Import the application
from app.main_saas import app

if __name__ == "__main__":
    print("Starting SaaS application with agents...")
    print(f"Using LLM provider: {os.environ.get('LLM_PROVIDER', 'openai')}")
    print(f"Using LLM model: {os.environ.get('LLM_MODEL', 'gpt-4')}")
    
    # Run the application
    uvicorn.run(
        "app.main_saas:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8002)),
        reload=True
    )
