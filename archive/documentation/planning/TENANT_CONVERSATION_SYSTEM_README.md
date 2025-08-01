# Tenant-Aware Conversation System

## Overview

This document describes the comprehensive tenant-aware conversation system implemented for the AI Event Planner. The system ensures that **all conversations are properly tied to a Tenant (Organization), User, and Conversation/Event ID**, providing complete multi-tenant data isolation and context tracking.

## Key Requirements Addressed

✅ **All conversations are tied to:**
1. **Tenant (Organization)** - Ensures multi-tenant data isolation
2. **User** - Tracks individual user context within the tenant
3. **Conversation/Event ID** - Provides specific conversation and event context

## System Architecture

### Core Components

#### 1. Database Models (`app/db/models_tenant_conversations.py`)

**TenantConversation**
- Primary conversation model with full tenant context
- Links to Organization, User, and optionally Event
- Tracks conversation metadata, status, and agent context
- Includes UUID for external references

**TenantMessage**
- All messages tied to tenant, user, and conversation
- Supports both user and agent messages
- Includes threading, metadata, and processing information
- Tracks internal vs external messages

**TenantAgentState**
- Agent state management with tenant context
- Stores complete agent state and checkpoints
- Tracks performance metrics per agent
- Supports multiple agents per conversation

**ConversationContext**
- Rich context storage for conversations
- User preferences, decisions, and memory
- Event-specific requirements and constraints
- Communication style and preferences

**ConversationParticipant**
- Multi-user conversation support
- Role-based access control
- Participant permissions and preferences

#### 2. Service Layer (`app/services/tenant_conversation_service.py`)

**TenantConversationService**
- Core service for conversation management
- Enforces tenant/user access control
- Provides CRUD operations with proper scoping
- Handles conversation context and participants

Key Methods:
- `create_conversation()` - Creates tenant-scoped conversations
- `get_conversation()` - Retrieves with access validation
- `list_conversations()` - Lists with tenant/user filtering
- `add_message()` - Adds messages with full context
- `update_agent_state()` - Manages agent states
- `update_conversation_context()` - Updates conversation context

#### 3. Agent Communication Tools (`app/tools/tenant_agent_communication_tools.py`)

**TenantAgentCommunicationTools**
- Tenant-aware agent communication interface
- Ensures all agent interactions have proper context
- Provides preference and decision tracking
- Handles internal agent-to-agent communication

Key Features:
- `send_message_to_user()` - User-facing messages
- `send_internal_message()` - Agent-to-agent communication
- `delegate_task()` - Task delegation between agents
- `track_user_preference()` - Preference discovery and storage
- `track_decision()` - Decision tracking with reasoning
- `get_conversation_context()` - Context retrieval

### Data Flow

```
1. Request → Tenant Middleware → Extract Organization/User Context
2. Service Layer → Validate Tenant/User Access
3. Database Operations → Scoped to Tenant/User/Conversation
4. Agent Tools → Operate within Tenant Context
5. Response → Filtered by Tenant/User Permissions
```

## Multi-Tenant Data Isolation

### Tenant Scoping
- All database queries filtered by `organization_id`
- User access validated through `OrganizationUser` relationships
- Event associations validated within tenant scope

### Access Control
- Users can only access conversations they own or participate in
- Cross-tenant data access is prevented at the service layer
- Agent states are isolated per tenant/conversation

### Data Integrity
- Foreign key constraints ensure referential integrity
- Composite indexes optimize tenant-scoped queries
- UUID fields provide external reference capabilities

## Usage Examples

### Creating a Tenant-Scoped Conversation

```python
from app.services.tenant_conversation_service import TenantConversationService

# Initialize service with tenant context
service = TenantConversationService(
    db=db_session,
    organization_id=1,  # Tenant ID
    user_id=123        # User ID
)

# Create conversation tied to tenant, user, and event
conversation = service.create_conversation(
    title="Corporate Event Planning",
    conversation_type="event_planning",
    event_id=456,  # Event/Conversation ID
    description="Planning the annual corporate conference",
    primary_agent_type="coordinator"
)
```

### Agent Communication with Full Context

```python
from app.tools.tenant_agent_communication_tools import TenantAgentCommunicationTools

# Initialize agent tools with full context
agent_tools = TenantAgentCommunicationTools(
    db=db_session,
    organization_id=1,      # Tenant
    user_id=123,           # User
    conversation_id=789,   # Conversation/Event ID
    agent_type="coordinator",
    agent_id="coord_001"
)

# Send message to user (tied to all context)
agent_tools.send_message_to_user(
    content="I've analyzed your event requirements and have some recommendations.",
    requires_action=True
)

# Track user preference (stored with tenant context)
agent_tools.track_user_preference(
    preference_type="venue_style",
    value="modern_corporate",
    confidence=0.9
)

# Delegate task to another agent (internal communication)
agent_tools.delegate_task(
    target_agent_type="financial",
    task_description="Analyze budget requirements for 200-person conference",
    task_data={"attendee_count": 200, "event_type": "conference"}
)
```

### Retrieving Tenant-Scoped Data

```python
# List conversations for specific tenant/user
conversations, total = service.list_conversations(
    limit=50,
    conversation_type="event_planning",
    event_id=456  # Filter by specific event
)

# Get conversation with access validation
conversation = service.get_conversation(
    conversation_id=789,
    include_messages=True,
    include_context=True
)

# Get conversation summary with full context
summary = service.get_conversation_summary(conversation_id=789)
```

## Database Schema

### Key Tables and Relationships

```sql
-- Core conversation table with tenant context
tenant_conversations (
    id, organization_id, user_id, event_id,
    conversation_uuid, title, description,
    conversation_type, status, primary_agent_type,
    agent_context, current_phase, completion_percentage,
    created_at, updated_at, last_activity_at
)

-- Messages with full context
tenant_messages (
    id, organization_id, conversation_id, user_id,
    role, content, content_type, agent_type, agent_id,
    message_uuid, parent_message_id, processing_time_ms,
    token_count, is_internal, is_error, requires_action,
    metadata, timestamp, edited_at
)

-- Agent states with tenant context
tenant_agent_states (
    id, organization_id, conversation_id, user_id,
    agent_type, agent_id, agent_version,
    state_data, checkpoint_data, state_version,
    is_active, total_interactions, successful_interactions,
    error_count, created_at, updated_at, last_checkpoint_at
)

-- Rich conversation context
conversation_contexts (
    id, organization_id, conversation_id, user_id,
    user_preferences, conversation_memory, decision_history,
    topic_transitions, event_requirements, budget_constraints,
    timeline_constraints, stakeholder_context,
    communication_style, preferred_detail_level,
    response_preferences, context_version, last_summary_at,
    created_at, updated_at
)

-- Multi-participant support
conversation_participants (
    id, organization_id, conversation_id, user_id,
    role, permissions, joined_at, last_seen_at,
    is_active, notification_preferences
)
```

### Indexes for Performance

```sql
-- Tenant-scoped queries
CREATE INDEX idx_tenant_user_conversations ON tenant_conversations (organization_id, user_id);
CREATE INDEX idx_tenant_event_conversations ON tenant_conversations (organization_id, event_id);
CREATE INDEX idx_conversation_context ON tenant_conversations (organization_id, user_id, event_id);

-- Message queries
CREATE INDEX idx_tenant_conversation_messages ON tenant_messages (organization_id, conversation_id, timestamp);
CREATE INDEX idx_tenant_user_messages ON tenant_messages (organization_id, user_id, timestamp);

-- Agent state queries
CREATE INDEX idx_tenant_agent_states ON tenant_agent_states (organization_id, conversation_id, agent_type);
```

## Testing

### Comprehensive Test Suite (`test_tenant_conversation_system.py`)

The test suite validates:

1. **Tenant Isolation** - Organizations cannot access each other's data
2. **User Access Control** - Users can only access authorized conversations
3. **Context Preservation** - All operations maintain tenant/user/conversation context
4. **Agent Communication** - Agent tools work within proper context
5. **Data Integrity** - Foreign key relationships and constraints work correctly
6. **Multi-Participant Support** - Multiple users can participate in conversations
7. **Event Association** - Conversations properly link to events

### Running Tests

```bash
python test_tenant_conversation_system.py
```

Expected output:
```
✓ test_tenant_conversation_creation
✓ test_tenant_isolation
✓ test_user_access_control
✓ test_message_creation_with_tenant_context
✓ test_agent_state_management
✓ test_agent_communication_tools
✓ test_conversation_context_management
✓ test_conversation_summary
✓ test_multi_participant_conversation
✓ test_event_conversation_association
✓ test_conversation_status_and_phases

Test Results: 11 passed, 0 failed
🎉 ALL TESTS PASSED!
```

## Migration

### Database Migration (`migrations/versions/20250727_tenant_conversations.py`)

The migration creates all necessary tables with:
- Proper foreign key relationships
- Optimized indexes for tenant-scoped queries
- Default values for new columns
- UUID support for external references

### Running Migration

```bash
alembic upgrade head
```

## Integration with Existing System

### Middleware Integration

The system integrates with existing tenant middleware (`app/middleware/tenant.py`) to:
- Extract tenant context from requests
- Validate user-organization relationships
- Provide tenant-scoped database sessions

### Agent Factory Integration

Agent factories can use the tenant-aware tools:

```python
def create_agent_with_tenant_context(
    agent_type: str,
    organization_id: int,
    user_id: int,
    conversation_id: int
):
    # Create agent with tenant-aware communication tools
    agent_tools = TenantAgentCommunicationTools(
        db=db,
        organization_id=organization_id,
        user_id=user_id,
        conversation_id=conversation_id,
        agent_type=agent_type
    )
    
    # Agent now has full tenant context for all operations
    return agent_tools
```

## Security Considerations

### Data Isolation
- All queries are scoped to organization_id
- Cross-tenant data access is prevented at multiple layers
- User permissions are validated for each operation

### Access Control
- Role-based access through conversation participants
- Permission-based operations within conversations
- Audit trail through message and state tracking

### Data Privacy
- Tenant data is completely isolated
- No cross-tenant information leakage
- Secure UUID-based external references

## Performance Considerations

### Indexing Strategy
- Composite indexes for common query patterns
- Tenant-scoped indexes for efficient filtering
- Time-based indexes for message retrieval

### Caching
- Conversation context can be cached per tenant
- Agent states support checkpoint-based recovery
- Message pagination for large conversations

### Scalability
- Horizontal scaling by tenant
- Database sharding possibilities
- Efficient query patterns for large datasets

## Monitoring and Analytics

### Metrics Tracked
- Agent interaction success rates
- Conversation completion percentages
- User engagement per tenant
- Message volume and processing times

### Audit Trail
- Complete message history with timestamps
- Agent state changes with versions
- User preference evolution tracking
- Decision history with reasoning

## Future Enhancements

### Planned Features
1. **Real-time Collaboration** - WebSocket support for multi-user conversations
2. **Advanced Analytics** - Tenant-specific usage analytics and insights
3. **Conversation Templates** - Reusable conversation patterns per tenant
4. **Integration APIs** - External system integration with tenant context
5. **Advanced Permissions** - Fine-grained permission system for conversations

### Extensibility
- Plugin architecture for custom agent types
- Webhook support for external integrations
- Custom context fields per tenant
- Configurable conversation workflows

## Conclusion

The tenant-aware conversation system successfully addresses the requirement that **all conversations be tied to a Tenant, User, and Conversation/Event ID**. The system provides:

- ✅ Complete multi-tenant data isolation
- ✅ Comprehensive user access control
- ✅ Full conversation and event context tracking
- ✅ Agent communication with proper scoping
- ✅ Rich context and memory management
- ✅ Scalable and secure architecture
- ✅ Comprehensive testing and validation

The system is production-ready and provides a solid foundation for multi-tenant AI agent conversations with complete context preservation and data isolation.
