# Azure Database Migration and Seeding Guide

This guide provides instructions for setting up and seeding the Azure PostgreSQL database for the AI Event Planner SaaS application.

## Overview

The AI Event Planner application uses an Azure PostgreSQL database to store event data, user information, and SaaS-related data such as organizations and subscription plans. This guide explains how to:

1. Create the database tables
2. Seed the database with initial data
3. Verify the database setup

## Prerequisites

- Azure PostgreSQL server is set up and running
- Database connection details are available
- Python 3.8+ is installed
- Required Python packages: `psycopg2-binary`

## Database Connection Details

The database connection details are:

- Host: `ai-event-planner-db.postgres.database.azure.com`
- Port: `5432`
- Database: `eventplanner`
- Username: `dbadmin@ai-event-planner-db`
- Password: `VM*admin`
- SSL Mode: `require`

## Setup Process

### Option 1: Complete Setup (Recommended)

For a complete setup of the database, you can use the `setup_azure_db_complete.py` script:

```bash
python scripts/setup_azure_db_complete.py --force
```

This script will:

1. Create all tables using direct SQL
2. Seed the database with SaaS data (users, organizations, subscription plans)
3. Seed the database with event data (conversations, messages, events, tasks, stakeholders)
4. Verify the database setup

The `--force` flag is optional and will force the seeding even if data already exists in the database.

### Option 2: Step-by-Step Setup

If you prefer to run the setup process step by step, you can follow these instructions:

#### 1. Create Database Tables

The database tables can be created using direct SQL statements. To create the tables:

```bash
python scripts/create_azure_tables_direct.py --force
```

This script will create all the necessary tables for the application, including:

- `users`: Stores user information
- `conversations`: Stores conversation data
- `messages`: Stores message data
- `events`: Stores event data
- `tasks`: Stores task data
- `stakeholders`: Stores stakeholder data
- `organizations`: Stores organization data
- `subscription_plans`: Stores subscription plan data
- `organization_users`: Stores the relationship between organizations and users
- `subscription_invoices`: Stores subscription invoice data
- `event_templates`: Stores event template data
- `template_items`: Stores template item data

#### 2. Seed the Database

The database seeding is done in two steps:

##### 2.1. Seed SaaS Data

First, seed the SaaS-related data (users, organizations, subscription plans):

```bash
python scripts/seed_azure_db_direct.py --force
```

This script will:

- Create sample users (admin and testuser)
- Create sample subscription plans (Basic and Premium)
- Create sample organizations (Acme Inc. and XYZ Corp)
- Create organization users (admin in Acme Inc. and testuser in XYZ Corp)

##### 2.2. Seed Event Data

Next, seed the event-related data:

```bash
python scripts/seed_azure_db_events.py --force
```

This script will:

- Create sample conversations
- Create sample messages
- Create sample events
- Create sample tasks
- Create sample stakeholders
- Update events with organization IDs

#### 3. Verify the Database Setup

To verify that the database has been set up correctly:

```bash
python scripts/check_azure_db_schema_and_data.py
```

This script will:

- Check the database connection
- List all tables in the database
- Show sample data from each table
- Verify the relationships between tables

## Troubleshooting

### Common Issues

1. **Connection Issues**: If you encounter connection issues, check that:
   - The Azure PostgreSQL server is running
   - The firewall rules allow connections from your IP address
   - The connection details are correct

2. **Migration Issues**: If migrations fail, try:
   - Running the migrations with the `--verbose` flag for more information
   - Checking the Alembic version table to see which migrations have been applied
   - Running the migrations one by one

3. **Seeding Issues**: If seeding fails, try:
   - Running the seeding scripts with the `--verbose` flag for more information
   - Checking the database tables to see what data has been inserted
   - Running the seeding scripts one by one

## Scripts Reference

### Complete Setup Script

- `scripts/setup_azure_db_complete.py`: Runs the complete database setup process (migrations, seeding, verification)

### Database Migration Scripts

- `scripts/create_azure_tables_direct.py`: Creates tables directly using SQL (recommended)
- `scripts/run_azure_migrations.py`: Runs Alembic migrations (may have issues with Python path)
- `scripts/run_azure_migrations_fixed.py`: Fixed version of the migration script (may have issues with Python path)
- `scripts/create_azure_tables.py`: Creates tables directly using SQL (older version)
- `scripts/create_azure_tables_fixed.py`: Fixed version of the table creation script (older version)

### Database Seeding Scripts

- `scripts/seed_azure_db_direct.py`: Seeds SaaS data (users, organizations, subscription plans)
- `scripts/seed_azure_db_events.py`: Seeds event data (conversations, messages, events, tasks, stakeholders)
- `scripts/seed_azure_db_saas.py`: Alternative script for seeding SaaS data
- `scripts/seed_azure_db_basic.py`: Seeds basic data (users, conversations, messages)

### Database Verification Scripts

- `scripts/check_azure_db_schema_and_data.py`: Checks the database schema and data
- `scripts/test_postgres_connection.py`: Tests the connection to the PostgreSQL database
- `scripts/azure_db_info.py`: Shows information about the Azure PostgreSQL database

## Additional Resources

- [Azure PostgreSQL Documentation](https://docs.microsoft.com/en-us/azure/postgresql/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
