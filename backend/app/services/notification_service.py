"""
Notification service for managing user notifications.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import asyncio

from app.models.notification import (
    Notification, NotificationPreference, NotificationType, 
    NotificationChannel, UserBlock, UserReport
)
from app.models.user import User
from app.models.match import Match


class NotificationService:
    """Service for managing notifications and social interactions."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        related_user_id: Optional[str] = None,
        related_match_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None,
        expires_in_hours: Optional[int] = None
    ) -> Notification:
        """
        Create a new notification for a user.
        
        Args:
            user_id: ID of the user to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            related_user_id: ID of related user (optional)
            related_match_id: ID of related match (optional)
            data: Additional notification data (optional)
            action_url: URL to navigate to when clicked (optional)
            expires_in_hours: Hours until notification expires (optional)
            
        Returns:
            Created notification
        """
        # Check if user is blocked by the related user
        if related_user_id:
            is_blocked = await self._is_user_blocked(user_id, related_user_id)
            if is_blocked:
                # Don't create notification if blocked
                return None
        
        # Check user's notification preferences
        preferences = await self._get_user_preferences(user_id)
        if not self._should_send_notification(notification_type, preferences):
            return None
        
        # Calculate expiration time
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        # Create notification
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            related_user_id=related_user_id,
            related_match_id=related_match_id,
            data=data or {},
            action_url=action_url,
            expires_at=expires_at
        )
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        
        # Schedule delivery
        await self._deliver_notification(notification, preferences)
        
        return notification
    
    async def get_user_notifications(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        """
        Get notifications for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of notifications to return
            offset: Number of notifications to skip
            unread_only: Whether to return only unread notifications
            
        Returns:
            List of notifications
        """
        query = select(Notification).options(
            selectinload(Notification.related_user),
            selectinload(Notification.related_match)
        ).where(
            and_(
                Notification.user_id == user_id,
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.utcnow()
                )
            )
        )
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        query = query.order_by(desc(Notification.created_at)).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: ID of the notification
            user_id: ID of the user (for security)
            
        Returns:
            True if successful, False otherwise
        """
        query = select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        
        result = await self.db.execute(query)
        notification = result.scalar_one_or_none()
        
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            await self.db.commit()
            return True
        
        return False
    
    async def mark_all_notifications_read(self, user_id: str) -> int:
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Number of notifications marked as read
        """
        query = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            count += 1
        
        await self.db.commit()
        return count
    
    async def get_unread_count(self, user_id: str) -> int:
        """
        Get count of unread notifications for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Number of unread notifications
        """
        query = select(func.count()).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False,
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.utcnow()
                )
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def block_user(self, blocker_id: str, blocked_id: str, reason: str = None, notes: str = None) -> bool:
        """
        Block a user.
        
        Args:
            blocker_id: ID of the user doing the blocking
            blocked_id: ID of the user being blocked
            reason: Reason for blocking
            notes: Additional notes
            
        Returns:
            True if successful, False otherwise
        """
        # Check if already blocked
        existing_query = select(UserBlock).where(
            and_(
                UserBlock.blocker_id == blocker_id,
                UserBlock.blocked_id == blocked_id
            )
        )
        
        result = await self.db.execute(existing_query)
        if result.scalar_one_or_none():
            return False  # Already blocked
        
        # Create block
        block = UserBlock(
            blocker_id=blocker_id,
            blocked_id=blocked_id,
            reason=reason,
            notes=notes
        )
        
        self.db.add(block)
        await self.db.commit()
        
        return True
    
    async def unblock_user(self, blocker_id: str, blocked_id: str) -> bool:
        """
        Unblock a user.
        
        Args:
            blocker_id: ID of the user doing the unblocking
            blocked_id: ID of the user being unblocked
            
        Returns:
            True if successful, False otherwise
        """
        query = select(UserBlock).where(
            and_(
                UserBlock.blocker_id == blocker_id,
                UserBlock.blocked_id == blocked_id
            )
        )
        
        result = await self.db.execute(query)
        block = result.scalar_one_or_none()
        
        if block:
            await self.db.delete(block)
            await self.db.commit()
            return True
        
        return False
    
    async def report_user(
        self,
        reporter_id: str,
        reported_id: str,
        category: str,
        description: str,
        evidence: Optional[Dict[str, Any]] = None
    ) -> UserReport:
        """
        Report a user for inappropriate behavior.
        
        Args:
            reporter_id: ID of the user making the report
            reported_id: ID of the user being reported
            category: Category of the report
            description: Description of the issue
            evidence: Evidence supporting the report
            
        Returns:
            Created report
        """
        report = UserReport(
            reporter_id=reporter_id,
            reported_id=reported_id,
            category=category,
            description=description,
            evidence=evidence or {}
        )
        
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        
        # Create notification for admins (simplified - in production, use proper admin notification system)
        await self.create_notification(
            user_id=reported_id,  # This would be admin user ID in production
            notification_type=NotificationType.SYSTEM,
            title="New User Report",
            message=f"User reported for {category}",
            related_user_id=reporter_id,
            data={"report_id": str(report.id), "category": category}
        )
        
        return report
    
    async def get_blocked_users(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get list of users blocked by a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of blocked users
        """
        query = select(UserBlock).options(
            selectinload(UserBlock.blocked)
        ).where(UserBlock.blocker_id == user_id)
        
        result = await self.db.execute(query)
        blocks = result.scalars().all()
        
        blocked_users = []
        for block in blocks:
            blocked_users.append({
                "id": str(block.blocked.id),
                "name": f"{block.blocked.first_name} {block.blocked.last_name}",
                "reason": block.reason,
                "blocked_at": block.created_at.isoformat()
            })
        
        return blocked_users
    
    async def _is_user_blocked(self, user_id: str, other_user_id: str) -> bool:
        """Check if a user is blocked by another user."""
        query = select(UserBlock).where(
            and_(
                UserBlock.blocker_id == other_user_id,
                UserBlock.blocked_id == user_id
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def _get_user_preferences(self, user_id: str) -> Optional[NotificationPreference]:
        """Get user's notification preferences."""
        query = select(NotificationPreference).where(
            NotificationPreference.user_id == user_id
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    def _should_send_notification(
        self,
        notification_type: NotificationType,
        preferences: Optional[NotificationPreference]
    ) -> bool:
        """Check if notification should be sent based on user preferences."""
        if not preferences:
            return True  # Default to sending if no preferences set
        
        # Check type-specific preferences
        if notification_type == NotificationType.MATCH and not preferences.match_notifications:
            return False
        if notification_type == NotificationType.MESSAGE and not preferences.message_notifications:
            return False
        if notification_type == NotificationType.LIKE and not preferences.like_notifications:
            return False
        if notification_type == NotificationType.PROFILE_VIEW and not preferences.profile_view_notifications:
            return False
        if notification_type == NotificationType.SYSTEM and not preferences.system_notifications:
            return False
        
        return True
    
    async def _deliver_notification(
        self,
        notification: Notification,
        preferences: Optional[NotificationPreference]
    ):
        """Deliver notification through appropriate channels."""
        channels = []
        
        # Always deliver in-app notifications
        if not preferences or preferences.in_app_enabled:
            channels.append(NotificationChannel.IN_APP.value)
        
        # TODO: Implement email, push, and SMS delivery
        # For now, just mark as delivered
        notification.is_delivered = True
        notification.delivered_at = datetime.utcnow()
        notification.delivery_channels = channels
        
        await self.db.commit()
    
    # Convenience methods for common notifications
    async def notify_new_match(self, user_id: str, match_user_id: str, match_id: str):
        """Create notification for a new match."""
        # Get match user info
        user_query = select(User).where(User.id == match_user_id)
        result = await self.db.execute(user_query)
        match_user = result.scalar_one_or_none()
        
        if match_user:
            await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.MATCH,
                title="New Match!",
                message=f"You have a new match with {match_user.first_name}!",
                related_user_id=match_user_id,
                related_match_id=match_id,
                action_url=f"/matches/{match_id}",
                expires_in_hours=168  # 1 week
            )
    
    async def notify_mutual_match(self, user1_id: str, user2_id: str, match_id: str):
        """Create notifications for a mutual match."""
        # Get user info
        users_query = select(User).where(User.id.in_([user1_id, user2_id]))
        result = await self.db.execute(users_query)
        users = {str(user.id): user for user in result.scalars().all()}
        
        # Notify both users
        for user_id, other_user_id in [(user1_id, user2_id), (user2_id, user1_id)]:
            other_user = users.get(other_user_id)
            if other_user:
                await self.create_notification(
                    user_id=user_id,
                    notification_type=NotificationType.MUTUAL_MATCH,
                    title="It's a Match! 🎉",
                    message=f"You and {other_user.first_name} liked each other!",
                    related_user_id=other_user_id,
                    related_match_id=match_id,
                    action_url=f"/theater/{match_id}",
                    expires_in_hours=168  # 1 week
                )
    
    async def notify_like_received(self, user_id: str, liker_user_id: str):
        """Create notification for receiving a like."""
        # Get liker user info
        user_query = select(User).where(User.id == liker_user_id)
        result = await self.db.execute(user_query)
        liker_user = result.scalar_one_or_none()
        
        if liker_user:
            await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.LIKE,
                title="Someone likes you!",
                message=f"{liker_user.first_name} liked your profile",
                related_user_id=liker_user_id,
                action_url="/discover",
                expires_in_hours=72  # 3 days
            )