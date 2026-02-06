"""
Messaging service for direct communication between matched users.
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime
import logging

from app.models.message import DirectMessage, Conversation, ProfileView, MutualConnection
from app.models.user import User
from app.models.match import Match
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType

logger = logging.getLogger(__name__)


class MessagingService:
    """Service for managing direct messages and conversations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_service = NotificationService(db)
    
    async def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        message_type: str = "text",
        media_url: Optional[str] = None,
        media_type: Optional[str] = None
    ) -> DirectMessage:
        """
        Send a direct message to a matched user.
        
        Args:
            sender_id: ID of the sender
            recipient_id: ID of the recipient
            content: Message content
            message_type: Type of message (text, image, gif, sticker)
            media_url: URL of media attachment (optional)
            media_type: MIME type of media (optional)
            
        Returns:
            Created message
        """
        # Verify users are matched
        match = await self._get_match(sender_id, recipient_id)
        if not match:
            raise ValueError("Users are not matched")
        
        # Check if sender is blocked by recipient
        is_blocked = await self.notification_service._is_user_blocked(sender_id, recipient_id)
        if is_blocked:
            raise ValueError("Cannot send message to this user")
        
        # Create message
        message = DirectMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            match_id=match.id,
            content=content,
            message_type=message_type,
            media_url=media_url,
            media_type=media_type
        )
        
        self.db.add(message)
        await self.db.flush()
        
        # Update or create conversation
        await self._update_conversation(match.id, sender_id, recipient_id, message)
        
        await self.db.commit()
        await self.db.refresh(message)
        
        # Send notification to recipient
        await self._notify_new_message(sender_id, recipient_id, content)
        
        return message
    
    async def get_conversations(
        self,
        user_id: str,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get user's conversations.
        
        Args:
            user_id: ID of the user
            include_archived: Whether to include archived conversations
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip
            
        Returns:
            List of conversations with metadata
        """
        query = select(Conversation).options(
            selectinload(Conversation.user1),
            selectinload(Conversation.user2),
            selectinload(Conversation.last_message)
        ).where(
            or_(
                Conversation.user1_id == user_id,
                Conversation.user2_id == user_id
            )
        )
        
        if not include_archived:
            query = query.where(
                or_(
                    and_(Conversation.user1_id == user_id, Conversation.is_archived_by_user1 == False),
                    and_(Conversation.user2_id == user_id, Conversation.is_archived_by_user2 == False)
                )
            )
        
        query = query.order_by(desc(Conversation.last_message_at)).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        conversations = result.scalars().all()
        
        # Format conversations
        formatted_conversations = []
        for conv in conversations:
            other_user = conv.user2 if str(conv.user1_id) == user_id else conv.user1
            is_user1 = str(conv.user1_id) == user_id
            
            formatted_conversations.append({
                "id": str(conv.id),
                "match_id": str(conv.match_id),
                "other_user": {
                    "id": str(other_user.id),
                    "name": f"{other_user.first_name} {other_user.last_name}",
                    "photo_url": None  # TODO: Get primary photo
                },
                "last_message": {
                    "content": conv.last_message.content if conv.last_message else None,
                    "sender_id": str(conv.last_message.sender_id) if conv.last_message else None,
                    "created_at": conv.last_message.created_at.isoformat() if conv.last_message else None
                } if conv.last_message else None,
                "unread_count": conv.user1_unread_count if is_user1 else conv.user2_unread_count,
                "is_muted": conv.is_muted_by_user1 if is_user1 else conv.is_muted_by_user2,
                "is_archived": conv.is_archived_by_user1 if is_user1 else conv.is_archived_by_user2,
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "created_at": conv.created_at.isoformat()
            })
        
        return formatted_conversations
    
    async def get_messages(
        self,
        user_id: str,
        match_id: str,
        limit: int = 50,
        before_message_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get messages for a conversation.
        
        Args:
            user_id: ID of the requesting user
            match_id: ID of the match
            limit: Maximum number of messages to return
            before_message_id: Get messages before this message ID (for pagination)
            
        Returns:
            List of messages
        """
        # Verify user is part of the match
        match = await self._get_match_by_id(match_id)
        if not match or (str(match.user1_id) != user_id and str(match.user2_id) != user_id):
            raise ValueError("User is not part of this match")
        
        query = select(DirectMessage).options(
            selectinload(DirectMessage.sender)
        ).where(
            and_(
                DirectMessage.match_id == match_id,
                DirectMessage.is_deleted == False
            )
        )
        
        if before_message_id:
            # Get messages before a specific message (for pagination)
            before_message_query = select(DirectMessage).where(DirectMessage.id == before_message_id)
            result = await self.db.execute(before_message_query)
            before_message = result.scalar_one_or_none()
            
            if before_message:
                query = query.where(DirectMessage.created_at < before_message.created_at)
        
        query = query.order_by(desc(DirectMessage.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        # Mark messages as read
        await self._mark_messages_read(user_id, match_id)
        
        # Format messages
        formatted_messages = []
        for msg in reversed(messages):  # Reverse to show oldest first
            formatted_messages.append({
                "id": str(msg.id),
                "sender_id": str(msg.sender_id),
                "sender_name": f"{msg.sender.first_name} {msg.sender.last_name}",
                "content": msg.content,
                "message_type": msg.message_type,
                "media_url": msg.media_url,
                "is_read": msg.is_read,
                "created_at": msg.created_at.isoformat()
            })
        
        return formatted_messages
    
    async def mark_conversation_read(self, user_id: str, match_id: str) -> bool:
        """Mark all messages in a conversation as read."""
        return await self._mark_messages_read(user_id, match_id)
    
    async def archive_conversation(self, user_id: str, match_id: str) -> bool:
        """Archive a conversation for a user."""
        query = select(Conversation).where(Conversation.match_id == match_id)
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            return False
        
        if str(conversation.user1_id) == user_id:
            conversation.is_archived_by_user1 = True
        elif str(conversation.user2_id) == user_id:
            conversation.is_archived_by_user2 = True
        else:
            return False
        
        await self.db.commit()
        return True
    
    async def unarchive_conversation(self, user_id: str, match_id: str) -> bool:
        """Unarchive a conversation for a user."""
        query = select(Conversation).where(Conversation.match_id == match_id)
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            return False
        
        if str(conversation.user1_id) == user_id:
            conversation.is_archived_by_user1 = False
        elif str(conversation.user2_id) == user_id:
            conversation.is_archived_by_user2 = False
        else:
            return False
        
        await self.db.commit()
        return True
    
    async def mute_conversation(self, user_id: str, match_id: str) -> bool:
        """Mute notifications for a conversation."""
        query = select(Conversation).where(Conversation.match_id == match_id)
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            return False
        
        if str(conversation.user1_id) == user_id:
            conversation.is_muted_by_user1 = True
        elif str(conversation.user2_id) == user_id:
            conversation.is_muted_by_user2 = True
        else:
            return False
        
        await self.db.commit()
        return True
    
    async def unmute_conversation(self, user_id: str, match_id: str) -> bool:
        """Unmute notifications for a conversation."""
        query = select(Conversation).where(Conversation.match_id == match_id)
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            return False
        
        if str(conversation.user1_id) == user_id:
            conversation.is_muted_by_user1 = False
        elif str(conversation.user2_id) == user_id:
            conversation.is_muted_by_user2 = False
        else:
            return False
        
        await self.db.commit()
        return True
    
    async def delete_message(self, user_id: str, message_id: str) -> bool:
        """Delete a message (soft delete)."""
        query = select(DirectMessage).where(DirectMessage.id == message_id)
        result = await self.db.execute(query)
        message = result.scalar_one_or_none()
        
        if not message or str(message.sender_id) != user_id:
            return False
        
        message.is_deleted = True
        message.deleted_by = user_id
        await self.db.commit()
        return True
    
    async def record_profile_view(
        self,
        viewer_id: str,
        viewed_user_id: str,
        source: str = "discover",
        duration_seconds: Optional[int] = None
    ) -> ProfileView:
        """Record a profile view for social features."""
        view = ProfileView(
            viewer_id=viewer_id,
            viewed_user_id=viewed_user_id,
            source=source,
            view_duration_seconds=duration_seconds
        )
        
        self.db.add(view)
        await self.db.commit()
        await self.db.refresh(view)
        
        # Optionally notify the viewed user
        # await self.notification_service.create_notification(...)
        
        return view
    
    async def get_profile_views(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get recent profile views for a user."""
        query = select(ProfileView).options(
            selectinload(ProfileView.viewer)
        ).where(
            ProfileView.viewed_user_id == user_id
        ).order_by(desc(ProfileView.viewed_at)).limit(limit)
        
        result = await self.db.execute(query)
        views = result.scalars().all()
        
        formatted_views = []
        for view in views:
            formatted_views.append({
                "viewer": {
                    "id": str(view.viewer.id),
                    "name": f"{view.viewer.first_name} {view.viewer.last_name}",
                    "photo_url": None  # TODO: Get primary photo
                },
                "viewed_at": view.viewed_at.isoformat(),
                "source": view.source
            })
        
        return formatted_views
    
    async def get_mutual_connections(
        self,
        user1_id: str,
        user2_id: str
    ) -> Dict[str, Any]:
        """Get mutual connections between two users."""
        # Find mutual matches
        query = select(Match).where(
            or_(
                and_(Match.user1_id == user1_id, Match.user2_id.in_(
                    select(Match.user2_id).where(Match.user1_id == user2_id)
                )),
                and_(Match.user2_id == user1_id, Match.user1_id.in_(
                    select(Match.user1_id).where(Match.user2_id == user2_id)
                ))
            )
        )
        
        result = await self.db.execute(query)
        mutual_matches = result.scalars().all()
        
        return {
            "count": len(mutual_matches),
            "mutual_match_ids": [str(match.id) for match in mutual_matches]
        }
    
    async def _get_match(self, user1_id: str, user2_id: str) -> Optional[Match]:
        """Get match between two users."""
        query = select(Match).where(
            or_(
                and_(Match.user1_id == user1_id, Match.user2_id == user2_id),
                and_(Match.user1_id == user2_id, Match.user2_id == user1_id)
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_match_by_id(self, match_id: str) -> Optional[Match]:
        """Get match by ID."""
        query = select(Match).where(Match.id == match_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _update_conversation(
        self,
        match_id: str,
        sender_id: str,
        recipient_id: str,
        message: DirectMessage
    ):
        """Update or create conversation metadata."""
        query = select(Conversation).where(Conversation.match_id == match_id)
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            # Create new conversation
            conversation = Conversation(
                match_id=match_id,
                user1_id=sender_id,
                user2_id=recipient_id,
                last_message_id=message.id,
                last_message_at=message.created_at,
                message_count=1,
                user2_unread_count=1
            )
            self.db.add(conversation)
        else:
            # Update existing conversation
            conversation.last_message_id = message.id
            conversation.last_message_at = message.created_at
            conversation.message_count += 1
            
            # Increment unread count for recipient
            if str(conversation.user1_id) == recipient_id:
                conversation.user1_unread_count += 1
            else:
                conversation.user2_unread_count += 1
        
        await self.db.flush()
    
    async def _mark_messages_read(self, user_id: str, match_id: str) -> bool:
        """Mark all unread messages in a conversation as read."""
        # Get unread messages
        query = select(DirectMessage).where(
            and_(
                DirectMessage.match_id == match_id,
                DirectMessage.recipient_id == user_id,
                DirectMessage.is_read == False
            )
        )
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        # Mark as read
        for message in messages:
            message.is_read = True
            message.read_at = datetime.utcnow()
        
        # Update conversation unread count
        conv_query = select(Conversation).where(Conversation.match_id == match_id)
        result = await self.db.execute(conv_query)
        conversation = result.scalar_one_or_none()
        
        if conversation:
            if str(conversation.user1_id) == user_id:
                conversation.user1_unread_count = 0
                conversation.user1_last_read_at = datetime.utcnow()
            else:
                conversation.user2_unread_count = 0
                conversation.user2_last_read_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def _notify_new_message(self, sender_id: str, recipient_id: str, content: str):
        """Send notification for new message."""
        # Get sender info
        sender_query = select(User).where(User.id == sender_id)
        result = await self.db.execute(sender_query)
        sender = result.scalar_one_or_none()
        
        if sender:
            # Truncate message preview
            preview = content[:100] + "..." if len(content) > 100 else content
            
            await self.notification_service.create_notification(
                user_id=recipient_id,
                notification_type=NotificationType.MESSAGE,
                title=f"New message from {sender.first_name}",
                message=preview,
                related_user_id=sender_id,
                data={"message_preview": preview},
                action_url=f"/messages",
                expires_in_hours=72
            )
