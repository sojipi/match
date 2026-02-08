"""Add avatar tables

Revision ID: 002
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_avatar_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ai_avatars table
    op.create_table('ai_avatars',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('personality_profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('avatar_version', sa.String(length=20), nullable=True),
        sa.Column('personality_traits', sa.JSON(), nullable=True),
        sa.Column('communication_patterns', sa.JSON(), nullable=True),
        sa.Column('response_style', sa.JSON(), nullable=True),
        sa.Column('memory_context', sa.JSON(), nullable=True),
        sa.Column('conversation_skills', sa.JSON(), nullable=True),
        sa.Column('emotional_range', sa.JSON(), nullable=True),
        sa.Column('cultural_context', sa.JSON(), nullable=True),
        sa.Column('completeness_score', sa.Float(), nullable=True),
        sa.Column('authenticity_score', sa.Float(), nullable=True),
        sa.Column('consistency_score', sa.Float(), nullable=True),
        sa.Column('training_iterations', sa.Integer(), nullable=True),
        sa.Column('last_training_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('performance_metrics', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.Column('improvement_areas', sa.JSON(), nullable=True),
        sa.Column('suggested_actions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['personality_profile_id'], ['personality_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_ai_avatars_user_id'), 'ai_avatars', ['user_id'], unique=False)

    # Create avatar_customizations table
    op.create_table('avatar_customizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('avatar_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customization_type', sa.String(length=50), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('original_value', sa.JSON(), nullable=True),
        sa.Column('custom_value', sa.JSON(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['avatar_id'], ['ai_avatars.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_avatar_customizations_avatar_id'), 'avatar_customizations', ['avatar_id'], unique=False)

    # Create avatar_training_sessions table
    op.create_table('avatar_training_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('avatar_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('training_type', sa.String(length=50), nullable=False),
        sa.Column('trigger_reason', sa.String(length=100), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('training_parameters', sa.JSON(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('performance_before', sa.JSON(), nullable=True),
        sa.Column('performance_after', sa.JSON(), nullable=True),
        sa.Column('improvements', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['avatar_id'], ['ai_avatars.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_avatar_training_sessions_avatar_id'), 'avatar_training_sessions', ['avatar_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_avatar_training_sessions_avatar_id'), table_name='avatar_training_sessions')
    op.drop_table('avatar_training_sessions')
    
    op.drop_index(op.f('ix_avatar_customizations_avatar_id'), table_name='avatar_customizations')
    op.drop_table('avatar_customizations')
    
    op.drop_index(op.f('ix_ai_avatars_user_id'), table_name='ai_avatars')
    op.drop_table('ai_avatars')