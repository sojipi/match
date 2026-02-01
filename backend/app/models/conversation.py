"""
Conversation and session database models.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class SessionType(enum.Enum):
    """Session type enumeration."""
    CONVERSATION = "conversation"
    SIMULATION = "simulation"
    SPEED_CHAT = "speed_chat"


class SessionStatus(enum.Enum):
    """Session status enumeration."""
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"


class AgentType(enum.Enum):
    """Agent type enumeration."""
    USER_AVATAR = "user_avatar"
    MATCHMAKER_AGENT = "matchmaker_agent"
    SYSTEM = "system"


class MessageType(enum.Enum):
    """Message type enumeration."""
    TEXT = "text"
    EMOTION = "emotion"
    ACTION = "action"
    SYSTEM_NOTIFICATION = "system_notification"


class MatchSession(Base):
    """Live matching session between users."""
    
    __tablename__ = "match_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user1_id = Column(UUID(as_uuid=True), nullable=False)
    user2_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Session configuration
    session_type = Column(Enum(SessionType), default=SessionType.CONVERSATION)
    status = Column(Enum(SessionStatus), default=SessionStatus.WAITING)
    
    # Session timing
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    
    # Real-time data
    live_compatibility_score = Column(Float, default=0.0)
    viewer_count = Column(Integer, default=0)
    
    # Session results
    final_compatibility_score = Column(Float)
    user1_feedback = Column(JSON, default=dict)
    user2_feedback = Column(JSON, default=dict)
    
    # Metadata
    scenario_id = Column(UUID(as_uuid=True))  # For simulation sessions
    ai_agent_config = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ConversationMessage(Base):
    """Individual conversation message."""
    
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Message content
    sender_type = Column(Enum(AgentType), nullable=False)
    sender_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    
    # Message metadata
    emotion_indicators = Column(JSON, default=list)
    compatibility_impact = Column(Float)
    is_highlighted = Column(Boolean, default=False)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class Scenario(Base):
    """Relationship simulation scenario."""
    
    __tablename__ = "scenarios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Scenario details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    
    # Configuration
    difficulty_level = Column(Integer, default=1)  # 1-5 scale
    expected_duration = Column(Integer)  # in minutes
    cultural_context = Column(String(50))
    
    # Scenario content
    context_data = Column(JSON, default=dict)
    success_criteria = Column(JSON, default=list)
    evaluation_metrics = Column(JSON, default=dict)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    average_rating = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())