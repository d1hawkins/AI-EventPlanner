"""Rename event time columns from start_time/end_time to start_date/end_date

Revision ID: 20251027_rename_time_columns
Revises: 20251027_add_missing_columns
Create Date: 2025-10-27 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251027_rename_time_columns'
down_revision = '20251027_add_missing_columns'
branch_labels = None
depends_on = None


def upgrade():
    # Check if columns exist and rename them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    events_columns = [col['name'] for col in inspector.get_columns('events')]

    # Rename start_time to start_date if it exists
    if 'start_time' in events_columns and 'start_date' not in events_columns:
        op.alter_column('events', 'start_time', new_column_name='start_date')

    # Rename end_time to end_date if it exists
    if 'end_time' in events_columns and 'end_date' not in events_columns:
        op.alter_column('events', 'end_time', new_column_name='end_date')


def downgrade():
    # Rename back to start_time/end_time
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    events_columns = [col['name'] for col in inspector.get_columns('events')]

    if 'start_date' in events_columns and 'start_time' not in events_columns:
        op.alter_column('events', 'start_date', new_column_name='start_time')

    if 'end_date' in events_columns and 'end_time' not in events_columns:
        op.alter_column('events', 'end_date', new_column_name='end_time')
