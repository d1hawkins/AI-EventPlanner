#!/usr/bin/env python3
"""
Script to run the AI Event Planner application.
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
host = os.getenv("HOST", "0.0.0.0")
port = int(os.getenv("PORT", "8000"))

if __name__ == "__main__":
    print(f"Starting AI Event Planner on http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
