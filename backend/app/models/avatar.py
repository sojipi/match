"""
AI Avatar database models.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class AvatarStatus(enum.Enum):
    """Avatar status enumeration."""
    CREATING = "creating"
    ACTIVE = "active"
    TRAINING = "training"
    INACTIVE = "inactive"
    ERROR = "error"


class AIAvatar(Base):
    """AI Avatar model representing a user's AI personality."""
    
    __tablename__ = "ai_avatars"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    personality_profile_id = Column(UUID(as_uuid=True), ForeignKey("personality_profiles.id", ondelete="CASCADE"), nullable=False)
    
    # Avatar identity
    name = Column(String(100), nullable=False)
    description = Column(Text)
    avatar_version = Column(String(20), default="1.0")
    
    # Avatar configuration
    personality_traits = Column(JSON, default=dict)  # Processed personality data for AI
    communication_patterns = Column(JSON, default=dict)  # How the avatar communicates
    response_style = Column(JSON, default=dict)  # Response patterns and preferences
    memory_context = Column(JSON, default=dict)  # Context for memory system
    
    # Avatar capabilities
    conversation_skills = Column(JSON, default=dict)  # Conversation abilities
    emotional_range = Column(JSON, default=dict)  # Emotional expression capabilities
    cultural_context = Column(JSON, default=dict)  # Cultural adaptation settings
    
    # Avatar quality metrics
    completeness_score = Column(Float, default=0.0)  # How complete the avatar is (0-1)
    authenticity_score = Column(Float, default=0.0)  # How authentic responses are (0-1)
    consistency_score = Column(Float, default=0.0)  # How consistent personality is (0-1)
    
    # Training and performance
    training_iterations = Column(Integer, default=0)
    last_training_date = Column(DateTime(timezone=True))
    performance_metrics = Column(JSON, default=dict)
    
    # Status and lifecycle
    status = Column(String(20), default=AvatarStatus.CREATING.value)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True))
    
    # Improvement suggestions
    improvement_areas = Column(JSON, default=list)  # Areas needing improvement
    suggested_actions = Column(JSON, default=list)  # Specific improvement actions
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ai_avatar")
    personality_profile = relationship("PersonalityProfile", back_populates="ai_avatar")
    customizations = relationship("AvatarCustomization", back_populates="avatar", cascade="all, delete-orphan")
    training_sessions = relationship("AvatarTrainingSession", back_populates="avatar", cascade="all, delete-orphan")


class AvatarCustomization(Base):
    """User customizations to their AI avatar."""
    
    __tablename__ = "avatar_customizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    avatar_id = Column(UUID(as_uuid=True), ForeignKey("ai_avatars.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Customization details
    customization_type = Column(String(50), nullable=False)  # "personality_adjustment", "communication_style", etc.
    field_name = Column(String(100), nullable=False)  # Specific field being customized
    original_value = Column(JSON)  # Original AI-generated value
    custom_value = Column(JSON)  # User's custom value
    
    # Customization metadata
    reason = Column(Text)  # Why the user made this change
    confidence = Column(Float, default=1.0)  # User's confidence in this change (0-1)
    impact_score = Column(Float)  # Estimated impact on avatar behavior
    
    # Status
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=True)  # For future moderation
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    avatar = relationship("AIAvatar", back_populates="customizations")


class AvatarTrainingSession(Base):
    """Training session for avatar improvement."""
    
    __tablename__ = "avatar_training_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    avatar_id = Column(UUID(as_uuid=True), ForeignKey("ai_avatars.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Training details
    training_type = Column(String(50), nullable=False)  # "initial", "personality_update", "performance_improvement"
    trigger_reason = Column(String(100))  # What triggered this training
    
    # Training data
    input_data = Column(JSON, default=dict)  # Data used for training
    training_parameters = Column(JSON, default=dict)  # Training configuration
    
    # Results
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    performance_before = Column(JSON, default=dict)
    performance_after = Column(JSON, default=dict)
    improvements = Column(JSON, default=list)
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Relationships
    avatar = relationship("AIAvatar", back_populates="training_sessions")