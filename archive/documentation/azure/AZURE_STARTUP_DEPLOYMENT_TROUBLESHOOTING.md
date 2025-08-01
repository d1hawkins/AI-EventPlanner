# Azure Startup Deployment Troubleshooting Guide

## Current Status
✅ All required files are present locally
✅ startup.py contains proper main() function
✅ web.config points to startup.py
✅ Procfile points to startup.py

## Problem
Despite having all files locally, Azure is still reporting:
```
python: can't open file '/home/site/wwwroot/startup.py': [Errno 2] No such file or directory
```

## Root Cause Analysis
The issue is that `startup.py` is not being deployed to Azure, even though it exists locally. This can happen due to:

1. **Git deployment issues** - File not committed or pushed
2. **Build process exclusions** - File being filtered out during deployment
3. **Azure deployment configuration** - Incorrect deployment source or settings

## Solutions to Try

### Solution 1: Verify Git Status
```bash
git status
git add startup.py
git commit -m "Add startup.py for Azure deployment"
git push origin main
```

### Solution 2: Force Include in Deployment
Create a `.deployment` file in the root directory to ensure proper deployment:

```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
WEBSITE_NODE_DEFAULT_VERSION=18.17.0
```

### Solution 3: Alternative Startup Configuration
Since Azure Oryx is looking for `startup.py`, ensure it's the primary startup method by updating the Azure App Service configuration:

**Azure Portal Settings:**
- Go to Configuration → General Settings
- Set "Startup Command" to: `python startup.py`

### Solution 4: Use requirements.txt for Dependencies
Ensure all dependencies are in requirements.txt so Azure can install them:

```txt
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
python-dotenv
alembic
passlib[bcrypt]
python-jose[cryptography]
python-multipart
email-validator
icalendar
```

### Solution 5: Create Backup Startup Methods
Since multiple startup files exist, ensure they all work:

1. **startup.py** (Primary - what Azure Oryx expects)
2. **startup_app.py** (Backup - what web.config uses)
3. **Procfile** (For Heroku-style deployment)

### Solution 6: Debug Deployment
Create a simple test file to verify deployment:

```python
# test_deployment.py
print("Deployment test successful!")
print("Files in current directory:")
import os
for file in os.listdir('.'):
    print(f"  {file}")
```

Then set this as startup command temporarily to see what files are actually deployed.

## Immediate Action Items

1. **Commit and push startup.py**:
   ```bash
   git add startup.py create_tables.py create_subscription_plans.py web.config Procfile
   git commit -m "Fix Azure startup configuration"
   git push origin main
   ```

2. **Verify Azure deployment source** in Azure Portal:
   - Go to Deployment Center
   - Ensure it's connected to the correct repository and branch
   - Trigger a manual deployment

3. **Check Azure logs** after deployment:
   - Go to Log Stream in Azure Portal
   - Look for deployment and startup logs

4. **Test locally** to ensure startup.py works:
   ```bash
   python startup.py
   ```

## Expected Resolution
After implementing these solutions, Azure should be able to:
1. Find and execute `startup.py`
2. Install dependencies automatically
3. Set up the database
4. Start the SaaS application successfully

## If Problem Persists
If the issue continues, the problem may be:
1. Azure deployment configuration
2. Repository branch mismatch
3. Build process filtering out the file
4. Azure App Service plan limitations

In that case, consider using the alternative startup files (startup_app.py) or switching to a Docker-based deployment.
