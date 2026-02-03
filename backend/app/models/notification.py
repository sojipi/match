"""
Notification database models.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class NotificationType(enum.Enum):
    """Notification type enumeration."""
    MATCH = "match"
    MUTUAL_MATCH = "mutual_match"
    MESSAGE = "message"
    LIKE = "like"
    SUPER_LIKE = "super_like"
    PROFILE_VIEW = "profile_view"
    COMPATIBILITY_REPORT = "compatibility_report"
    SYSTEM = "system"


class NotificationChannel(enum.Enum):
    """Notification delivery channel enumeration."""
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


class Notification(Base):
    """User notification model."""
    
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Notification content
    type = Column(Enum(NotificationType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Related entities
    related_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    related_match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"))
    
    # Notification metadata
    data = Column(JSON, default=dict)  # Additional data for the notification
    action_url = Column(String(500))  # URL to navigate to when clicked
    
    # Delivery status
    is_read = Column(Boolean, default=False)
    is_delivered = Column(Boolean, default=False)
    delivery_channels = Column(JSON, default=list)  # Channels used for delivery
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    related_user = relationship("User", foreign_keys=[related_user_id])
    related_match = relationship("Match", foreign_keys=[related_match_id])


class NotificationPreference(Base):
    """User notification preferences model."""
    
    __tablename__ = "notification_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Channel preferences
    in_app_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    
    # Type preferences
    match_notifications = Column(Boolean, default=True)
    message_notifications = Column(Boolean, default=True)
    like_notifications = Column(Boolean, default=True)
    profile_view_notifications = Column(Boolean, default=False)
    system_notifications = Column(Boolean, default=True)
    
    # Timing preferences
    quiet_hours_start = Column(String(5))  # Format: "22:00"
    quiet_hours_end = Column(String(5))    # Format: "08:00"
    timezone = Column(String(50), default="UTC")
    
    # Frequency settings
    email_digest_frequency = Column(String(20), default="daily")  # none, daily, weekly
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")


class UserBlock(Base):
    """User blocking model."""
    
    __tablename__ = "user_blocks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blocker_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    blocked_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Block details
    reason = Column(String(100))  # harassment, spam, inappropriate, other
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    blocker = relationship("User", foreign_keys=[blocker_id])
    blocked = relationship("User", foreign_keys=[blocked_id])


class UserReport(Base):
    """User reporting model."""
    
    __tablename__ = "user_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reported_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Report details
    category = Column(String(50), nullable=False)  # harassment, fake_profile, inappropriate_content, spam, other
    description = Column(Text, nullable=False)
    evidence = Column(JSON, default=dict)  # Screenshots, message IDs, etc.
    
    # Status
    status = Column(String(20), default="pending")  # pending, investigating, resolved, dismissed
    admin_notes = Column(Text)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id])
    reported = relationship("User", foreign_keys=[reported_id])
    resolver = relationship("User", foreign_keys=[resolved_by])