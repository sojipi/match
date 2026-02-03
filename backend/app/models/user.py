"""
User and profile database models.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, Date, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
import uuid

from app.core.database import Base


class User(Base):
    """User account model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(20))
    location = Column(String(255))
    bio = Column(Text)
    
    # Account status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String(20), default="free")
    
    # Settings
    privacy_settings = Column(JSON, default=dict)
    notification_preferences = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_active = Column(DateTime(timezone=True))
    
    # Relationships
    photos = relationship("UserPhoto", back_populates="user", cascade="all, delete-orphan")
    personality_profile = relationship("PersonalityProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    dating_preferences = relationship("DatingPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    ai_avatar = relationship("AIAvatar", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # Match relationships (user can be user1 or user2 in matches)
    matches_as_user1 = relationship("Match", foreign_keys="Match.user1_id", back_populates="user1")
    matches_as_user2 = relationship("Match", foreign_keys="Match.user2_id", back_populates="user2")
    
    # Session relationships
    sessions_as_user1 = relationship("MatchSession", foreign_keys="MatchSession.user1_id", back_populates="user1")
    sessions_as_user2 = relationship("MatchSession", foreign_keys="MatchSession.user2_id", back_populates="user2")


class UserPhoto(Base):
    """User photo model."""
    
    __tablename__ = "user_photos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_url = Column(String(500), nullable=False)
    is_primary = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="photos")


class PersonalityProfile(Base):
    """User personality profile model."""
    
    __tablename__ = "personality_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Big Five personality traits (0.0 to 1.0)
    openness = Column(Float)
    conscientiousness = Column(Float)
    extraversion = Column(Float)
    agreeableness = Column(Float)
    neuroticism = Column(Float)
    
    # Additional personality data
    values = Column(JSON, default=dict)  # Custom values with importance ratings
    communication_style = Column(String(50))
    conflict_resolution_style = Column(String(50))
    
    # Assessment metadata
    assessment_version = Column(String(20))
    completeness_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="personality_profile")
    ai_avatar = relationship("AIAvatar", back_populates="personality_profile", uselist=False)


class DatingPreferences(Base):
    """User dating preferences model."""
    
    __tablename__ = "dating_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Basic preferences
    age_range_min = Column(Integer)
    age_range_max = Column(Integer)
    max_distance = Column(Integer)  # in kilometers
    gender_preference = Column(JSON, default=list)
    
    # Relationship preferences
    relationship_goals = Column(JSON, default=list)
    lifestyle_preferences = Column(JSON, default=dict)
    deal_breakers = Column(JSON, default=list)
    importance_weights = Column(JSON, default=dict)  # Weight different compatibility factors
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="dating_preferences")