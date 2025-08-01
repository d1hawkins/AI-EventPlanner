# Azure Startup Issue Solution - Final Fix

## Problem Analysis

The Azure deployment was failing with the error:
```
python: can't open file '/home/site/wwwroot/startup.py': [Errno 2] No such file or directory
```

## Root Cause

The issue was caused by inconsistent startup file configurations:

1. **Azure Oryx** was trying to run `startup.py` (detected automatically)
2. **web.config** was configured to run `startup_app.py` 
3. **Procfile** was configured to run `startup_working.py` (which didn't exist)
4. The original `startup.py` was trying to import a `main()` function from `run_saas_with_agents.py` that didn't exist

## Solution Implemented

### 1. Fixed startup.py
- Updated `startup.py` to be a complete, self-contained startup script
- Added proper `main()` function that Azure Oryx can call
- Integrated all necessary startup logic:
  - Dependency installation
  - Database setup
  - Application startup with proper environment configuration
- Added fallback mechanisms for robust error handling

### 2. Updated Procfile
- Changed from `web: python startup_working.py` to `web: python startup.py`
- Now consistent with what Azure Oryx expects

### 3. Fixed Supporting Scripts
- Updated `create_tables.py` to include a `main()` function
- Updated `create_subscription_plans.py` to include a `main()` function
- These functions are called by `startup.py` during database setup

## Key Features of the Fix

### Robust Startup Process
```python
def main():
    """Main function for Azure startup"""
    try:
        install_dependencies()
        setup_database()
        start_application()
    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)
```

### Environment Configuration
- Automatically detects Azure environment variables (PORT, etc.)
- Loads `.env.saas` configuration
- Sets appropriate defaults for production deployment
- Configures LLM provider and other settings

### Database Setup
- Creates database tables if they don't exist
- Sets up subscription plans
- Handles errors gracefully and continues if setup fails

### Application Startup
- Uses uvicorn to run the FastAPI application
- Configures for production (reload=False)
- Includes fallback to simpler app if main app fails

## Files Modified

1. **startup.py** - Complete rewrite with proper main() function
2. **Procfile** - Updated to point to startup.py
3. **create_tables.py** - Added main() function
4. **create_subscription_plans.py** - Added main() function

## Expected Result

With these changes, Azure should be able to:
1. Find and execute `startup.py`
2. Install dependencies automatically
3. Set up the database
4. Start the SaaS application successfully

The startup script is now consistent across all configuration files and provides a robust, production-ready startup process for the Azure deployment.

## Testing

To test locally, you can run:
```bash
python startup.py
```

This will simulate the Azure startup process and help identify any remaining issues before deployment.
