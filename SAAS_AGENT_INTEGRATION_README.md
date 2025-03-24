# SaaS Agent Integration

This document provides instructions for using the AI Event Planner SaaS platform with integrated AI agents.

## Overview

The AI Event Planner SaaS platform now includes integrated AI agents that can assist with various aspects of event planning. These agents are available based on your subscription tier and can help with tasks such as:

- Event coordination
- Resource planning
- Financial planning
- Stakeholder management
- Marketing and communications
- Project management
- Analytics
- Compliance and security

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL (for production) or SQLite (for development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-event-planner.git
   cd ai-event-planner
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.saas.example .env.saas
   # Edit .env.saas with your configuration
   ```

4. Run the application:
   ```bash
   python run_saas_with_agents.py
   ```

5. Access the application at http://localhost:8002

### Configuration

The following environment variables can be configured in `.env.saas`:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `LLM_PROVIDER`: LLM provider (openai, google, or azure_openai)
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI)
- `GOOGLE_API_KEY`: Google AI API key (if using Google)
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key (if using Azure)

## Using AI Agents

### Accessing Agents

1. Log in to your account at http://localhost:8002/saas/login.html
2. Navigate to the AI Agents page from the sidebar
3. Select an agent to start a conversation

### Available Agents

The following agents are available based on your subscription tier:

#### Free Tier
- **Event Coordinator**: Orchestrates the event planning process
- **Resource Planner**: Plans and manages resources needed for your event

#### Professional Tier
- All Free tier agents
- **Financial Advisor**: Handles budgeting and financial planning
- **Stakeholder Manager**: Manages communication with stakeholders
- **Marketing Specialist**: Creates marketing strategies
- **Project Manager**: Manages timelines and tasks

#### Enterprise Tier
- All Professional tier agents
- **Analytics Expert**: Analyzes event data
- **Compliance & Security Specialist**: Ensures compliance with regulations

### Agent Capabilities

Each agent has specific capabilities:

- **Event Coordinator**:
  - Event planning coordination
  - Task delegation
  - Progress tracking

- **Resource Planner**:
  - Venue selection
  - Equipment planning
  - Staff allocation

- **Financial Advisor**:
  - Budget creation
  - Cost estimation
  - Financial tracking

- **Stakeholder Manager**:
  - Stakeholder identification
  - Communication planning
  - Expectation management

- **Marketing Specialist**:
  - Marketing strategy
  - Content creation
  - Social media planning

- **Project Manager**:
  - Timeline creation
  - Task management
  - Risk management

- **Analytics Expert**:
  - Data collection planning
  - Performance analysis
  - Insights & recommendations

- **Compliance & Security Specialist**:
  - Compliance assessment
  - Security planning
  - Risk assessment

## Conversation Management

### Starting a Conversation

1. Select an agent from the AI Agents page
2. Type your message in the chat input
3. Press Enter or click Send

### Viewing Conversation History

1. Navigate to the AI Agents page
2. View your recent conversations in the sidebar
3. Click on a conversation to continue

### Exporting Conversations

1. Open a conversation with an agent
2. Click the Export button
3. Save the exported file to your computer

## Subscription Management

### Viewing Your Subscription

1. Navigate to the Subscription page from the sidebar
2. View your current subscription tier and features

### Upgrading Your Subscription

1. Navigate to the Subscription page
2. Click the Upgrade button
3. Select a new subscription tier
4. Complete the payment process

## Troubleshooting

### Common Issues

- **Agent not available**: Check your subscription tier
- **Cannot send message**: Ensure you are logged in
- **Error loading agents**: Try refreshing the page

### Support

For additional support, contact support@aieventplanner.com or use the Support page in the application.

## Development

### Architecture

The SaaS agent integration follows a multi-tenant architecture:

1. **Frontend**: React components for agent interaction
2. **Backend**: FastAPI endpoints with tenant context
3. **Database**: Multi-tenant data storage
4. **AI System**: LangGraph-based agent system

### Adding New Agents

To add a new agent:

1. Create a new agent graph in `app/graphs/`
2. Add the agent to `app/agents/agent_factory.py`
3. Update the agent metadata in `app/agents/api_router.py`
4. Add the agent capabilities to `app/web/static/saas/js/agent-service.js`

### Testing

Run the tests with:

```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
