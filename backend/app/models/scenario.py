"""
Scenario and simulation database models.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class ScenarioCategory(enum.Enum):
    """Scenario category enumeration."""
    FINANCIAL = "financial"
    FAMILY = "family"
    LIFESTYLE = "lifestyle"
    CAREER = "career"
    SOCIAL = "social"
    CONFLICT_RESOLUTION = "conflict_resolution"
    VALUES = "values"
    COMMUNICATION = "communication"
    FUTURE_PLANNING = "future_planning"
    DAILY_LIFE = "daily_life"


class ScenarioDifficulty(enum.Enum):
    """Scenario difficulty level enumeration."""
    EASY = 1
    MODERATE = 2
    CHALLENGING = 3
    DIFFICULT = 4
    EXPERT = 5


class SimulationStatus(enum.Enum):
    """Simulation session status enumeration."""
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class ScenarioTemplate(Base):
    """Template for relationship scenarios used in simulations."""
    
    __tablename__ = "scenario_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Scenario identification
    name = Column(String(100), nullable=False, index=True)
    category = Column(Enum(ScenarioCategory), nullable=False, index=True)
    difficulty_level = Column(Enum(ScenarioDifficulty), default=ScenarioDifficulty.MODERATE)
    
    # Scenario content
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    context = Column(Text)  # Background context
    setup_prompt = Column(Text, nullable=False)  # How to present the scenario
    
    # Scenario configuration
    estimated_duration_minutes = Column(Integer, default=15)
    participant_roles = Column(JSON, default=list)  # Roles for participants
    success_criteria = Column(JSON, default=list)  # What indicates success
    
    # Scenario prompts and guidance
    initial_prompt = Column(Text)  # How to start the scenario
    guiding_questions = Column(JSON, default=list)  # Questions to guide discussion
    escalation_prompts = Column(JSON, default=list)  # How to escalate if needed
    resolution_prompts = Column(JSON, default=list)  # How to guide toward resolution
    
    # Compatibility focus areas
    personality_dimensions = Column(JSON, default=list)  # Which traits this tests
    value_dimensions = Column(JSON, default=list)  # Which values this explores
    skill_dimensions = Column(JSON, default=list)  # Which skills this assesses
    
    # Cultural and demographic considerations
    cultural_adaptations = Column(JSON, default=dict)  # Cultural variations
    age_appropriateness = Column(String(50), default="all")  # Age range
    relationship_stage = Column(String(50), default="early")  # Relationship stage
    language_variants = Column(JSON, default=dict)  # Language-specific versions
    
    # Usage and performance metrics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # How often it leads to good insights
    user_rating = Column(Float, default=0.0)  # User satisfaction rating
    completion_rate = Column(Float, default=0.0)  # How often users complete it
    
    # Content management
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=True)
    requires_moderation = Column(Boolean, default=False)
    content_warnings = Column(JSON, default=list)  # Content warnings if needed
    
    # Metadata
    tags = Column(JSON, default=list)  # Searchable tags
    keywords = Column(JSON, default=list)  # Keywords for matching
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))  # Who created this scenario
    
    # Relationships
    simulations = relationship("SimulationSession", back_populates="scenario_template")
    results = relationship("ScenarioResult", back_populates="scenario_template")


class SimulationSession(Base):
    """Simulation session between users using a scenario."""
    
    __tablename__ = "simulation_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Session participants
    user1_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user2_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), index=True)
    
    # Scenario information
    scenario_template_id = Column(UUID(as_uuid=True), ForeignKey("scenario_templates.id"), nullable=False, index=True)
    scenario_instance_data = Column(JSON, default=dict)  # Customized scenario data
    
    # Session configuration
    session_title = Column(String(200))
    session_description = Column(Text)
    status = Column(Enum(SimulationStatus), default=SimulationStatus.SCHEDULED)
    
    # Timing
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    max_duration_minutes = Column(Integer, default=30)
    
    # Session settings
    is_public = Column(Boolean, default=False)
    allow_observers = Column(Boolean, default=False)
    auto_guidance_enabled = Column(Boolean, default=True)
    cultural_adaptation = Column(String(50))  # Cultural context applied
    language = Column(String(10), default="en")
    
    # Live session data
    current_phase = Column(String(50))  # setup, scenario_presentation, interaction, resolution, analysis
    phase_start_time = Column(DateTime(timezone=True))
    observer_count = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)
    
    # Interaction tracking
    message_count = Column(Integer, default=0)
    turn_count = Column(Integer, default=0)
    guidance_interventions = Column(Integer, default=0)
    user_reactions = Column(JSON, default=list)
    
    # Results and analysis
    scenario_completion_score = Column(Float)  # How well they completed the scenario
    collaboration_score = Column(Float)  # How well they worked together
    conflict_resolution_score = Column(Float)  # How they handled conflicts
    value_alignment_score = Column(Float)  # Value alignment discovered
    communication_effectiveness = Column(Float)  # Communication quality
    
    # Session outcomes
    session_highlights = Column(JSON, default=list)
    key_insights = Column(JSON, default=list)
    user_feedback = Column(JSON, default=dict)
    moderator_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="simulation_sessions_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="simulation_sessions_as_user2")
    match = relationship("Match", back_populates="simulation_sessions")
    scenario_template = relationship("ScenarioTemplate", back_populates="simulations")
    messages = relationship("SimulationMessage", back_populates="session", cascade="all, delete-orphan")
    result = relationship("ScenarioResult", back_populates="simulation_session", uselist=False)


class SimulationMessage(Base):
    """Message in a simulation session."""
    
    __tablename__ = "simulation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("simulation_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message sender
    sender_id = Column(String(100), nullable=False)  # User ID or agent ID
    sender_type = Column(String(50), nullable=False)  # user_avatar, scenario_agent, system
    sender_name = Column(String(100), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, action, system, guidance
    
    # Scenario context
    scenario_phase = Column(String(50))  # Which phase of scenario this relates to
    turn_number = Column(Integer)
    response_time_seconds = Column(Float)
    
    # Analysis data
    emotion_indicators = Column(JSON, default=list)
    sentiment_score = Column(Float)
    topic_tags = Column(JSON, default=list)
    scenario_relevance = Column(Float)  # How relevant to the scenario
    
    # Compatibility impact
    collaboration_impact = Column(Float)  # Impact on collaboration score
    conflict_resolution_impact = Column(Float)  # Impact on conflict resolution
    value_alignment_impact = Column(Float)  # Impact on value alignment
    is_highlighted = Column(Boolean, default=False)
    highlight_reason = Column(String(200))
    
    # Message status
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    edited_at = Column(DateTime(timezone=True))
    
    # Relationships
    session = relationship("SimulationSession", back_populates="messages")


class ScenarioResult(Base):
    """Results and analysis from a completed scenario simulation."""
    
    __tablename__ = "scenario_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_session_id = Column(UUID(as_uuid=True), ForeignKey("simulation_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_template_id = Column(UUID(as_uuid=True), ForeignKey("scenario_templates.id"), nullable=False, index=True)
    
    # Overall results
    overall_success_score = Column(Float, nullable=False)  # 0.0 to 1.0
    scenario_completion_rate = Column(Float)  # How much of scenario was completed
    
    # Dimensional scores
    collaboration_score = Column(Float)  # How well they worked together
    communication_score = Column(Float)  # Communication effectiveness
    conflict_resolution_score = Column(Float)  # Conflict handling
    value_alignment_score = Column(Float)  # Value compatibility
    problem_solving_score = Column(Float)  # Problem-solving approach
    empathy_score = Column(Float)  # Empathy and understanding
    
    # Scenario-specific results
    scenario_objectives_met = Column(JSON, default=list)  # Which objectives were achieved
    key_decisions_made = Column(JSON, default=list)  # Important decisions during scenario
    conflict_points = Column(JSON, default=list)  # Where conflicts arose
    resolution_strategies = Column(JSON, default=list)  # How conflicts were resolved
    
    # Insights and analysis
    strengths_identified = Column(JSON, default=list)  # Relationship strengths
    challenges_identified = Column(JSON, default=list)  # Areas for improvement
    compatibility_insights = Column(JSON, default=list)  # Compatibility discoveries
    behavioral_patterns = Column(JSON, default=list)  # Observed behavior patterns
    
    # Recommendations
    relationship_recommendations = Column(JSON, default=list)  # Actionable advice
    future_scenario_suggestions = Column(JSON, default=list)  # Suggested next scenarios
    skill_development_areas = Column(JSON, default=list)  # Areas to work on
    
    # Analysis metadata
    analysis_confidence = Column(Float, default=0.8)  # Confidence in analysis
    analysis_version = Column(String(20), default="1.0")
    processing_time_seconds = Column(Float)
    
    # User feedback on results
    user1_rating = Column(Float)  # User 1's rating of the analysis
    user2_rating = Column(Float)  # User 2's rating of the analysis
    user1_feedback = Column(Text)  # User 1's feedback
    user2_feedback = Column(Text)  # User 2's feedback
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    simulation_session = relationship("SimulationSession", back_populates="result")
    scenario_template = relationship("ScenarioTemplate", back_populates="results")


class ScenarioLibrary(Base):
    """Curated collections of scenarios for different purposes."""
    
    __tablename__ = "scenario_libraries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Library information
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # beginner, advanced, cultural, etc.
    
    # Library configuration
    scenario_ids = Column(JSON, default=list)  # List of scenario template IDs
    recommended_order = Column(JSON, default=list)  # Suggested order for scenarios
    prerequisites = Column(JSON, default=list)  # Required scenarios before this library
    
    # Target audience
    target_demographics = Column(JSON, default=dict)  # Age, culture, relationship stage
    difficulty_range = Column(JSON, default=list)  # Min and max difficulty levels
    estimated_total_duration = Column(Integer)  # Total time for all scenarios
    
    # Usage and performance
    usage_count = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    user_satisfaction = Column(Float, default=0.0)
    
    # Library status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    requires_subscription = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))