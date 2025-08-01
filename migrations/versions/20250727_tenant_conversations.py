"""Add tenant-aware conversation models

Revision ID: 20250727_tenant_conversations
Revises: 20250722_conversation_memory
Create Date: 2025-07-27 21:42:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250727_tenant_conversations'
down_revision = '20250722_conversation_memory'
branch_labels = None
depends_on = None


def upgrade():
    # Create tenant_conversations table
    op.create_table('tenant_conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.Column('conversation_uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('conversation_type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('primary_agent_type', sa.String(length=100), nullable=True),
        sa.Column('agent_context', sa.JSON(), nullable=True),
        sa.Column('current_phase', sa.String(length=100), nullable=True),
        sa.Column('completion_percentage', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('conversation_uuid')
    )
    
    # Create indexes for tenant_conversations
    op.create_index('idx_tenant_user_conversations', 'tenant_conversations', ['organization_id', 'user_id'])
    op.create_index('idx_tenant_event_conversations', 'tenant_conversations', ['organization_id', 'event_id'])
    op.create_index('idx_conversation_context', 'tenant_conversations', ['organization_id', 'user_id', 'event_id'])
    op.create_index('idx_conversation_status', 'tenant_conversations', ['organization_id', 'status', 'updated_at'])
    op.create_index(op.f('ix_tenant_conversations_id'), 'tenant_conversations', ['id'])
    op.create_index(op.f('ix_tenant_conversations_organization_id'), 'tenant_conversations', ['organization_id'])
    op.create_index(op.f('ix_tenant_conversations_user_id'), 'tenant_conversations', ['user_id'])
    op.create_index(op.f('ix_tenant_conversations_event_id'), 'tenant_conversations', ['event_id'])

    # Create tenant_messages table
    op.create_table('tenant_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=True),
        sa.Column('agent_type', sa.String(length=100), nullable=True),
        sa.Column('agent_id', sa.String(length=255), nullable=True),
        sa.Column('message_uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_message_id', sa.Integer(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('is_internal', sa.Boolean(), nullable=True),
        sa.Column('is_error', sa.Boolean(), nullable=True),
        sa.Column('requires_action', sa.Boolean(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('edited_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['tenant_conversations.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['parent_message_id'], ['tenant_messages.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_uuid')
    )
    
    # Create indexes for tenant_messages
    op.create_index('idx_tenant_conversation_messages', 'tenant_messages', ['organization_id', 'conversation_id', 'timestamp'])
    op.create_index('idx_tenant_user_messages', 'tenant_messages', ['organization_id', 'user_id', 'timestamp'])
    op.create_index(op.f('ix_tenant_messages_id'), 'tenant_messages', ['id'])
    op.create_index(op.f('ix_tenant_messages_organization_id'), 'tenant_messages', ['organization_id'])
    op.create_index(op.f('ix_tenant_messages_conversation_id'), 'tenant_messages', ['conversation_id'])
    op.create_index(op.f('ix_tenant_messages_user_id'), 'tenant_messages', ['user_id'])
    op.create_index(op.f('ix_tenant_messages_timestamp'), 'tenant_messages', ['timestamp'])

    # Create tenant_agent_states table
    op.create_table('tenant_agent_states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.String(length=100), nullable=False),
        sa.Column('agent_id', sa.String(length=255), nullable=False),
        sa.Column('agent_version', sa.String(length=50), nullable=True),
        sa.Column('state_data', sa.JSON(), nullable=False),
        sa.Column('checkpoint_data', sa.JSON(), nullable=True),
        sa.Column('state_version', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('total_interactions', sa.Integer(), nullable=True),
        sa.Column('successful_interactions', sa.Integer(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_checkpoint_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['tenant_conversations.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for tenant_agent_states
    op.create_index('idx_tenant_agent_states', 'tenant_agent_states', ['organization_id', 'conversation_id', 'agent_type'])
    op.create_index('idx_agent_state_updates', 'tenant_agent_states', ['organization_id', 'agent_type', 'updated_at'])
    op.create_index(op.f('ix_tenant_agent_states_id'), 'tenant_agent_states', ['id'])
    op.create_index(op.f('ix_tenant_agent_states_organization_id'), 'tenant_agent_states', ['organization_id'])
    op.create_index(op.f('ix_tenant_agent_states_conversation_id'), 'tenant_agent_states', ['conversation_id'])
    op.create_index(op.f('ix_tenant_agent_states_user_id'), 'tenant_agent_states', ['user_id'])
    op.create_index(op.f('ix_tenant_agent_states_agent_type'), 'tenant_agent_states', ['agent_type'])

    # Create conversation_contexts table
    op.create_table('conversation_contexts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('user_preferences', sa.JSON(), nullable=True),
        sa.Column('conversation_memory', sa.JSON(), nullable=True),
        sa.Column('decision_history', sa.JSON(), nullable=True),
        sa.Column('topic_transitions', sa.JSON(), nullable=True),
        sa.Column('event_requirements', sa.JSON(), nullable=True),
        sa.Column('budget_constraints', sa.JSON(), nullable=True),
        sa.Column('timeline_constraints', sa.JSON(), nullable=True),
        sa.Column('stakeholder_context', sa.JSON(), nullable=True),
        sa.Column('communication_style', sa.String(length=100), nullable=True),
        sa.Column('preferred_detail_level', sa.String(length=50), nullable=True),
        sa.Column('response_preferences', sa.JSON(), nullable=True),
        sa.Column('context_version', sa.Integer(), nullable=True),
        sa.Column('last_summary_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['tenant_conversations.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('conversation_id')
    )
    
    # Create indexes for conversation_contexts
    op.create_index('idx_conversation_context_tenant', 'conversation_contexts', ['organization_id', 'conversation_id'])
    op.create_index(op.f('ix_conversation_contexts_id'), 'conversation_contexts', ['id'])
    op.create_index(op.f('ix_conversation_contexts_organization_id'), 'conversation_contexts', ['organization_id'])
    op.create_index(op.f('ix_conversation_contexts_user_id'), 'conversation_contexts', ['user_id'])

    # Create conversation_participants table
    op.create_table('conversation_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('notification_preferences', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['tenant_conversations.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for conversation_participants
    op.create_index('idx_conversation_participants', 'conversation_participants', ['organization_id', 'conversation_id', 'user_id'])
    op.create_index(op.f('ix_conversation_participants_id'), 'conversation_participants', ['id'])
    op.create_index(op.f('ix_conversation_participants_organization_id'), 'conversation_participants', ['organization_id'])
    op.create_index(op.f('ix_conversation_participants_conversation_id'), 'conversation_participants', ['conversation_id'])
    op.create_index(op.f('ix_conversation_participants_user_id'), 'conversation_participants', ['user_id'])

    # Set default values for new columns
    op.execute("UPDATE tenant_conversations SET conversation_type = 'event_planning' WHERE conversation_type IS NULL")
    op.execute("UPDATE tenant_conversations SET status = 'active' WHERE status IS NULL")
    op.execute("UPDATE tenant_conversations SET completion_percentage = 0 WHERE completion_percentage IS NULL")
    op.execute("UPDATE tenant_messages SET content_type = 'text' WHERE content_type IS NULL")
    op.execute("UPDATE tenant_messages SET is_internal = false WHERE is_internal IS NULL")
    op.execute("UPDATE tenant_messages SET is_error = false WHERE is_error IS NULL")
    op.execute("UPDATE tenant_messages SET requires_action = false WHERE requires_action IS NULL")
    op.execute("UPDATE tenant_agent_states SET state_version = 1 WHERE state_version IS NULL")
    op.execute("UPDATE tenant_agent_states SET is_active = true WHERE is_active IS NULL")
    op.execute("UPDATE tenant_agent_states SET total_interactions = 0 WHERE total_interactions IS NULL")
    op.execute("UPDATE tenant_agent_states SET successful_interactions = 0 WHERE successful_interactions IS NULL")
    op.execute("UPDATE tenant_agent_states SET error_count = 0 WHERE error_count IS NULL")
    op.execute("UPDATE conversation_contexts SET context_version = 1 WHERE context_version IS NULL")
    op.execute("UPDATE conversation_participants SET role = 'participant' WHERE role IS NULL")
    op.execute("UPDATE conversation_participants SET is_active = true WHERE is_active IS NULL")


def downgrade():
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('conversation_participants')
    op.drop_table('conversation_contexts')
    op.drop_table('tenant_agent_states')
    op.drop_table('tenant_messages')
    op.drop_table('tenant_conversations')
