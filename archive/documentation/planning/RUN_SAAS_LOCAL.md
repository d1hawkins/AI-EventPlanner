# Running the AI Event Planner SaaS Version Locally

This guide explains how to run the AI Event Planner SaaS version locally for development and testing purposes.

## Prerequisites

- Python 3.9 or higher
- PostgreSQL database (configured in `.env.saas`)
- Required Python packages (install with `pip install -r requirements.txt`)

## Available Scripts

There are several scripts available to run the SaaS version locally:

### 1. Standard SaaS Application (with migrations)

```bash
python run_saas.py
```

This script:
- Loads environment variables from `.env.saas`
- Runs database migrations
- Starts the FastAPI server on port 8000
- Opens a browser window to the application

### 2. SaaS Application (without migrations)

```bash
python run_saas_no_migrations.py
```

This script:
- Loads environment variables from `.env.saas`
- Skips database migrations
- Starts the FastAPI server on port 8000
- Opens a browser window to the application

### 3. SaaS Application with Agent Integration

```bash
python run_saas_with_agents_alt.py
```

This script:
- Loads environment variables from `.env.saas`
- Starts the FastAPI server with agent integration on port 8003
- Does not automatically open a browser window

### 4. Static Files Server

```bash
python serve_saas_static_alt.py
```

This script:
- Starts a simple HTTP server on port 8001
- Serves only the static files from `app/web/static/saas`
- Useful for frontend development without backend functionality

## Running Multiple Servers Simultaneously

You can run multiple servers simultaneously to test different aspects of the application:

1. Run the main application without migrations:
   ```bash
   python run_saas_no_migrations.py
   ```

2. In another terminal, run the static files server:
   ```bash
   python serve_saas_static_alt.py
   ```

3. In a third terminal, run the application with agent integration:
   ```bash
   python run_saas_with_agents_alt.py
   ```

## Accessing the Application

- Main application: http://localhost:8000/static/saas/index.html
- Static files server: http://localhost:8001/saas/
- Agent integration: http://localhost:8003/static/saas/index.html

## Environment Variables

The application uses environment variables from `.env.saas`. Make sure this file exists and contains the necessary configuration.

## Troubleshooting

### Port Already in Use

If you encounter an error like "Address already in use", it means another process is already using the port. You can either:

1. Stop the other process
2. Modify the script to use a different port
3. Use one of the alternative scripts that use different ports

### Database Connection Issues

If you encounter database connection issues, check:

1. The `DATABASE_URL` in your `.env.saas` file
2. That your PostgreSQL server is running
3. That the database exists and is accessible with the provided credentials

### Missing Module Errors

If you encounter "No module named" errors, make sure you have installed all required packages:

```bash
pip install -r requirements.txt
```
