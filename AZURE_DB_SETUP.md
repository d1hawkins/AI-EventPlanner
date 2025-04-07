# Azure PostgreSQL Database Setup

This document provides instructions for setting up and seeding the Azure PostgreSQL database for the AI Event Planner SaaS application.

## Overview

The database setup process involves two main steps:

1. **Running Migrations**: Create or update the database schema
2. **Seeding the Database**: Populate the database with initial data required for the application to function

## Prerequisites

- Python 3.8 or higher
- Access to the Azure PostgreSQL database
- `.env.azure` file with the correct database connection string
- Required Python packages (install with `pip install -r db_requirements.txt`)

## Setup Scripts

Three scripts are provided to help with the database setup:

1. `seed_azure_db.py`: Seeds the database with initial data
2. `setup_azure_db.py`: Runs migrations and then seeds the database
3. `check_azure_db_schema.py`: Checks the database schema to verify tables and columns

### Installation

Install the required Python packages:

```bash
pip install -r db_requirements.txt
```

## Configuration

The database connection is configured through the `.env.azure` file, which should contain:

```
DATABASE_URL=postgresql://dbadmin:VM%2Aadmin@ai-event-planner-db.postgres.database.azure.com:5432/eventplanner
```

## Initial Data

The seeding process will create:

1. **Subscription Plans**:
   - Free tier
   - Professional tier
   - Enterprise tier

2. **Admin User**:
   - Default: admin@example.com / admin / password123
   - Can be customized via command-line arguments

3. **Default Organization** (optional):
   - Default: "Default Organization" with slug "default"
   - Can be customized via command-line arguments

## Usage

### Complete Setup (Migrations + Seeding)

To run both migrations and seeding in one step:

```bash
python setup_azure_db.py
```

### Custom Admin User

To specify a custom admin user:

```bash
python setup_azure_db.py --admin-email your.email@example.com --admin-username yourusername --admin-password yourpassword
```

### Custom Organization

To specify a custom default organization:

```bash
python setup_azure_db.py --org-name "Your Organization" --org-slug your-org
```

### Skip Organization Creation

If you don't want to create a default organization:

```bash
python setup_azure_db.py --skip-org
```

### Run Only Migrations

To run only the migrations without seeding:

```bash
python setup_azure_db.py --skip-seed
```

### Run Only Seeding

To run only the seeding without migrations:

```bash
python setup_azure_db.py --skip-migrations
```

## Troubleshooting

### Checking Database Schema

You can use the `check_azure_db_schema.py` script to verify that the database schema is correct:

```bash
python check_azure_db_schema.py
```

For more detailed output, use the `--verbose` flag:

```bash
python check_azure_db_schema.py --verbose
```

This script will:
- Connect to the database
- Check if all expected tables exist
- Verify that tables have the expected columns
- Report the number of rows in each table

### Database Connection Issues

If you encounter database connection issues:

1. Verify the `DATABASE_URL` in `.env.azure` is correct
2. Ensure the database server is accessible from your network
3. Check that the database user has the necessary permissions
4. Run `python check_azure_db_schema.py` to diagnose connection issues

### Migration Errors

If migrations fail:

1. Check the error message for specific issues
2. Ensure the database user has permission to create and modify tables
3. Try running migrations manually: `python scripts/run_azure_migrations.py`

### Seeding Errors

If seeding fails:

1. Check if the tables exist in the database
2. Ensure the migrations have been run successfully
3. Try running seeding manually: `python seed_azure_db.py`

## Security Considerations

- The default admin password is for development only. Always use a strong password in production.
- Consider using Azure Key Vault or another secure method to store sensitive credentials.
- Update the admin user's password after the initial setup.

## Next Steps

After setting up the database:

1. Verify the setup by logging in with the admin user
2. Create additional organizations and users as needed
3. Configure subscription plans in the application
