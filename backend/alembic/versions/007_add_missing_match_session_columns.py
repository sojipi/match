"""Add missing columns to match_sessions table

Revision ID: 007
Revises: 006
Create Date: 2026-02-08 17:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Check which columns exist and add missing ones
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = {col['name'] for col in inspector.get_columns('match_sessions')}

    # First, rename columns if they exist with different names
    if 'start_time' in existing_columns and 'started_at' not in existing_columns:
        op.alter_column('match_sessions', 'start_time', new_column_name='started_at')
        existing_columns.remove('start_time')
        existing_columns.add('started_at')

    if 'end_time' in existing_columns and 'ended_at' not in existing_columns:
        op.alter_column('match_sessions', 'end_time', new_column_name='ended_at')
        existing_columns.remove('end_time')
        existing_columns.add('ended_at')

    # Now add missing columns if they don't exist
    if 'title' not in existing_columns:
        op.add_column('match_sessions', sa.Column('title', sa.String(length=200), nullable=True))

    if 'description' not in existing_columns:
        op.add_column('match_sessions', sa.Column('description', sa.Text(), nullable=True))

    if 'scheduled_at' not in existing_columns:
        op.add_column('match_sessions', sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True))

    if 'started_at' not in existing_columns:
        op.add_column('match_sessions', sa.Column('started_at', sa.DateTime(timezone=True), nullable=True))

    if 'ended_at' not in existing_columns:
        op.add_column('match_sessions', sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True))

    if 'max_duration_minutes' not in existing_columns:
        op.add_column('match_sessions', sa.Column('max_duration_minutes', sa.Integer(), nullable=True, server_default='30'))

    if 'is_public' not in existing_columns:
        op.add_column('match_sessions', sa.Column('is_public', sa.Boolean(), nullable=True, server_default='false'))

    if 'allow_observers' not in existing_columns:
        op.add_column('match_sessions', sa.Column('allow_observers', sa.Boolean(), nullable=True, server_default='false'))

    if 'current_phase' not in existing_columns:
        op.add_column('match_sessions', sa.Column('current_phase', sa.String(length=50), nullable=True))

    if 'observer_count' not in existing_columns:
        op.add_column('match_sessions', sa.Column('observer_count', sa.Integer(), nullable=True, server_default='0'))

    if 'engagement_score' not in existing_columns:
        op.add_column('match_sessions', sa.Column('engagement_score', sa.Float(), nullable=True, server_default='0.0'))

    if 'session_highlights' not in existing_columns:
        op.add_column('match_sessions', sa.Column('session_highlights', sa.JSON(), nullable=True))

    if 'user_feedback' not in existing_columns:
        op.add_column('match_sessions', sa.Column('user_feedback', sa.JSON(), nullable=True))


def downgrade():
    # Remove added columns
    op.drop_column('match_sessions', 'user_feedback')
    op.drop_column('match_sessions', 'session_highlights')
    op.drop_column('match_sessions', 'engagement_score')
    op.drop_column('match_sessions', 'observer_count')
    op.drop_column('match_sessions', 'current_phase')
    op.drop_column('match_sessions', 'allow_observers')
    op.drop_column('match_sessions', 'is_public')
    op.drop_column('match_sessions', 'max_duration_minutes')
    op.drop_column('match_sessions', 'ended_at')
    op.drop_column('match_sessions', 'started_at')
    op.drop_column('match_sessions', 'scheduled_at')
    op.drop_column('match_sessions', 'description')
    op.drop_column('match_sessions', 'title')
