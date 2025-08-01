#!/usr/bin/env python3
"""
SaaS application runner with real conversational agents
"""
import os
import sys

def main():
    """Main entry point for SaaS application with agents"""
    print("Starting SaaS application with real conversational agents...")
    
    # Import and run the conversational adapter
    from app_adapter_conversational import app
    import uvicorn
    
    # Get port from environment (Azure sets this)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
