# 🔗 Your Azure PostgreSQL DATABASE_URL

Based on your Azure configuration found in `scripts/azure_db_info.py`, here is your **DATABASE_URL**:

```
postgres://dbadmin@ai-event-planner-db:VM*admin@ai-event-planner-db.postgres.database.azure.com:5432/eventplanner?sslmode=require
```

## 📋 Database Configuration Details

From your Azure setup:
- **Host:** `ai-event-planner-db.postgres.database.azure.com`
- **Port:** `5432`
- **Database:** `eventplanner`
- **Username:** `dbadmin@ai-event-planner-db` (Azure format)
- **Password:** `VM*admin`
- **SSL Mode:** `require`

## 🚨 IMMEDIATE ACTION: Add to GitHub Secrets

**Copy and paste this DATABASE_URL into your GitHub secrets:**

1. Go to: https://github.com/d1hawkins/AI-EventPlanner/settings/secrets/actions
2. Click **"New repository secret"**
3. **Name:** `DATABASE_URL`
4. **Value:** 
   ```
   postgres://dbadmin@ai-event-planner-db:VM*admin@ai-event-planner-db.postgres.database.azure.com:5432/eventplanner?sslmode=require
   ```

## ✅ Both Secrets Ready

Now you have both required secrets:

### 1. SECRET_KEY
```
or7miYlGqc1vm_7zqlZBMiShAsrDB4t3fBv1O5MYMRk
```

### 2. DATABASE_URL  
```
postgres://dbadmin@ai-event-planner-db:VM*admin@ai-event-planner-db.postgres.database.azure.com:5432/eventplanner?sslmode=require
```

## 🚀 Next Steps

1. **Add both secrets to GitHub** (links provided above)
2. **Go to GitHub Actions** and re-run your failed deployment
3. **Monitor the deployment** - it should now succeed!

Your deployment should work perfectly with these exact values from your Azure setup.
