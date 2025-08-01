# Azure Tenant Conversation System Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the tenant-aware conversation system to Azure with PostgreSQL, including solutions for common deployment issues like database connection timeouts.

## 🚨 Common Issue: Database Connection Timeouts

**Error**: `connection to server at "ai-event-planner-db.postgres.database.azure.com" (52.224.66.120), port 5432 failed: Connection timed out`

### Root Causes
1. **Azure PostgreSQL Firewall Rules**: The database server may not allow connections from Azure App Service
2. **Network Security Groups**: Blocking database connections
3. **Connection Pool Exhaustion**: Too many concurrent connections
4. **Database Server Paused**: Azure Database for PostgreSQL may be paused

## 🔧 Solutions

### 1. Fix Azure PostgreSQL Firewall Rules

```bash
# Allow Azure services to access the database
az postgres server firewall-rule create \
  --resource-group your-resource-group \
  --server ai-event-planner-db \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Allow all IP addresses (for testing only)
az postgres server firewall-rule create \
  --resource-group your-resource-group \
  --server ai-event-planner-db \
  --name AllowAll \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 255.255.255.255
```

### 2. Update Database Connection Settings

Add these environment variables to your Azure App Service:

```bash
# Connection timeout settings
DATABASE_CONNECT_TIMEOUT=30
DATABASE_COMMAND_TIMEOUT=60
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_RECYCLE=3600

# Retry settings
DATABASE_RETRY_ATTEMPTS=3
DATABASE_RETRY_DELAY=1.0
```

### 3. Use the Resilient Service

Update your agent API router to use the fallback service:

```python
# In app/agents/api_router.py
from app.services.tenant_conversation_service_with_fallback import tenant_conversation_service

# Replace calls to the regular service with the fallback service
conversation = tenant_conversation_service.get_or_create_conversation(
    db=db,
    organization_id=organization_id,
    user_id=current_user_id,
    event_id=event_id,
    conversation_type="event_planning"
)
```

### 4. Database Migration with Retry Logic

Create a migration script that handles connection issues:

```python
# migrate_with_retry.py
import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app.config import DATABASE_URL
from app.db.models_tenant_conversations import Base

def migrate_with_retry(max_retries=5, delay=10):
    """Run migrations with retry logic for Azure deployment."""
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(engine)
            print("✅ Migration completed successfully")
            return True
            
        except OperationalError as e:
            if "connection" in str(e).lower() and attempt < max_retries - 1:
                print(f"⚠️ Connection failed (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                continue
            else:
                print(f"❌ Migration failed: {e}")
                return False
    
    return False

if __name__ == "__main__":
    migrate_with_retry()
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Verify Azure PostgreSQL server is running
- [ ] Check firewall rules allow App Service connections
- [ ] Confirm connection string is correct
- [ ] Test database connectivity from local environment

### Database Setup
- [ ] Run migrations: `python migrate_with_retry.py`
- [ ] Verify tables created: `python create_tenant_conversation_tables.py`
- [ ] Seed initial data if needed

### App Service Configuration
- [ ] Set all required environment variables
- [ ] Configure connection timeout settings
- [ ] Enable logging for debugging
- [ ] Set up health check endpoints

### Post-Deployment
- [ ] Test user registration (creates organization)
- [ ] Test agent conversation (creates tenant conversation)
- [ ] Monitor logs for connection issues
- [ ] Verify fallback mechanisms work

## 🔍 Troubleshooting

### Check Database Connectivity

```python
# test_db_connection.py
import os
import psycopg2
from app.config import DATABASE_URL

def test_connection():
    try:
        # Parse connection string
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected to PostgreSQL: {version[0]}")
        
        # Test tenant tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'tenant_%'
        """)
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tenant tables: {[t[0] for t in tables]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
```

### Monitor Connection Pool

```python
# monitor_connections.py
from sqlalchemy import create_engine, text
from app.config import DATABASE_URL

def monitor_connections():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check active connections
        result = conn.execute(text("""
            SELECT count(*) as active_connections
            FROM pg_stat_activity
            WHERE state = 'active'
        """))
        active = result.fetchone()[0]
        
        # Check max connections
        result = conn.execute(text("SHOW max_connections"))
        max_conn = result.fetchone()[0]
        
        print(f"Active connections: {active}/{max_conn}")
        
        if active > int(max_conn) * 0.8:
            print("⚠️ High connection usage detected")

if __name__ == "__main__":
    monitor_connections()
```

## 🚀 Deployment Commands

### Quick Deploy with Resilience

```bash
# Deploy with fallback service enabled
az webapp deployment source config-zip \
  --resource-group your-resource-group \
  --name your-app-name \
  --src deployment.zip

# Set environment variables for resilience
az webapp config appsettings set \
  --resource-group your-resource-group \
  --name your-app-name \
  --settings \
    USE_FALLBACK_SERVICE=true \
    DATABASE_RETRY_ATTEMPTS=3 \
    DATABASE_CONNECT_TIMEOUT=30 \
    ENABLE_CONNECTION_POOLING=true
```

### Health Check Endpoint

Add this to your app for monitoring:

```python
# In your main app file
@app.get("/health/database")
async def health_check_database():
    """Health check endpoint for database connectivity."""
    try:
        # Test database connection
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

## 📊 Monitoring and Alerts

### Set up Azure Monitor alerts for:
- Database connection failures
- High connection pool usage
- Application errors related to database
- Response time degradation

### Log Analysis Queries

```kusto
// Database connection errors
traces
| where message contains "connection" and message contains "failed"
| summarize count() by bin(timestamp, 5m)

// Fallback service usage
traces
| where message contains "fallback" or message contains "cache"
| summarize count() by bin(timestamp, 5m)
```

## 🎯 Success Metrics

After deployment, verify these metrics:
- [ ] Database connection success rate > 95%
- [ ] Average response time < 2 seconds
- [ ] Zero data loss during connection issues
- [ ] Fallback mechanisms activate when needed
- [ ] User experience remains smooth during database issues

## 📞 Support

If you continue experiencing issues:
1. Check Azure PostgreSQL server status
2. Review firewall and network security group rules
3. Monitor connection pool usage
4. Enable detailed logging
5. Consider upgrading database tier for better performance

The tenant conversation system is designed to be resilient and will continue functioning even during temporary database connectivity issues through the fallback mechanisms.
