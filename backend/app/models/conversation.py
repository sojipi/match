"""
Conversation and session database models.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class SessionStatus(enum.Enum):
    """Conversation session status enumeration."""
    WAITING = "waiting"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    ERROR = "error"


class SessionType(enum.Enum):
    """Conversation session type enumeration."""
    MATCHMAKING = "matchmaking"
    SIMULATION = "simulation"
    SPEED_CHAT = "speed_chat"
    GUIDED_CONVERSATION = "guided_conversation"


class MessageType(enum.Enum):
    """Message type enumeration."""
    TEXT = "text"
    EMOTION = "emotion"
    ACTION = "action"
    SYSTEM_NOTIFICATION = "system_notification"
    FACILITATION = "facilitation"


class AgentType(enum.Enum):
    """Agent type enumeration."""
    USER_AVATAR = "user_avatar"
    MATCHMAKER_AGENT = "matchmaker_agent"
    SCENARIO_AGENT = "scenario_agent"
    SYSTEM = "system"


class ConversationSession(Base):
    """Conversation session between users or their AI avatars."""
    
    __tablename__ = "conversation_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Participants
    user1_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user2_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session configuration
    session_type = Column(String(50), default=SessionType.MATCHMAKING.value, nullable=False)
    status = Column(String(20), default=SessionStatus.WAITING.value, nullable=False)
    
    # Session metadata
    title = Column(String(200))
    description = Column(Text)
    scenario_id = Column(String(100))  # Reference to scenario if applicable
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Session settings
    max_duration_minutes = Column(Integer, default=60)
    allow_matchmaker_intervention = Column(Boolean, default=True)
    auto_generate_scenarios = Column(Boolean, default=False)
    
    # Real-time data
    current_turn = Column(String(50))  # Which user's turn it is
    turn_count = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    
    # Live session data
    viewer_count = Column(Integer, default=0)
    live_compatibility_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    
    # Results and analysis
    final_compatibility_score = Column(Float)
    compatibility_analysis = Column(JSON, default=dict)
    session_highlights = Column(JSON, default=list)
    user_feedback = Column(JSON, default=dict)
    
    # Status tracking
    is_live = Column(Boolean, default=False)
    is_recorded = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="conversation_sessions_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="conversation_sessions_as_user2")
    messages = relationship("ConversationMessage", back_populates="session", cascade="all, delete-orphan", order_by="ConversationMessage.timestamp")
    compatibility_reports = relationship("ConversationCompatibilityReport", back_populates="session", cascade="all, delete-orphan")


class ConversationMessage(Base):
    """Individual message in a conversation session."""
    
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message sender
    sender_id = Column(String(100), nullable=False)  # User ID or agent ID
    sender_type = Column(String(50), default=AgentType.USER_AVATAR.value, nullable=False)
    sender_name = Column(String(100), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default=MessageType.TEXT.value, nullable=False)
    
    # Message metadata
    turn_number = Column(Integer)
    response_time_seconds = Column(Float)  # Time taken to generate response
    confidence_score = Column(Float)  # AI confidence in response
    
    # Emotional and contextual data
    emotion_indicators = Column(JSON, default=list)  # Detected emotions
    sentiment_score = Column(Float)  # Message sentiment (-1 to 1)
    topic_tags = Column(JSON, default=list)  # Conversation topics
    
    # Compatibility impact
    compatibility_impact = Column(Float)  # Impact on compatibility score
    is_highlighted = Column(Boolean, default=False)  # Important moment
    highlight_reason = Column(String(200))  # Why this message is highlighted
    
    # Message status
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(String(200))
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    edited_at = Column(DateTime(timezone=True))
    
    # Relationships
    session = relationship("ConversationSession", back_populates="messages")


class ConversationCompatibilityReport(Base):
    """Compatibility analysis report for a conversation session."""
    
    __tablename__ = "conversation_compatibility_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Report metadata
    report_type = Column(String(50), default="conversation_analysis")  # Type of compatibility analysis
    analysis_version = Column(String(20), default="1.0")
    
    # Overall compatibility
    overall_score = Column(Float, nullable=False)  # 0.0 to 1.0
    confidence_level = Column(Float, default=0.8)  # Confidence in the analysis
    
    # Dimensional scores
    personality_compatibility = Column(Float)  # Big Five alignment
    values_alignment = Column(Float)  # Core values compatibility
    communication_style = Column(Float)  # Communication compatibility
    emotional_connection = Column(Float)  # Emotional resonance
    conflict_resolution = Column(Float)  # How they handle disagreements
    lifestyle_compatibility = Column(Float)  # Lifestyle and preferences
    
    # Detailed analysis
    strengths = Column(JSON, default=list)  # Compatibility strengths
    challenges = Column(JSON, default=list)  # Potential challenges
    recommendations = Column(JSON, default=list)  # Actionable recommendations
    
    # Conversation analysis
    conversation_quality = Column(Float)  # Quality of interaction
    engagement_level = Column(Float)  # How engaged both parties were
    topic_diversity = Column(Float)  # Range of topics covered
    emotional_depth = Column(Float)  # Depth of emotional sharing
    
    # Interaction patterns
    turn_balance = Column(Float)  # How balanced the conversation was
    response_times = Column(JSON, default=dict)  # Response time analysis
    conversation_flow = Column(Float)  # How naturally conversation flowed
    
    # Predictive insights
    relationship_potential = Column(Float)  # Predicted relationship success
    compatibility_trend = Column(String(20))  # "improving", "stable", "declining"
    key_insights = Column(JSON, default=list)  # Key compatibility insights
    
    # Report generation
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    generated_by = Column(String(50), default="ai_analysis")  # Who/what generated the report
    processing_time_seconds = Column(Float)
    
    # Report status
    is_final = Column(Boolean, default=False)  # Is this the final report
    is_shared = Column(Boolean, default=False)  # Has been shared with users
    user_feedback = Column(JSON, default=dict)  # User feedback on report accuracy
    
    # Relationships
    session = relationship("ConversationSession", back_populates="compatibility_reports")


class ScenarioTemplate(Base):
    """Template for relationship scenarios used in simulations."""
    
    __tablename__ = "scenario_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Scenario identification
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # "financial", "family", "lifestyle", etc.
    difficulty_level = Column(Integer, default=1)  # 1-5 difficulty scale
    
    # Scenario content
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    context = Column(Text)  # Background context
    
    # Scenario configuration
    estimated_duration_minutes = Column(Integer, default=15)
    participant_roles = Column(JSON, default=list)  # Roles for participants
    success_criteria = Column(JSON, default=list)  # What indicates success
    
    # Scenario prompts
    initial_prompt = Column(Text)  # How to start the scenario
    guiding_questions = Column(JSON, default=list)  # Questions to guide discussion
    escalation_prompts = Column(JSON, default=list)  # How to escalate if needed
    
    # Compatibility focus
    personality_dimensions = Column(JSON, default=list)  # Which traits this tests
    value_dimensions = Column(JSON, default=list)  # Which values this explores
    skill_dimensions = Column(JSON, default=list)  # Which skills this assesses
    
    # Cultural and demographic considerations
    cultural_adaptations = Column(JSON, default=dict)  # Cultural variations
    age_appropriateness = Column(String(50), default="all")  # Age range
    relationship_stage = Column(String(50), default="early")  # Relationship stage
    
    # Usage and performance
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # How often it leads to good insights
    user_rating = Column(Float, default=0.0)  # User satisfaction rating
    
    # Status
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=True)
    requires_moderation = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))  # Who created this scenario


class ConversationAnalytics(Base):
    """Analytics and metrics for conversation sessions."""
    
    __tablename__ = "conversation_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic metrics
    total_messages = Column(Integer, default=0)
    total_duration_seconds = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)
    
    # Engagement metrics
    user1_message_count = Column(Integer, default=0)
    user2_message_count = Column(Integer, default=0)
    message_balance_ratio = Column(Float, default=0.0)  # How balanced the conversation was
    
    # Content analysis
    unique_topics_count = Column(Integer, default=0)
    topic_transitions = Column(Integer, default=0)
    question_count = Column(Integer, default=0)
    emotional_expressions = Column(Integer, default=0)
    
    # Quality metrics
    conversation_depth_score = Column(Float, default=0.0)
    authenticity_score = Column(Float, default=0.0)
    natural_flow_score = Column(Float, default=0.0)
    
    # Compatibility indicators
    agreement_moments = Column(Integer, default=0)
    disagreement_moments = Column(Integer, default=0)
    shared_interests_discovered = Column(Integer, default=0)
    value_alignments_found = Column(Integer, default=0)
    
    # Real-time tracking
    peak_engagement_time = Column(DateTime(timezone=True))
    lowest_engagement_time = Column(DateTime(timezone=True))
    conversation_highlights = Column(JSON, default=list)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session = relationship("ConversationSession")