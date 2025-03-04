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
├── pyproject.toml    # Project dependencies
└── README.md         # This file
```

## Setup

1. Install dependencies:

```bash
pip install poetry
poetry install
```

2. Create a `.env` file with your configuration:

```
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key_for_jwt
DATABASE_URL=sqlite:///./app.db
```

3. Run the application:

```bash
poetry run uvicorn app.main:app --reload
```

4. Access the chat interface at http://localhost:8000

## Development

- Run tests: `poetry run pytest`
- Format code: `poetry run black .`

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
