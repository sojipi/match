"""
Notification and real-time update models.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class NotificationType(enum.Enum):
    """Notification type enumeration."""
    NEW_MATCH = "new_match"
    MUTUAL_MATCH = "mutual_match"
    SESSION_STARTED = "session_started"
    SESSION_COMPLETED = "session_completed"
    COMPATIBILITY_REPORT = "compatibility_report"
    MESSAGE_RECEIVED = "message_received"
    PROFILE_VIEWED = "profile_viewed"
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class NotificationStatus(enum.Enum):
    """Notification status enumeration."""
    UNREAD = "unread"
    READ = "read"
    DISMISSED = "dismissed"


class Notification(Base):
    """User notification model."""
    
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Notification content
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Notification metadata
    status = Column(Enum(NotificationStatus), default=NotificationStatus.UNREAD)
    priority = Column(Integer, default=1)  # 1=low, 2=medium, 3=high
    
    # Related entities
    related_match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"))
    related_session_id = Column(UUID(as_uuid=True), ForeignKey("match_sessions.id"))
    related_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Delivery tracking
    sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    dismissed_at = Column(DateTime(timezone=True))
    
    # Additional data
    action_url = Column(String(500))  # URL to navigate to when clicked
    extra_data = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    related_match = relationship("Match", foreign_keys=[related_match_id])
    related_session = relationship("MatchSession", foreign_keys=[related_session_id])
    related_user = relationship("User", foreign_keys=[related_user_id])


class UserActivity(Base):
    """User activity tracking model."""
    
    __tablename__ = "user_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String(50), nullable=False)  # login, profile_update, match_action, etc.
    description = Column(String(500))
    
    # Activity metadata
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(String(500))
    device_info = Column(JSON, default=dict)
    
    # Location data (optional)
    location_data = Column(JSON, default=dict)
    
    # Additional context
    extra_data = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")