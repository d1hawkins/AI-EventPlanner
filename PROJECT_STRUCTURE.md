# AI Event Planner - Project Structure

## Overview
This is an AI-powered event planning SaaS application with specialized AI agents for different aspects of event planning.

## Core Application Structure

```
AI-EventPlanner/
├── app/                          # Main application code
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── main_saas.py             # SaaS-specific application entry point
│   ├── config.py                # Application configuration
│   │
│   ├── agents/                  # AI agent system
│   │   ├── __init__.py
│   │   ├── agent_factory.py     # Agent creation and management
│   │   └── api_router.py        # Agent API endpoints
│   │
│   ├── auth/                    # Authentication system
│   │   ├── __init__.py
│   │   ├── router.py           # Auth routes
│   │   └── dependencies.py     # Auth dependencies
│   │
│   ├── db/                      # Database models and session
│   │   ├── __init__.py
│   │   ├── base.py             # Database base configuration
│   │   ├── session.py          # Database session management
│   │   ├── models.py           # Core database models
│   │   ├── models_saas.py      # SaaS-specific models
│   │   └── models_tenant_conversations.py  # Tenant conversation models
│   │
│   ├── graphs/                  # LangGraph workflow definitions
│   │   ├── __init__.py
│   │   ├── coordinator_graph.py           # Main coordinator workflow
│   │   ├── analytics_graph.py             # Analytics agent workflow
│   │   ├── compliance_security_graph.py   # Compliance agent workflow
│   │   ├── financial_graph.py             # Financial agent workflow
│   │   ├── marketing_communications_graph.py  # Marketing agent workflow
│   │   ├── project_management_graph.py    # Project management workflow
│   │   ├── resource_planning_graph.py     # Resource planning workflow
│   │   └── stakeholder_management_graph.py # Stakeholder management workflow
│   │
│   ├── schemas/                 # Pydantic schemas for data validation
│   │   ├── __init__.py
│   │   ├── user.py             # User schemas
│   │   ├── event.py            # Event schemas
│   │   ├── analytics.py        # Analytics schemas
│   │   ├── compliance.py       # Compliance schemas
│   │   ├── financial.py        # Financial schemas
│   │   ├── marketing.py        # Marketing schemas
│   │   ├── project.py          # Project management schemas
│   │   └── stakeholder.py      # Stakeholder schemas
│   │
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── tenant_conversation_service.py
│   │   └── tenant_conversation_service_with_fallback.py
│   │
│   ├── state/                   # State management
│   │   ├── __init__.py
│   │   ├── manager.py          # State manager
│   │   └── tenant_aware_manager.py  # Tenant-aware state management
│   │
│   ├── subscription/            # Subscription and billing
│   │   ├── __init__.py
│   │   ├── router.py           # Subscription routes
│   │   ├── schemas.py          # Subscription schemas
│   │   └── feature_control.py  # Feature access control
│   │
│   ├── tools/                   # Agent tools and utilities
│   │   ├── __init__.py
│   │   ├── agent_communication_tools.py    # Inter-agent communication
│   │   ├── analytics_tools.py              # Analytics tools
│   │   ├── compliance_tools.py             # Compliance tools
│   │   ├── coordinator_search_tool.py      # Coordinator search
│   │   ├── event_tools.py                  # Event management tools
│   │   ├── financial_tools.py              # Financial tools
│   │   ├── marketing_tools.py              # Marketing tools
│   │   ├── project_tools.py                # Project management tools
│   │   ├── stakeholder_tools.py            # Stakeholder tools
│   │   └── tenant_agent_communication_tools.py  # Tenant-aware communication
│   │
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── azure_logging.py    # Azure-specific logging
│   │   ├── conversation_memory.py          # Conversation memory management
│   │   ├── conversation_paths.py           # Conversation flow paths
│   │   ├── llm_factory.py                  # LLM provider factory
│   │   ├── logging_utils.py                # General logging utilities
│   │   ├── mcp_adapter.py                  # MCP server adapter
│   │   ├── persistent_conversation_memory.py  # Persistent memory
│   │   ├── proactive_suggestions.py        # Proactive suggestion system
│   │   ├── question_manager.py             # Question management
│   │   ├── recommendation_engine.py        # Recommendation system
│   │   ├── recommendation_learning.py      # Learning recommendations
│   │   └── search_utils.py                 # Search utilities
│   │
│   ├── middleware/              # Middleware components
│   │   ├── __init__.py
│   │   └── tenant.py           # Tenant isolation middleware
│   │
│   └── web/                     # Web interface
│       ├── __init__.py
│       ├── router.py           # Web routes
│       └── static/             # Static web assets
│           ├── index.html      # Main landing page
│           ├── css/            # Stylesheets
│           ├── js/             # JavaScript files
│           └── saas/           # SaaS-specific web interface
│               ├── index.html  # SaaS dashboard
│               ├── css/        # SaaS stylesheets
│               ├── js/         # SaaS JavaScript
│               └── *.html      # Various SaaS pages
│
├── migrations/                  # Database migrations
│   ├── env.py                  # Alembic environment
│   ├── script.py.mako          # Migration template
│   └── versions/               # Migration versions
│
├── scripts/                     # Database and utility scripts
│   └── *.py                    # Various database setup scripts
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Test configuration
│   └── *.py                    # Test files
│
├── examples/                    # Example code and demos
│   └── mcp_example.py          # MCP server example
│
├── mcp-servers/                 # MCP server implementations
│   ├── README.md
│   ├── sendgrid-mcp/           # SendGrid MCP server
│   └── openweather-mcp/        # OpenWeather MCP server
│
├── archive/                     # Archived files (organized cleanup)
│   ├── deployment/             # Deployment-related files
│   │   ├── azure-scripts/      # Azure deployment scripts
│   │   ├── docker/             # Docker configurations
│   │   └── configs/            # Deployment configurations
│   ├── development/            # Development artifacts
│   │   ├── app-adapters/       # Various app adapter versions
│   │   ├── tests/              # Old test files
│   │   ├── fixes/              # Bug fix scripts
│   │   └── utilities/          # Development utilities
│   ├── documentation/          # Documentation files
│   │   ├── planning/           # Planning documents
│   │   ├── azure/              # Azure-specific documentation
│   │   └── implementation/     # Implementation guides
│   └── legacy/                 # Legacy files and environments
│       ├── environments/       # Old environment files
│       ├── scripts/            # Legacy scripts
│       └── logs/               # Old log files
│
├── .github/                     # GitHub workflows
│   └── workflows/              # CI/CD workflows
│
├── app_adapter_with_agents_fixed.py  # Current production adapter
├── alembic.ini                 # Alembic configuration
├── langgraph.json              # LangGraph configuration
├── package.json                # Node.js dependencies (for MCP servers)
├── pyproject.toml              # Python project configuration
├── requirements.txt            # Python dependencies
├── Procfile                    # Process file for deployment
├── web.config                  # Web server configuration
├── .dockerignore               # Docker ignore file
├── .gitignore                  # Git ignore file
└── README.md                   # Project documentation
```

## Key Components

### AI Agent System
- **Coordinator Agent**: Main orchestrator that delegates tasks to specialized agents
- **Specialized Agents**: Analytics, Compliance, Financial, Marketing, Project Management, Resource Planning, Stakeholder Management
- **Agent Communication**: Inter-agent communication system with tenant awareness
- **Conversation Memory**: Persistent conversation history and context management

### SaaS Features
- **Multi-tenant Architecture**: Tenant isolation and data separation
- **Subscription Management**: Feature access control based on subscription tiers
- **User Authentication**: Secure user authentication and authorization
- **Web Interface**: Modern web interface for event planning and agent interaction

### Database
- **PostgreSQL**: Primary database with Azure PostgreSQL support
- **Alembic Migrations**: Database schema versioning and migrations
- **Multi-tenant Models**: Tenant-aware data models

### Deployment
- **Azure App Service**: Cloud deployment on Azure
- **Docker Support**: Containerized deployment options
- **Environment Management**: Multiple environment configurations

### MCP Integration
- **SendGrid**: Email service integration
- **OpenWeather**: Weather data integration
- **Extensible**: Framework for adding additional MCP servers

## Getting Started

1. **Local Development**: Use `app_adapter_with_agents_fixed.py` as the main entry point
2. **Database Setup**: Run migrations in the `migrations/` directory
3. **Environment**: Configure environment variables (see archive/legacy/environments/ for examples)
4. **Dependencies**: Install from `requirements.txt`
5. **Web Interface**: Access the SaaS interface at `/saas/`

## Architecture Notes

- **Event-Driven**: Uses LangGraph for workflow orchestration
- **Microservices-Ready**: Modular design supports service separation
- **Cloud-Native**: Designed for Azure cloud deployment
- **Extensible**: Plugin architecture for adding new agents and tools
