# Azure Database Migration Guide

This guide explains how to run and verify database migrations on the Azure PostgreSQL database.

## Overview

The AI Event Planner application uses Alembic for database migrations. This ensures that the database schema is always in sync with the application code.

## Automatic Migration on Startup

The application automatically runs migrations when it starts on Azure App Service. The `startup.sh` script includes migration logic that:

1. Attempts to run the comprehensive migration script with retry logic
2. Falls back to the simple migration script if the comprehensive one fails
3. Continues with application startup even if migrations fail (with warnings)

## Manual Migration Execution

If you need to run migrations manually on Azure, you have several options:

### Option 1: Via Azure Portal (Recommended)

1. Go to the Azure Portal
2. Navigate to your App Service
3. Go to **Advanced Tools** (Kudu) → **Go**
4. Open **Debug Console** → **CMD** or **PowerShell**
5. Navigate to the application directory:
   ```bash
   cd /home/site/wwwroot
   ```
6. Run the comprehensive migration script:
   ```bash
   python scripts/run_azure_migration_comprehensive.py
   ```

### Option 2: Via Azure CLI

If you have Azure CLI installed locally:

```bash
# Login to Azure
az login

# Set your subscription (if needed)
az account set --subscription "your-subscription-name"

# Run migrations via SSH
az webapp ssh --name ai-event-planner --resource-group ai-event-planner-rg

# Once connected:
cd /home/site/wwwroot
python scripts/run_azure_migration_comprehensive.py
```

### Option 3: Trigger App Restart

Simply restarting the app will trigger migrations automatically:

```bash
az webapp restart --name ai-event-planner --resource-group ai-event-planner-rg
```

## Migration Scripts

### Comprehensive Migration Script

**File:** `scripts/run_azure_migration_comprehensive.py`

This script provides:
- Database connection verification
- Detailed error reporting
- Retry logic (up to 3 attempts by default)
- Migration status checking
- Post-migration verification

**Usage:**
```bash
# Basic usage
python scripts/run_azure_migration_comprehensive.py

# With custom retry settings
python scripts/run_azure_migration_comprehensive.py --max-retries 5 --retry-delay 10

# Skip connection verification
python scripts/run_azure_migration_comprehensive.py --skip-verification
```

### Database Verification Script

**File:** `scripts/verify_azure_db.py`

This script provides detailed information about the database state:
- Database connection info
- Migration status
- Table information
- Row counts
- Table structures (verbose mode)
- Foreign key constraints (verbose mode)

**Usage:**
```bash
# Basic verification
python scripts/verify_azure_db.py

# Verbose output with table structures
python scripts/verify_azure_db.py --verbose
```

## Migration Files

The application has the following migration files in `migrations/versions/`:

1. **20250320_initial_schema.py** - Base schema (users, conversations, messages, events, agent_states)
2. **20250322_saas_migration.py** - SaaS schema (organizations, subscriptions, plans)
3. **20250722_conversation_memory.py** - Conversation memory enhancements
4. **20250727_tenant_conversations.py** - Tenant-aware conversation system

These migrations are applied in order using Alembic's revision chain:
```
20250320_initial → 20250322_saas → 20250722_conversation_memory → 20250727_tenant_conversations
```

### Drop and Reload Script

**File:** `scripts/drop_and_reload_db.py`

This script provides a nuclear option to completely reset the database:
- Drops ALL tables in the database (including alembic_version)
- Runs all migrations from scratch
- Verifies the final database state

**⚠️ WARNING: This will DELETE ALL DATA in the database!**

**Usage via Azure Environment Variable:**

1. Go to Azure Portal → App Service → Configuration → Application Settings
2. Add new setting: `DROP_AND_RELOAD` = `true`
3. Save and restart the application
4. **IMPORTANT**: After the app starts successfully, immediately REMOVE the `DROP_AND_RELOAD` setting to prevent accidental re-runs

**Usage via Kudu Console:**

```bash
cd /home/site/wwwroot
python scripts/drop_and_reload_db.py
```

The script includes a 5-second countdown before execution to prevent accidental runs.

**When to use:**
- Database is in an inconsistent state
- Migration chain is broken
- Need to start completely fresh
- Tables exist but alembic_version is missing or corrupt

## Environment Variables

The migration scripts require the following environment variable:

- **DATABASE_URL**: PostgreSQL connection string

On Azure App Service, this should be set in the Application Settings.

**Format:**
```
postgresql://username:password@host:5432/database?sslmode=require
```

For the current Azure deployment:
```
postgresql://dbadmin@ai-event-planner-db:PASSWORD@ai-event-planner-db.postgres.database.azure.com:5432/eventplanner?sslmode=require
```

## Troubleshooting

### Migration Fails with "No module named 'alembic'"

The required dependencies may not be installed. The migration script will attempt to install them automatically, but you can also install manually:

```bash
pip install alembic psycopg2-binary sqlalchemy
```

### Connection Timeout or "Cannot connect to database"

1. Check that the DATABASE_URL environment variable is correctly set
2. Verify that the PostgreSQL server allows connections from Azure App Service
3. Check the Azure PostgreSQL firewall rules
4. Ensure SSL mode is set to 'require' in the connection string

### "alembic_version table does not exist"

This is normal for a fresh database. The migration script will create this table and run all migrations.

### Migration Fails with "relation already exists"

This can happen if tables were created manually or through a previous failed migration. Options:

1. **Drop and recreate tables** (WARNING: This will delete all data):
   ```bash
   # Connect to the database
   psql "$DATABASE_URL"

   # Drop all tables
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;

   # Run migrations
   python scripts/run_azure_migration_comprehensive.py
   ```

2. **Stamp the database with the current revision** (if tables are already correct):
   ```bash
   alembic stamp head
   ```

### Verify Migration Status

To check the current migration status:

```bash
# Using the verification script
python scripts/verify_azure_db.py --verbose

# Or using Alembic directly
alembic current
alembic history
```

## Monitoring Migrations

You can monitor migration execution through:

1. **Application Logs** (Azure Portal → App Service → Log Stream)
2. **Kudu Logs** (Advanced Tools → Debug Console → LogFiles)
3. **Azure Application Insights** (if configured)

## Best Practices

1. **Always backup the database before running migrations in production**
   ```bash
   pg_dump "$DATABASE_URL" > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Test migrations in a staging environment first**

3. **Monitor the application after migrations** to ensure everything works correctly

4. **Keep migration scripts in version control** (already done)

5. **Never edit migration files directly** - create new migrations instead:
   ```bash
   alembic revision --autogenerate -m "description of changes"
   ```

## Getting Help

If you encounter issues:

1. Check the application logs for detailed error messages
2. Run the verification script to diagnose database state
3. Review the Alembic documentation: https://alembic.sqlalchemy.org/
4. Check the Azure PostgreSQL documentation

## Migration History

- **2025-03-20**: Initial schema migration (base tables)
- **2025-03-22**: SaaS migration (organizations, subscriptions)
- **2025-07-22**: Conversation memory enhancements
- **2025-07-27**: Tenant-aware conversation system
- **2025-10-25**: PostgreSQL-only migration (removed SQLite support)
- **2025-10-27**: Fixed migration chain references and added drop/reload capability

---

**Last Updated:** October 27, 2025
