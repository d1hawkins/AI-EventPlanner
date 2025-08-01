# SaaS and Agent Database Analysis

This document provides an analysis of the database operations in the AI Event Planner SaaS application, focusing on what data is being written to and read from the database.

## Database Schema Overview

The application uses a relational database with the following key tables:

1. **users**: Stores user authentication and profile information
2. **organizations**: Stores tenant/organization information for multi-tenancy
3. **organization_users**: Maps users to organizations with role information
4. **subscription_plans**: Defines available subscription tiers and features
5. **subscription_invoices**: Tracks billing information for organizations
6. **conversations**: Stores chat sessions between users and agents
7. **messages**: Stores individual messages within conversations
8. **agent_states**: Stores the state of agents during conversations
9. **events**: Stores event planning details
10. **tasks**: Stores tasks related to events
11. **stakeholders**: Stores stakeholder information for events

## Data Written to the Database

### User Management

- **User Registration**: When a user registers, their email, username, and hashed password are written to the `users` table.
- **User Authentication**: Login attempts update the last login timestamp in the `users` table.

### Organization Management

- **Organization Creation**: When a new organization is created, its details are written to the `organizations` table.
- **User-Organization Association**: When a user is added to an organization, a record is created in the `organization_users` table with role information.

### Subscription Management

- **Subscription Plans**: Predefined subscription plans are stored in the `subscription_plans` table.
- **Organization Subscriptions**: When an organization subscribes to a plan, the organization record is updated with subscription details.
- **Billing Information**: Subscription invoices are written to the `subscription_invoices` table.

### Agent Interactions

- **Conversations**: When a user starts a conversation with an agent, a new record is created in the `conversations` table.
- **Messages**: Each message exchanged between the user and agent is written to the `messages` table.
- **Agent State**: The agent's memory and context are stored in the `agent_states` table, allowing conversations to be resumed.

### Event Planning

- **Events**: When a user creates an event, its details are written to the `events` table.
- **Tasks**: Tasks associated with events are written to the `tasks` table.
- **Stakeholders**: Stakeholder information is written to the `stakeholders` table.

## Data Read from the Database

### User Management

- **Authentication**: User credentials are read from the `users` table during login.
- **User Profile**: User information is read when displaying profile information.

### Organization Management

- **Organization Details**: Organization information is read when displaying organization details.
- **User Permissions**: User roles within organizations are read to determine access permissions.

### Subscription Management

- **Subscription Plans**: Available plans are read when displaying subscription options.
- **Current Subscription**: Organization subscription details are read to determine feature access.
- **Billing History**: Invoice records are read when displaying billing history.

### Agent Interactions

- **Conversation History**: Previous messages are read to provide context for ongoing conversations.
- **Agent State**: Agent state is read to resume conversations and maintain context.

### Event Planning

- **Events**: Event details are read when displaying event information.
- **Tasks**: Task lists are read when displaying event planning progress.
- **Stakeholders**: Stakeholder information is read when managing event participants.

## Multi-tenancy Implementation

The application implements multi-tenancy through the `organizations` table:

1. Each user can belong to multiple organizations (via `organization_users` table).
2. Each organization has its own subscription plan that determines feature access.
3. Events, conversations, and other resources are associated with specific organizations.
4. The application uses tenant context to filter data based on the current organization.

## Agent-Specific Database Operations

Agents interact with the database in the following ways:

1. **Reading Context**: Agents read conversation history and agent state to maintain context.
2. **Writing Responses**: Agent responses are written to the `messages` table.
3. **Updating State**: Agents update their state in the `agent_states` table.
4. **Creating Tasks**: Agents can create tasks in the `tasks` table based on conversation context.
5. **Reading Event Data**: Agents read event data to provide relevant recommendations.

## Feature Access Control

The application controls feature access based on subscription plans:

1. **Plan Features**: The `features` field in the `subscription_plans` table defines available features.
2. **Organization Features**: The organization's current plan determines which features are accessible.
3. **Agent Availability**: Access to specialized agents is controlled by the subscription plan.
4. **Usage Limits**: The number of events and users is limited based on the subscription plan.

## Database Transactions

The application uses database transactions to ensure data consistency:

1. **Organization Creation**: Creating an organization and adding the initial admin user is done in a transaction.
2. **Subscription Changes**: Updating an organization's subscription details is done in a transaction.
3. **Event Creation**: Creating an event and associated resources is done in a transaction.

## Conclusion

The AI Event Planner SaaS application uses a relational database to store and manage user data, organization information, subscription details, agent interactions, and event planning resources. The database schema is designed to support multi-tenancy, with clear separation between organizations and their resources.

Agents interact with the database primarily through conversations, reading context and writing responses. The application controls feature access based on subscription plans, ensuring that organizations only have access to the features included in their plan.
