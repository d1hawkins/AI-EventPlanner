"""SaaS migration

Revision ID: 20250322_saas
Revises: 
Create Date: 2025-03-22 17:38:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250322_saas'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('plan_id', sa.String(length=50), nullable=False),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('subscription_status', sa.String(length=50), server_default='inactive', nullable=True),
        sa.Column('max_users', sa.Integer(), server_default='5', nullable=True),
        sa.Column('max_events', sa.Integer(), server_default='10', nullable=True),
        sa.Column('features', sa.Text(), server_default='{"basic": true, "advanced": false, "premium": false}', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)

    # Create organization_users table
    op.create_table(
        'organization_users',
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_primary', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('organization_id', 'user_id')
    )

    # Create subscription_plans table
    op.create_table(
        'subscription_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('stripe_price_id', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('interval', sa.String(length=20), server_default='month', nullable=True),
        sa.Column('max_users', sa.Integer(), server_default='5', nullable=True),
        sa.Column('max_events', sa.Integer(), server_default='10', nullable=True),
        sa.Column('features', sa.Text(), server_default='{"basic": true, "advanced": false, "premium": false}', nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscription_plans_id'), 'subscription_plans', ['id'], unique=False)

    # Create subscription_invoices table
    op.create_table(
        'subscription_invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('stripe_invoice_id', sa.String(length=255), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='pending', nullable=True),
        sa.Column('invoice_date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('paid_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscription_invoices_id'), 'subscription_invoices', ['id'], unique=False)

    # Add stripe_customer_id to users table
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))

    # Add organization_id to conversations table
    op.add_column('conversations', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'conversations', 'organizations', ['organization_id'], ['id'])

    # Add organization_id to events table
    op.add_column('events', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'events', 'organizations', ['organization_id'], ['id'])


def downgrade():
    # Remove foreign keys
    op.drop_constraint(None, 'events', type_='foreignkey')
    op.drop_constraint(None, 'conversations', type_='foreignkey')

    # Remove columns
    op.drop_column('events', 'organization_id')
    op.drop_column('conversations', 'organization_id')
    op.drop_column('users', 'stripe_customer_id')

    # Drop tables
    op.drop_index(op.f('ix_subscription_invoices_id'), table_name='subscription_invoices')
    op.drop_table('subscription_invoices')
    op.drop_index(op.f('ix_subscription_plans_id'), table_name='subscription_plans')
    op.drop_table('subscription_plans')
    op.drop_table('organization_users')
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')
