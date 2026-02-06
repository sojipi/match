"""
Push notification service for PWA support.
"""
from typing import Optional, Dict, Any
import json
import logging
from pywebpush import webpush, WebPushException

from app.core.config import settings

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for sending push notifications to PWA clients."""
    
    def __init__(self):
        self.vapid_private_key = settings.VAPID_PRIVATE_KEY
        self.vapid_public_key = settings.VAPID_PUBLIC_KEY
        self.vapid_claims = {
            "sub": f"mailto:{settings.FROM_EMAIL}"
        }
        self.enabled = settings.PUSH_NOTIFICATIONS_ENABLED
    
    async def send_push_notification(
        self,
        subscription_info: Dict[str, Any],
        title: str,
        body: str,
        icon: Optional[str] = None,
        badge: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None
    ) -> bool:
        """
        Send a push notification to a subscribed client.
        
        Args:
            subscription_info: Web push subscription information
            title: Notification title
            body: Notification body
            icon: Notification icon URL
            badge: Notification badge URL
            data: Additional notification data
            action_url: URL to navigate to when clicked
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"Push notifications disabled. Would have sent: {title}")
            return True
        
        if not self.vapid_private_key or not self.vapid_public_key:
            logger.warning("VAPID keys not configured. Cannot send push notifications.")
            return False
        
        try:
            # Prepare notification payload
            notification_data = {
                "title": title,
                "body": body,
                "icon": icon or f"{settings.FRONTEND_URL}/logo192.png",
                "badge": badge or f"{settings.FRONTEND_URL}/badge.png",
                "data": data or {},
                "actions": []
            }
            
            if action_url:
                notification_data["data"]["url"] = action_url
                notification_data["actions"].append({
                    "action": "open",
                    "title": "View"
                })
            
            # Send push notification
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(notification_data),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims
            )
            
            logger.info(f"Push notification sent successfully: {title}")
            return True
            
        except WebPushException as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            
            # If subscription is no longer valid, we should remove it
            if e.response and e.response.status_code in [404, 410]:
                logger.info("Push subscription is no longer valid")
                # TODO: Remove invalid subscription from database
            
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending push notification: {str(e)}")
            return False
    
    async def send_match_notification(
        self,
        subscription_info: Dict[str, Any],
        match_name: str,
        action_url: Optional[str] = None
    ) -> bool:
        """Send new match push notification."""
        return await self.send_push_notification(
            subscription_info=subscription_info,
            title="New Match! 💕",
            body=f"You have a new match with {match_name}!",
            data={"type": "match"},
            action_url=action_url
        )
    
    async def send_mutual_match_notification(
        self,
        subscription_info: Dict[str, Any],
        match_name: str,
        action_url: Optional[str] = None
    ) -> bool:
        """Send mutual match push notification."""
        return await self.send_push_notification(
            subscription_info=subscription_info,
            title="It's a Match! 🎉",
            body=f"You and {match_name} liked each other!",
            data={"type": "mutual_match"},
            action_url=action_url
        )
    
    async def send_message_notification(
        self,
        subscription_info: Dict[str, Any],
        sender_name: str,
        message_preview: str,
        action_url: Optional[str] = None
    ) -> bool:
        """Send new message push notification."""
        return await self.send_push_notification(
            subscription_info=subscription_info,
            title=f"New message from {sender_name}",
            body=message_preview,
            data={"type": "message"},
            action_url=action_url
        )
    
    async def send_compatibility_report_notification(
        self,
        subscription_info: Dict[str, Any],
        match_name: str,
        action_url: Optional[str] = None
    ) -> bool:
        """Send compatibility report ready push notification."""
        return await self.send_push_notification(
            subscription_info=subscription_info,
            title="Compatibility Report Ready 📊",
            body=f"Your compatibility report with {match_name} is ready!",
            data={"type": "compatibility_report"},
            action_url=action_url
        )


# Global push notification service instance
push_notification_service = PushNotificationService()
