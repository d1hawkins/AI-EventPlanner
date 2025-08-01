"""Add conversation memory table

Revision ID: 20250722_conversation_memory
Revises: 20250322_saas_migration
Create Date: 2025-07-22 00:33:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250722_conversation_memory'
down_revision = '20250322_saas_migration'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conversation_memory',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.String(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.Column('memory_type', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('context', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_memory_conversation_id'), 'conversation_memory', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_conversation_memory_id'), 'conversation_memory', ['id'], unique=False)
    op.create_index(op.f('ix_conversation_memory_organization_id'), 'conversation_memory', ['organization_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_conversation_memory_organization_id'), table_name='conversation_memory')
    op.drop_index(op.f('ix_conversation_memory_id'), table_name='conversation_memory')
    op.drop_index(op.f('ix_conversation_memory_conversation_id'), table_name='conversation_memory')
    op.drop_table('conversation_memory')
    # ### end Alembic commands ###
