"""Update notification schema

Revision ID: 003
Revises: 002
Create Date: 2026-02-03 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_update_notification_schema'
down_revision = '002_add_avatar_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to notifications table if they don't exist
    # Using batch operations to handle potential existing columns gracefully

    # Check if columns exist and add them if they don't
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('notifications')]

    if 'data' not in existing_columns:
        op.add_column('notifications', sa.Column('data', sa.JSON(), nullable=True, server_default='{}'))

    if 'action_url' not in existing_columns:
        op.add_column('notifications', sa.Column('action_url', sa.String(length=500), nullable=True))

    if 'is_delivered' not in existing_columns:
        op.add_column('notifications', sa.Column('is_delivered', sa.Boolean(), nullable=True, server_default='false'))

    if 'delivery_channels' not in existing_columns:
        op.add_column('notifications', sa.Column('delivery_channels', sa.JSON(), nullable=True, server_default='[]'))

    if 'delivered_at' not in existing_columns:
        op.add_column('notifications', sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True))

    if 'expires_at' not in existing_columns:
        op.add_column('notifications', sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove the columns added in upgrade
    op.drop_column('notifications', 'expires_at')
    op.drop_column('notifications', 'delivered_at')
    op.drop_column('notifications', 'delivery_channels')
    op.drop_column('notifications', 'is_delivered')
    op.drop_column('notifications', 'action_url')
    op.drop_column('notifications', 'data')
