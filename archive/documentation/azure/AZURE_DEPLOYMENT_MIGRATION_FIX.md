# Azure Deployment Migration Fix

## Issue

When deploying the AI Event Planner SaaS application to Azure, the following error occurred during database migrations:

```
unrecognized arguments: --command cd /home/site/wwwroot && alembic upgrade head
```

This error occurred because the `az webapp ssh --command` approach used in the deployment scripts was not properly handling the command arguments.

## Solution

The solution involved two main changes:

1. Using the Kudu REST API instead of `az webapp ssh --command` to run commands on the Azure App Service
2. Using the `scripts/migrate.py` module instead of calling `alembic upgrade head` directly

### Files Updated

The following files were updated:

1. `deploy-simple.sh`
2. `run-migrations.sh`
3. `verify-deployment.sh`
4. `azure-deploy-saas.sh`
5. `deploy-app-to-azure.sh`
6. `.github/workflows/azure-deploy-saas.yml`

### Changes Made

#### 1. Using the Kudu REST API

Instead of using `az webapp ssh --command`, we now use the Kudu REST API to run commands on the Azure App Service. This approach is more reliable and provides better error handling.

Example:

```bash
# Get publishing credentials
USERNAME=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $APP_NAME --query publishingUserName -o tsv)
PASSWORD=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $APP_NAME --query publishingPassword -o tsv)

# Use the Kudu REST API to run a command
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  https://$APP_NAME.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"$PYTHON_PATH -m scripts.migrate\", \"dir\":\"/home/site/wwwroot\"}")
```

#### 2. Using the `scripts/migrate.py` module

Instead of calling `alembic upgrade head` directly, we now use the `scripts/migrate.py` module, which provides a more robust way to run database migrations.

Example:

```bash
# Run database migrations using the migrate.py script
python -m scripts.migrate
```

#### 3. Handling the case where `jq` is not installed

We also added a check to handle the case where the `jq` command-line tool is not installed, which was causing an error in the deployment scripts.

Example:

```bash
# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq is not installed. Using alternative approach.${NC}"
    
    # Get publishing credentials using direct Azure CLI queries
    USERNAME=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $APP_NAME --query publishingUserName -o tsv)
    PASSWORD=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $APP_NAME --query publishingPassword -o tsv)
else
    # Get publishing credentials using jq
    CREDS=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $APP_NAME --query "{username:publishingUserName, password:publishingPassword}" -o json)
    USERNAME=$(echo $CREDS | jq -r '.username')
    PASSWORD=$(echo $CREDS | jq -r '.password')
fi
```

#### 4. Including the `scripts` directory in deployment packages

We updated the deployment scripts to include the `scripts` directory in the deployment packages, since we're now using the `scripts/migrate.py` module for migrations.

Example:

```bash
# Copy application files to the deployment directory
cp -r app deploy/
cp -r migrations deploy/
cp -r scripts deploy/
cp alembic.ini deploy/
cp requirements.txt deploy/
```

## Testing

The changes were tested locally by running the `deploy-simple.sh` script. The script now handles the case where `jq` is not installed and uses the Kudu REST API to run the migration script.

## Conclusion

These changes should fix the issue with database migrations during deployment to Azure. The approach is more robust and provides better error handling.
