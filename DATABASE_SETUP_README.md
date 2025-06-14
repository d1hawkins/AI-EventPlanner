# Database Setup Instructions

This document provides instructions on how to manually create and seed the database for the AI Event Planner SaaS application.

## Prerequisites

- Access to the PostgreSQL database server
- PostgreSQL client (psql) installed
- Database connection details (server, username, password, database name)

## Running the SQL Script

1. Connect to your PostgreSQL database using psql:

```bash
psql -h YOUR_DB_SERVER -U YOUR_USERNAME -d YOUR_DB_NAME
```

For example:
```bash
psql -h ai-event-planner-db.postgres.database.azure.com -U dbadmin@ai-event-planner-db -d eventplanner
```

2. When prompted, enter your password.

3. Once connected, you can run the SQL script directly:

```sql
\i create_and_seed_database.sql
```

Alternatively, you can run the script from the command line without entering the psql shell:

```bash
psql -h YOUR_DB_SERVER -U YOUR_USERNAME -d YOUR_DB_NAME -f create_and_seed_database.sql
```

For example:
```bash
psql -h ai-event-planner-db.postgres.database.azure.com -U dbadmin@ai-event-planner-db -d eventplanner -f create_and_seed_database.sql
```

## Verifying the Setup

The script includes a verification step at the end that will show you the count of rows in each table. You should see output similar to this:

```
 table_name       | row_count 
------------------+-----------
 users            |         1
 organizations    |         1
 events           |         3
 conversations    |         1
 messages         |         4
 subscription_plans |         3
 subscriptions    |         1
 user_organizations |         1
```

If you see these counts, the database has been successfully created and seeded.

## Troubleshooting

If you encounter any issues:

1. Make sure your database connection details are correct.
2. Ensure you have the necessary permissions to create tables and insert data.
3. Check for any error messages in the output.
4. If you're using Azure PostgreSQL, make sure your IP address is allowed in the firewall rules.

## Default Login

After running the script, you can log in to the application with the following credentials:

- Email: admin@example.com
- Password: password

## Tables Created

The script creates the following tables:

1. `users` - User accounts
2. `organizations` - Organizations that users belong to
3. `events` - Events created by users
4. `conversations` - Conversations with agents
5. `messages` - Individual messages in conversations
6. `subscription_plans` - Available subscription plans
7. `subscriptions` - Organization subscriptions to plans
8. `user_organizations` - Relationship between users and organizations
