"""Add conversation models for AI agent system

Revision ID: 004_add_conversation_models
Revises: 003_update_notification_schema
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_conversation_models'
down_revision = '003_update_notification_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Create conversation_sessions table
    op.create_table('conversation_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user1_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user2_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scenario_id', sa.String(length=100), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('max_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('allow_matchmaker_intervention', sa.Boolean(), nullable=True),
        sa.Column('auto_generate_scenarios', sa.Boolean(), nullable=True),
        sa.Column('current_turn', sa.String(length=50), nullable=True),
        sa.Column('turn_count', sa.Integer(), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True),
        sa.Column('viewer_count', sa.Integer(), nullable=True),
        sa.Column('live_compatibility_score', sa.Float(), nullable=True),
        sa.Column('engagement_score', sa.Float(), nullable=True),
        sa.Column('final_compatibility_score', sa.Float(), nullable=True),
        sa.Column('compatibility_analysis', sa.JSON(), nullable=True),
        sa.Column('session_highlights', sa.JSON(), nullable=True),
        sa.Column('user_feedback', sa.JSON(), nullable=True),
        sa.Column('is_live', sa.Boolean(), nullable=True),
        sa.Column('is_recorded', sa.Boolean(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_sessions_user1_id'), 'conversation_sessions', ['user1_id'], unique=False)
    op.create_index(op.f('ix_conversation_sessions_user2_id'), 'conversation_sessions', ['user2_id'], unique=False)

    # Create conversation_messages table
    op.create_table('conversation_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sender_id', sa.String(length=100), nullable=False),
        sa.Column('sender_type', sa.String(length=50), nullable=False),
        sa.Column('sender_name', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(length=50), nullable=False),
        sa.Column('turn_number', sa.Integer(), nullable=True),
        sa.Column('response_time_seconds', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('emotion_indicators', sa.JSON(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('topic_tags', sa.JSON(), nullable=True),
        sa.Column('compatibility_impact', sa.Float(), nullable=True),
        sa.Column('is_highlighted', sa.Boolean(), nullable=True),
        sa.Column('highlight_reason', sa.String(length=200), nullable=True),
        sa.Column('is_edited', sa.Boolean(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('is_flagged', sa.Boolean(), nullable=True),
        sa.Column('flag_reason', sa.String(length=200), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['conversation_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_messages_session_id'), 'conversation_messages', ['session_id'], unique=False)

    # Create conversation_compatibility_reports table
    op.create_table('conversation_compatibility_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=True),
        sa.Column('analysis_version', sa.String(length=20), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('personality_compatibility', sa.Float(), nullable=True),
        sa.Column('values_alignment', sa.Float(), nullable=True),
        sa.Column('communication_style', sa.Float(), nullable=True),
        sa.Column('emotional_connection', sa.Float(), nullable=True),
        sa.Column('conflict_resolution', sa.Float(), nullable=True),
        sa.Column('lifestyle_compatibility', sa.Float(), nullable=True),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('challenges', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('conversation_quality', sa.Float(), nullable=True),
        sa.Column('engagement_level', sa.Float(), nullable=True),
        sa.Column('topic_diversity', sa.Float(), nullable=True),
        sa.Column('emotional_depth', sa.Float(), nullable=True),
        sa.Column('turn_balance', sa.Float(), nullable=True),
        sa.Column('response_times', sa.JSON(), nullable=True),
        sa.Column('conversation_flow', sa.Float(), nullable=True),
        sa.Column('relationship_potential', sa.Float(), nullable=True),
        sa.Column('compatibility_trend', sa.String(length=20), nullable=True),
        sa.Column('key_insights', sa.JSON(), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('generated_by', sa.String(length=50), nullable=True),
        sa.Column('processing_time_seconds', sa.Float(), nullable=True),
        sa.Column('is_final', sa.Boolean(), nullable=True),
        sa.Column('is_shared', sa.Boolean(), nullable=True),
        sa.Column('user_feedback', sa.JSON(), nullable=True),
        sa.Column('conversation_highlights', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['conversation_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create scenario_templates table
    op.create_table('scenario_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('difficulty_level', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('participant_roles', sa.JSON(), nullable=True),
        sa.Column('success_criteria', sa.JSON(), nullable=True),
        sa.Column('initial_prompt', sa.Text(), nullable=True),
        sa.Column('guiding_questions', sa.JSON(), nullable=True),
        sa.Column('escalation_prompts', sa.JSON(), nullable=True),
        sa.Column('personality_dimensions', sa.JSON(), nullable=True),
        sa.Column('value_dimensions', sa.JSON(), nullable=True),
        sa.Column('skill_dimensions', sa.JSON(), nullable=True),
        sa.Column('cultural_adaptations', sa.JSON(), nullable=True),
        sa.Column('age_appropriateness', sa.String(length=50), nullable=True),
        sa.Column('relationship_stage', sa.String(length=50), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('user_rating', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('requires_moderation', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create conversation_analytics table
    op.create_table('conversation_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_messages', sa.Integer(), nullable=True),
        sa.Column('total_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('average_response_time', sa.Float(), nullable=True),
        sa.Column('user1_message_count', sa.Integer(), nullable=True),
        sa.Column('user2_message_count', sa.Integer(), nullable=True),
        sa.Column('message_balance_ratio', sa.Float(), nullable=True),
        sa.Column('unique_topics_count', sa.Integer(), nullable=True),
        sa.Column('topic_transitions', sa.Integer(), nullable=True),
        sa.Column('question_count', sa.Integer(), nullable=True),
        sa.Column('emotional_expressions', sa.Integer(), nullable=True),
        sa.Column('conversation_depth_score', sa.Float(), nullable=True),
        sa.Column('authenticity_score', sa.Float(), nullable=True),
        sa.Column('natural_flow_score', sa.Float(), nullable=True),
        sa.Column('agreement_moments', sa.Integer(), nullable=True),
        sa.Column('disagreement_moments', sa.Integer(), nullable=True),
        sa.Column('shared_interests_discovered', sa.Integer(), nullable=True),
        sa.Column('value_alignments_found', sa.Integer(), nullable=True),
        sa.Column('peak_engagement_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('lowest_engagement_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('conversation_highlights', sa.JSON(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['conversation_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Set default values for new columns
    op.execute("UPDATE conversation_sessions SET session_type = 'matchmaking' WHERE session_type IS NULL")
    op.execute("UPDATE conversation_sessions SET status = 'waiting' WHERE status IS NULL")
    op.execute("UPDATE conversation_sessions SET max_duration_minutes = 60 WHERE max_duration_minutes IS NULL")
    op.execute("UPDATE conversation_sessions SET allow_matchmaker_intervention = true WHERE allow_matchmaker_intervention IS NULL")
    op.execute("UPDATE conversation_sessions SET auto_generate_scenarios = false WHERE auto_generate_scenarios IS NULL")
    op.execute("UPDATE conversation_sessions SET turn_count = 0 WHERE turn_count IS NULL")
    op.execute("UPDATE conversation_sessions SET message_count = 0 WHERE message_count IS NULL")
    op.execute("UPDATE conversation_sessions SET viewer_count = 0 WHERE viewer_count IS NULL")
    op.execute("UPDATE conversation_sessions SET live_compatibility_score = 0.0 WHERE live_compatibility_score IS NULL")
    op.execute("UPDATE conversation_sessions SET engagement_score = 0.0 WHERE engagement_score IS NULL")
    op.execute("UPDATE conversation_sessions SET is_live = false WHERE is_live IS NULL")
    op.execute("UPDATE conversation_sessions SET is_recorded = true WHERE is_recorded IS NULL")
    op.execute("UPDATE conversation_sessions SET is_public = false WHERE is_public IS NULL")

    op.execute("UPDATE conversation_messages SET message_type = 'text' WHERE message_type IS NULL")
    op.execute("UPDATE conversation_messages SET is_highlighted = false WHERE is_highlighted IS NULL")
    op.execute("UPDATE conversation_messages SET is_edited = false WHERE is_edited IS NULL")
    op.execute("UPDATE conversation_messages SET is_deleted = false WHERE is_deleted IS NULL")
    op.execute("UPDATE conversation_messages SET is_flagged = false WHERE is_flagged IS NULL")

    op.execute("UPDATE conversation_compatibility_reports SET report_type = 'conversation_analysis' WHERE report_type IS NULL")
    op.execute("UPDATE conversation_compatibility_reports SET analysis_version = '1.0' WHERE analysis_version IS NULL")
    op.execute("UPDATE conversation_compatibility_reports SET confidence_level = 0.8 WHERE confidence_level IS NULL")
    op.execute("UPDATE conversation_compatibility_reports SET generated_by = 'ai_analysis' WHERE generated_by IS NULL")
    op.execute("UPDATE conversation_compatibility_reports SET is_final = false WHERE is_final IS NULL")
    op.execute("UPDATE conversation_compatibility_reports SET is_shared = false WHERE is_shared IS NULL")

    op.execute("UPDATE scenario_templates SET difficulty_level = 1 WHERE difficulty_level IS NULL")
    op.execute("UPDATE scenario_templates SET estimated_duration_minutes = 15 WHERE estimated_duration_minutes IS NULL")
    op.execute("UPDATE scenario_templates SET age_appropriateness = 'all' WHERE age_appropriateness IS NULL")
    op.execute("UPDATE scenario_templates SET relationship_stage = 'early' WHERE relationship_stage IS NULL")
    op.execute("UPDATE scenario_templates SET usage_count = 0 WHERE usage_count IS NULL")
    op.execute("UPDATE scenario_templates SET success_rate = 0.0 WHERE success_rate IS NULL")
    op.execute("UPDATE scenario_templates SET user_rating = 0.0 WHERE user_rating IS NULL")
    op.execute("UPDATE scenario_templates SET is_active = true WHERE is_active IS NULL")
    op.execute("UPDATE scenario_templates SET is_approved = true WHERE is_approved IS NULL")
    op.execute("UPDATE scenario_templates SET requires_moderation = false WHERE requires_moderation IS NULL")

    op.execute("UPDATE conversation_analytics SET total_messages = 0 WHERE total_messages IS NULL")
    op.execute("UPDATE conversation_analytics SET total_duration_seconds = 0 WHERE total_duration_seconds IS NULL")
    op.execute("UPDATE conversation_analytics SET average_response_time = 0.0 WHERE average_response_time IS NULL")
    op.execute("UPDATE conversation_analytics SET user1_message_count = 0 WHERE user1_message_count IS NULL")
    op.execute("UPDATE conversation_analytics SET user2_message_count = 0 WHERE user2_message_count IS NULL")
    op.execute("UPDATE conversation_analytics SET message_balance_ratio = 0.0 WHERE message_balance_ratio IS NULL")
    op.execute("UPDATE conversation_analytics SET unique_topics_count = 0 WHERE unique_topics_count IS NULL")
    op.execute("UPDATE conversation_analytics SET topic_transitions = 0 WHERE topic_transitions IS NULL")
    op.execute("UPDATE conversation_analytics SET question_count = 0 WHERE question_count IS NULL")
    op.execute("UPDATE conversation_analytics SET emotional_expressions = 0 WHERE emotional_expressions IS NULL")
    op.execute("UPDATE conversation_analytics SET conversation_depth_score = 0.0 WHERE conversation_depth_score IS NULL")
    op.execute("UPDATE conversation_analytics SET authenticity_score = 0.0 WHERE authenticity_score IS NULL")
    op.execute("UPDATE conversation_analytics SET natural_flow_score = 0.0 WHERE natural_flow_score IS NULL")
    op.execute("UPDATE conversation_analytics SET agreement_moments = 0 WHERE agreement_moments IS NULL")
    op.execute("UPDATE conversation_analytics SET disagreement_moments = 0 WHERE disagreement_moments IS NULL")
    op.execute("UPDATE conversation_analytics SET shared_interests_discovered = 0 WHERE shared_interests_discovered IS NULL")
    op.execute("UPDATE conversation_analytics SET value_alignments_found = 0 WHERE value_alignments_found IS NULL")


def downgrade():
    # Drop tables in reverse order
    op.drop_table('conversation_analytics')
    op.drop_table('scenario_templates')
    op.drop_table('conversation_compatibility_reports')
    op.drop_index(op.f('ix_conversation_messages_session_id'), table_name='conversation_messages')
    op.drop_table('conversation_messages')
    op.drop_index(op.f('ix_conversation_sessions_user2_id'), table_name='conversation_sessions')
    op.drop_index(op.f('ix_conversation_sessions_user1_id'), table_name='conversation_sessions')
    op.drop_table('conversation_sessions')