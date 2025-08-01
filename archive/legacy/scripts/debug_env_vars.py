import os

def check_env_vars():
    """Debug function to check environment variables"""
    tavily_key = os.getenv('TAVILY_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    print(f"TAVILY_API_KEY: {'SET' if tavily_key else 'NOT SET'}")
    print(f"GOOGLE_API_KEY: {'SET' if google_key else 'NOT SET'}")
    
    if tavily_key:
        print(f"TAVILY_API_KEY length: {len(tavily_key)}")
    if google_key:
        print(f"GOOGLE_API_KEY length: {len(google_key)}")
    
    # Check the logic that should determine real_agents_available
    real_agents_available = bool(tavily_key and google_key)
    print(f"real_agents_available should be: {real_agents_available}")
    
    return {
        "tavily_key_present": bool(tavily_key),
        "google_key_present": bool(google_key),
        "real_agents_available": real_agents_available
    }

if __name__ == "__main__":
    result = check_env_vars()
    print("Result:", result)
