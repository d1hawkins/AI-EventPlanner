# AI Event Planner

An AI-powered event planning system built with LangGraph, LangChain, and FastAPI.

## Overview

This system implements a hierarchical agent structure for event planning, with a Frontend Coordinator Agent that interfaces with users and orchestrates specialized agents for different aspects of event planning.

## Features

- Frontend Coordinator Agent as a LangGraph Supervisor agent
- Comprehensive information collection and proposal generation
- Task delegation to specialized agents
- Persistent state management
- User authentication
- Chat interface for testing
- Support for various event types

## Project Structure

```
ai-event-planner/
├── app/
│   ├── agents/       # Agent implementations
│   ├── auth/         # Authentication system
│   ├── db/           # Database models and session management
│   ├── graphs/       # LangGraph definitions
│   ├── models/       # Data models
│   ├── schemas/      # Pydantic schemas
│   ├── state/        # State management
│   ├── tools/        # Agent tools
│   ├── utils/        # Helper utilities
│   └── web/          # Web interface
├── tests/            # Test suite
├── .github/
│   └── workflows/    # GitHub Actions workflows for CI/CD
├── migrations/       # Database migration scripts
├── scripts/          # Utility scripts
├── Dockerfile        # Container definition
├── azure-deploy.sh   # Azure deployment script
├── pyproject.toml    # Project dependencies
└── README.md         # This file
```

## Setup

1. Install dependencies:

```bash
pip install poetry

# For OpenAI only (default)
poetry install --without google

# For both OpenAI and Google AI
poetry install
```

2. Create a `.env` file with your configuration:

```
# LLM Provider (options: "openai" or "google")
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4

# Google AI Configuration (if using Google AI)
# GOOGLE_API_KEY=your_google_api_key
# GOOGLE_MODEL=gemini-pro

# JWT Authentication
SECRET_KEY=your_secret_key_for_jwt

# Database
DATABASE_URL=sqlite:///./app.db
```

For detailed information about LLM configuration and dependency management, see [LLM_CONFIGURATION.md](LLM_CONFIGURATION.md).

3. Run the application:

```bash
poetry run uvicorn app.main:app --reload
```

4. Access the chat interface at http://localhost:8000

## Development

- Run tests: `poetry run pytest`
- Format code: `poetry run black .`

## Azure Deployment

This project is configured for deployment to Azure using GitHub Actions for CI/CD. The deployment uses:

- **Azure App Service** with Web App for Containers
- **Azure Database for PostgreSQL** for production database
- **Azure Container Registry** for Docker images
- **Azure Key Vault** for secure storage of secrets

### Deployment Steps

1. Set up Azure resources:

```bash
./azure-deploy.sh
```

This script creates all necessary Azure resources including resource group, app service plan, web app, PostgreSQL database, and key vault.

2. Configure GitHub repository secrets:

- `AZURE_CREDENTIALS`: Azure service principal credentials (JSON content from AZURE_CREDENTIALS.json)
- `ACR_LOGIN_SERVER`: Azure Container Registry login server
- `ACR_USERNAME`: Azure Container Registry username
- `ACR_PASSWORD`: Azure Container Registry password
- `AZURE_RESOURCE_GROUP`: Azure resource group name
- `OPENAI_API_KEY`: Your OpenAI API key
- `SENDGRID_API_KEY`: Your SendGrid API key
- `GOOGLE_API_KEY`: Your Google API key
- `STRIPE_API_KEY`: Your Stripe API key
- `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret

3. Push changes to the main branch to trigger the CI/CD pipeline.

The GitHub Actions workflow will:
- Build and test the application
- Build and push the Docker image to Azure Container Registry
- Deploy the image to Azure App Service
- Run database migrations

### Database Migrations

Database migrations are managed with Alembic. To create a new migration:

```bash
# Generate a migration script
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

In production, migrations are automatically applied during deployment.

## Secrets Management

This project uses environment variables for sensitive information. To set up:

1. Copy template files to create your configuration:
   ```bash
   cp AZURE_CREDENTIALS.template.json AZURE_CREDENTIALS.json
   cp .env.saas.template .env.saas
   cp .env.backup.template .env.backup
   ```

2. Edit these files to add your actual credentials

3. For GitHub Actions deployment, add these secrets to your repository:
   - `AZURE_CREDENTIALS`: The entire JSON content from your AZURE_CREDENTIALS.json file
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SENDGRID_API_KEY`: Your SendGrid API key
   - `GOOGLE_API_KEY`: Your Google API key
   - `STRIPE_API_KEY`: Your Stripe API key
   - `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret

These files are in .gitignore to prevent accidental commits of sensitive information.

## Enhanced Coordinator Agent

The Frontend Coordinator Agent has been enhanced to provide a more structured approach to event planning:

### Information Collection

The coordinator systematically collects information in the following categories:

1. **Basic Event Details**
   - Event type (conference, wedding, corporate meeting, etc.)
   - Event title/name
   - Event description and purpose
   - Expected attendee count
   - Event scale (small, medium, large)

2. **Timeline Information**
   - Start and end dates
   - Key milestones and deadlines
   - Setup and teardown requirements

3. **Budget Parameters**
   - Overall budget range
   - Budget allocation priorities
   - Payment timeline and requirements

4. **Location Requirements**
   - Geographic preferences
   - Venue type requirements
   - Space and capacity needs
   - Technical requirements

5. **Stakeholder Information**
   - Key stakeholders and their roles
   - Speakers/presenters (if applicable)
   - Sponsors (if applicable)
   - VIP attendees

6. **Resource Requirements**
   - Equipment needs
   - Staffing requirements
   - Service providers needed

7. **Success Criteria**
   - Primary goals for the event
   - Key performance indicators
   - Expected outcomes

8. **Risk Assessment**
   - Potential challenges
   - Contingency preferences
   - Insurance requirements

### Proposal Generation

Once sufficient information has been collected, the coordinator generates a comprehensive event proposal that includes:

1. Executive summary
2. Detailed event description
3. Timeline with milestones
4. Budget breakdown
5. Resource allocation plan
6. Stakeholder management approach
7. Risk management strategy
8. Success metrics
9. Next steps

### Task Delegation

After the proposal is approved, the coordinator delegates specific tasks to specialized agents:

- **Resource Planning Agent**: Handles venue selection, service providers, equipment
- **Financial Agent**: Manages budget, payments, contracts
- **Stakeholder Management Agent**: Coordinates sponsors, speakers, volunteers
- **Marketing & Communications Agent**: Manages campaigns, website, attendee communications
- **Project Management Agent**: Tracks tasks, timeline, risks
- **Analytics Agent**: Collects data, analyzes performance
- **Compliance & Security Agent**: Ensures legal requirements, security protocols

## Command Line Testing

Two scripts are provided for testing the coordinator agent:

1. **test_coordinator_proposal.py**: Tests the coordinator's ability to collect information and generate a proposal using a simulated conversation.

```bash
poetry run python test_coordinator_proposal.py
```

2. **run_coordinator.py**: Provides an interactive command-line interface to chat with the coordinator agent.

```bash
poetry run python run_coordinator.py
```

Special commands in the interactive chat:
- `status`: See the current state of the event planning
- `proposal`: Generate a proposal based on the information collected
- `approve`: Approve the proposal and proceed with implementation
- `debug`: Print the current state for debugging
- `exit`: End the conversation
