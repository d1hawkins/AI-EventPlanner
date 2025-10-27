"""Add missing columns to events and agent_states

Revision ID: 20251027_add_missing_columns
Revises: 20250727_tenant_conversations
Create Date: 2025-10-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251027_add_missing_columns'
down_revision = '20250727_tenant_conversations'
branch_labels = None
depends_on = None


def upgrade():
    # Check if columns exist before adding them
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Add event_type column to events table if it doesn't exist
    events_columns = [col['name'] for col in inspector.get_columns('events')]
    if 'event_type' not in events_columns:
        op.add_column('events', sa.Column('event_type', sa.String(), nullable=True))

    # Add state_data column to agent_states table if it doesn't exist
    agent_states_columns = [col['name'] for col in inspector.get_columns('agent_states')]
    if 'state_data' not in agent_states_columns:
        op.add_column('agent_states', sa.Column('state_data', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade():
    # Remove the columns
    op.drop_column('agent_states', 'state_data')
    op.drop_column('events', 'event_type')
