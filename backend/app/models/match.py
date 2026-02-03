"""
Match and compatibility database models.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, Float, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class MatchStatus(enum.Enum):
    """Match status enumeration."""
    PENDING = "pending"
    MUTUAL = "mutual"
    EXPIRED = "expired"
    BLOCKED = "blocked"


class InterestLevel(enum.Enum):
    """User interest level enumeration."""
    LIKE = "like"
    PASS = "pass"
    SUPER_LIKE = "super_like"


class MatchSessionStatus(enum.Enum):
    """Match session status enumeration."""
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Match(Base):
    """Match relationship between two users."""
    
    __tablename__ = "matches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user1_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user2_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Match status
    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING)
    user1_interest = Column(Enum(InterestLevel))
    user2_interest = Column(Enum(InterestLevel))
    
    # Compatibility data
    compatibility_score = Column(Float)
    
    # Interaction tracking
    conversation_count = Column(Integer, default=0)
    simulation_count = Column(Integer, default=0)
    last_interaction = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="matches_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="matches_as_user2")
    compatibility_reports = relationship("CompatibilityReport", back_populates="match", cascade="all, delete-orphan")
    sessions = relationship("MatchSession", back_populates="match", cascade="all, delete-orphan")


class MatchSession(Base):
    """Session for a specific match between two users."""
    
    __tablename__ = "match_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    user1_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user2_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session details
    session_type = Column(String(50), default="live_matching")  # live_matching, simulation, speed_chat
    status = Column(Enum(MatchSessionStatus), default=MatchSessionStatus.SCHEDULED)
    
    # Session metadata
    title = Column(String(200))
    description = Column(Text)
    
    # Timing
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    
    # Session configuration
    max_duration_minutes = Column(Integer, default=30)
    is_public = Column(Boolean, default=False)
    allow_observers = Column(Boolean, default=False)
    
    # Live session data
    current_phase = Column(String(50))  # introduction, conversation, scenario, wrap_up
    observer_count = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)
    
    # Results
    final_compatibility_score = Column(Float)
    session_highlights = Column(JSON, default=list)
    user_feedback = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    match = relationship("Match", back_populates="sessions")
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="sessions_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="sessions_as_user2")
    compatibility_report = relationship("CompatibilityReport", back_populates="session", uselist=False)


class CompatibilityReport(Base):
    """Compatibility assessment report."""
    
    __tablename__ = "compatibility_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("match_sessions.id"))
    
    # Overall compatibility
    overall_score = Column(Float, nullable=False)
    
    # Dimension scores
    personality_compatibility = Column(Float)
    communication_compatibility = Column(Float)
    values_compatibility = Column(Float)
    lifestyle_compatibility = Column(Float)
    
    # Analysis results
    strengths = Column(JSON, default=list)
    challenges = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    
    # Detailed analysis
    interaction_analysis = Column(JSON, default=dict)
    scenario_results = Column(JSON, default=list)
    
    # Metadata
    analysis_version = Column(String(20))
    confidence_score = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    match = relationship("Match", back_populates="compatibility_reports")
    session = relationship("MatchSession", back_populates="compatibility_report")