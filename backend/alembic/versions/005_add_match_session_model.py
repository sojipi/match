"""Add MatchSession model

Revision ID: 005_add_match_session_model
Revises: 004_add_conversation_models
Create Date: 2024-01-01 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_match_session_model'
down_revision = '004_add_conversation_models'
branch_labels = None
depends_on = None


def upgrade():
    # Create match_sessions table
    op.create_table('match_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user1_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user2_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.Enum('SCHEDULED', 'ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED', name='matchsessionstatus'), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('max_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('allow_observers', sa.Boolean(), nullable=True),
        sa.Column('current_phase', sa.String(length=50), nullable=True),
        sa.Column('observer_count', sa.Integer(), nullable=True),
        sa.Column('engagement_score', sa.Float(), nullable=True),
        sa.Column('final_compatibility_score', sa.Float(), nullable=True),
        sa.Column('session_highlights', sa.JSON(), nullable=True),
        sa.Column('user_feedback', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_match_sessions_match_id'), 'match_sessions', ['match_id'], unique=False)
    op.create_index(op.f('ix_match_sessions_user1_id'), 'match_sessions', ['user1_id'], unique=False)
    op.create_index(op.f('ix_match_sessions_user2_id'), 'match_sessions', ['user2_id'], unique=False)

    # Set default values for new columns
    op.execute("UPDATE match_sessions SET session_type = 'live_matching' WHERE session_type IS NULL")
    op.execute("UPDATE match_sessions SET status = 'SCHEDULED' WHERE status IS NULL")
    op.execute("UPDATE match_sessions SET max_duration_minutes = 30 WHERE max_duration_minutes IS NULL")
    op.execute("UPDATE match_sessions SET is_public = false WHERE is_public IS NULL")
    op.execute("UPDATE match_sessions SET allow_observers = false WHERE allow_observers IS NULL")
    op.execute("UPDATE match_sessions SET observer_count = 0 WHERE observer_count IS NULL")
    op.execute("UPDATE match_sessions SET engagement_score = 0.0 WHERE engagement_score IS NULL")


def downgrade():
    # Drop indexes and table
    op.drop_index(op.f('ix_match_sessions_user2_id'), table_name='match_sessions')
    op.drop_index(op.f('ix_match_sessions_user1_id'), table_name='match_sessions')
    op.drop_index(op.f('ix_match_sessions_match_id'), table_name='match_sessions')
    op.drop_table('match_sessions')
    
    # Drop the enum type
    op.execute('DROP TYPE matchsessionstatus')