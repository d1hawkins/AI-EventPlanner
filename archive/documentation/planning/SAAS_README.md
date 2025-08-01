# AI Event Planner SaaS

This is a SaaS (Software as a Service) version of the AI Event Planner application. It includes multi-tenancy, subscription management, and is designed to be deployed to Azure.

## Features

- **Multi-tenancy**: Each organization has its own isolated data and users
- **Subscription Management**: Different subscription tiers with varying features and limits
- **User Management**: Invite team members, manage roles and permissions
- **Event Planning**: AI-powered event planning with specialized agents
- **Azure Deployment**: Ready to deploy to Azure App Service and Azure Database for PostgreSQL

## Getting Started

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Azure account (for deployment)

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-event-planner.git
   cd ai-event-planner
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   cp .env.saas.example .env
   # Edit .env with your configuration
   ```

4. Run database migrations:
   ```
   alembic upgrade head
   ```

5. Run the application:
   ```
   python run_saas.py
   ```

   Or to just view the static files:
   ```
   python serve_saas_static.py
   ```

6. Access the application at http://localhost:8000/static/saas/index.html

### Docker Development

1. Build and run the Docker container:
   ```
   ./run_saas_docker.sh
   ```

2. Access the application at http://localhost:8000/static/saas/index.html

## Deployment to Azure

### Prerequisites

- Azure CLI installed and configured
- Azure subscription
- Azure App Service plan
- Azure Database for PostgreSQL

### Deployment Steps

1. Set up environment variables for Azure:
   ```
   cp .env.saas.example .env.azure
   # Edit .env.azure with your Azure configuration
   ```

2. Deploy to Azure:
   ```
   ./azure-deploy-saas.sh
   ```

3. Access your application at https://your-app-name.azurewebsites.net

## Architecture

### Backend

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and settings management
- **LangGraph**: Framework for building LLM-powered agents

### Frontend

- **HTML/CSS/JavaScript**: Simple, responsive UI
- **Bootstrap**: CSS framework for responsive design

### Database

- **PostgreSQL**: Relational database for storing application data
- **Multi-tenant schema**: Each organization has its own schema

### Azure Services

- **Azure App Service**: Hosting the application
- **Azure Database for PostgreSQL**: Database service
- **Azure Blob Storage**: Storing files and assets
- **Azure Key Vault**: Managing secrets
- **Azure Application Insights**: Monitoring and analytics

## Subscription Plans

### Free Plan
- Up to 5 users
- Up to 10 events
- Basic features

### Professional Plan
- Up to 20 users
- Up to 50 events
- Advanced features
- Priority support

### Enterprise Plan
- Unlimited users
- Unlimited events
- All features
- Premium support
- Custom integrations

## Development

### Project Structure

- `app/`: Main application package
  - `auth/`: Authentication and authorization
  - `db/`: Database models and session management
  - `middleware/`: Middleware for multi-tenancy
  - `schemas/`: Pydantic models for data validation
  - `subscription/`: Subscription management
  - `tools/`: AI agent tools
  - `utils/`: Utility functions
  - `web/`: Web interface
- `migrations/`: Database migrations
- `scripts/`: Utility scripts
- `tests/`: Test suite

### Adding a New Feature

1. Create a new branch:
   ```
   git checkout -b feature/your-feature-name
   ```

2. Implement your feature

3. Write tests

4. Run tests:
   ```
   pytest
   ```

5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- OpenAI for providing the LLM models
- FastAPI for the web framework
- SQLAlchemy for the ORM
- Bootstrap for the CSS framework
