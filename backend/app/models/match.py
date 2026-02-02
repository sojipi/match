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
    compatibility_report_id = Column(UUID(as_uuid=True), ForeignKey("compatibility_reports.id"))
    
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
    compatibility_report = relationship("CompatibilityReport", back_populates="match")
    sessions = relationship("MatchSession", back_populates="match", cascade="all, delete-orphan")


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
    match = relationship("Match", back_populates="compatibility_report")
    session = relationship("MatchSession", back_populates="compatibility_report")