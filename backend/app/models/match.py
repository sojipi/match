"""
Match and compatibility database models.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
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
    user1_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user2_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Match status
    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING)
    user1_interest = Column(Enum(InterestLevel))
    user2_interest = Column(Enum(InterestLevel))
    
    # Compatibility data
    compatibility_score = Column(Float)
    compatibility_report_id = Column(UUID(as_uuid=True))
    
    # Interaction tracking
    conversation_count = Column(Integer, default=0)
    simulation_count = Column(Integer, default=0)
    last_interaction = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CompatibilityReport(Base):
    """Compatibility assessment report."""
    
    __tablename__ = "compatibility_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    
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