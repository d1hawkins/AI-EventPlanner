"""Rename tenant_messages metadata column to message_metadata

Revision ID: 20251027_rename_metadata_column
Revises: 20251027_rename_time_columns
Create Date: 2025-10-27 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251027_rename_metadata_column'
down_revision = '20251027_rename_time_columns'
branch_labels = None
depends_on = None


def upgrade():
    # Check if columns exist and rename them
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Check if tenant_messages table exists
    tables = inspector.get_table_names()
    if 'tenant_messages' not in tables:
        # Table doesn't exist yet, skip this migration
        return

    tenant_messages_columns = [col['name'] for col in inspector.get_columns('tenant_messages')]

    # Rename metadata to message_metadata if needed
    if 'metadata' in tenant_messages_columns and 'message_metadata' not in tenant_messages_columns:
        op.alter_column('tenant_messages', 'metadata', new_column_name='message_metadata')


def downgrade():
    # Rename back to metadata
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    tables = inspector.get_table_names()
    if 'tenant_messages' not in tables:
        return

    tenant_messages_columns = [col['name'] for col in inspector.get_columns('tenant_messages')]

    if 'message_metadata' in tenant_messages_columns and 'metadata' not in tenant_messages_columns:
        op.alter_column('tenant_messages', 'message_metadata', new_column_name='metadata')
