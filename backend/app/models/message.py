"""
Direct messaging database models.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class DirectMessage(Base):
    """Direct message between matched users."""
    
    __tablename__ = "direct_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Conversation participants
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, image, gif, sticker
    
    # Media attachments
    media_url = Column(String(500))
    media_type = Column(String(50))  # image/jpeg, image/png, image/gif
    thumbnail_url = Column(String(500))
    
    # Message metadata
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    
    # Moderation and safety
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(String(200))
    is_deleted = Column(Boolean, default=False)
    deleted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    match = relationship("Match")


class Conversation(Base):
    """Conversation thread between matched users."""
    
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Participants
    user1_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user2_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Conversation metadata
    last_message_id = Column(UUID(as_uuid=True), ForeignKey("direct_messages.id"))
    last_message_at = Column(DateTime(timezone=True))
    message_count = Column(Integer, default=0)
    
    # Read status for each user
    user1_last_read_at = Column(DateTime(timezone=True))
    user2_last_read_at = Column(DateTime(timezone=True))
    user1_unread_count = Column(Integer, default=0)
    user2_unread_count = Column(Integer, default=0)
    
    # Conversation status
    is_active = Column(Boolean, default=True)
    is_archived_by_user1 = Column(Boolean, default=False)
    is_archived_by_user2 = Column(Boolean, default=False)
    is_muted_by_user1 = Column(Boolean, default=False)
    is_muted_by_user2 = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    match = relationship("Match")
    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])
    last_message = relationship("DirectMessage", foreign_keys=[last_message_id])


class ProfileView(Base):
    """Track profile views for social features."""
    
    __tablename__ = "profile_views"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Viewer and viewed user
    viewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    viewed_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # View metadata
    view_duration_seconds = Column(Integer)  # How long they viewed the profile
    source = Column(String(50))  # Where they viewed from: discover, match, search
    
    # Timestamps
    viewed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    viewer = relationship("User", foreign_keys=[viewer_id])
    viewed_user = relationship("User", foreign_keys=[viewed_user_id])


class MutualConnection(Base):
    """Track mutual connections between users."""
    
    __tablename__ = "mutual_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # The two users with mutual connections
    user1_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user2_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Mutual connection details
    mutual_match_ids = Column(JSON, default=list)  # List of mutual match IDs
    connection_count = Column(Integer, default=0)
    
    # Timestamps
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])
