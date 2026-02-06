"""
Notification and social interaction endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.notification import NotificationType, NotificationPreference, PushSubscription

router = APIRouter()


class NotificationResponse(BaseModel):
    """Notification response model."""
    id: str
    type: str
    title: str
    message: str
    is_read: bool
    created_at: str
    read_at: Optional[str] = None
    action_url: Optional[str] = None
    data: Dict[str, Any] = {}
    related_user: Optional[Dict[str, Any]] = None


class NotificationListResponse(BaseModel):
    """Notification list response."""
    notifications: List[NotificationResponse]
    unread_count: int
    total_count: int


class BlockUserRequest(BaseModel):
    """Block user request."""
    reason: Optional[str] = None
    notes: Optional[str] = None


class ReportUserRequest(BaseModel):
    """Report user request."""
    category: str
    description: str
    evidence: Optional[Dict[str, Any]] = None


class BlockedUser(BaseModel):
    """Blocked user response."""
    id: str
    name: str
    reason: Optional[str] = None
    blocked_at: str


class NotificationPreferencesRequest(BaseModel):
    """Notification preferences update request."""
    in_app_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    match_notifications: Optional[bool] = None
    message_notifications: Optional[bool] = None
    like_notifications: Optional[bool] = None
    profile_view_notifications: Optional[bool] = None
    system_notifications: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None
    email_digest_frequency: Optional[str] = None


class NotificationPreferencesResponse(BaseModel):
    """Notification preferences response."""
    in_app_enabled: bool
    email_enabled: bool
    push_enabled: bool
    match_notifications: bool
    message_notifications: bool
    like_notifications: bool
    profile_view_notifications: bool
    system_notifications: bool
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: str
    email_digest_frequency: str


class PushSubscriptionRequest(BaseModel):
    """Push subscription request."""
    endpoint: str
    keys: Dict[str, str]  # Contains p256dh and auth keys
    user_agent: Optional[str] = None
    device_name: Optional[str] = None


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user notifications."""
    notification_service = NotificationService(db)
    
    try:
        # Get notifications
        notifications = await notification_service.get_user_notifications(
            user_id=str(current_user.id),
            limit=limit,
            offset=offset,
            unread_only=unread_only
        )
        
        # Get unread count
        unread_count = await notification_service.get_unread_count(str(current_user.id))
        
        # Convert to response format
        notification_responses = []
        for notification in notifications:
            related_user = None
            if notification.related_user:
                related_user = {
                    "id": str(notification.related_user.id),
                    "name": f"{notification.related_user.first_name} {notification.related_user.last_name}",
                    "photo_url": None  # TODO: Get primary photo
                }
            
            notification_responses.append(NotificationResponse(
                id=str(notification.id),
                type=notification.type.value,
                title=notification.title,
                message=notification.message,
                is_read=notification.is_read,
                created_at=notification.created_at.isoformat(),
                read_at=notification.read_at.isoformat() if notification.read_at else None,
                action_url=notification.action_url,
                data=notification.data,
                related_user=related_user
            ))
        
        return NotificationListResponse(
            notifications=notification_responses,
            unread_count=unread_count,
            total_count=len(notifications)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a notification as read."""
    notification_service = NotificationService(db)
    
    try:
        success = await notification_service.mark_notification_read(
            notification_id=notification_id,
            user_id=str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )


@router.post("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read."""
    notification_service = NotificationService(db)
    
    try:
        count = await notification_service.mark_all_notifications_read(str(current_user.id))
        return {"message": f"Marked {count} notifications as read"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notifications as read: {str(e)}"
        )


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications."""
    notification_service = NotificationService(db)
    
    try:
        count = await notification_service.get_unread_count(str(current_user.id))
        return {"unread_count": count}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )


@router.post("/block/{user_id}")
async def block_user(
    user_id: str,
    request: BlockUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Block a user."""
    notification_service = NotificationService(db)
    
    try:
        success = await notification_service.block_user(
            blocker_id=str(current_user.id),
            blocked_id=user_id,
            reason=request.reason,
            notes=request.notes
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already blocked"
            )
        
        return {"message": "User blocked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to block user: {str(e)}"
        )


@router.delete("/block/{user_id}")
async def unblock_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unblock a user."""
    notification_service = NotificationService(db)
    
    try:
        success = await notification_service.unblock_user(
            blocker_id=str(current_user.id),
            blocked_id=user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not blocked"
            )
        
        return {"message": "User unblocked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unblock user: {str(e)}"
        )


@router.get("/blocked", response_model=List[BlockedUser])
async def get_blocked_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of blocked users."""
    notification_service = NotificationService(db)
    
    try:
        blocked_users = await notification_service.get_blocked_users(str(current_user.id))
        return [BlockedUser(**user) for user in blocked_users]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get blocked users: {str(e)}"
        )


@router.post("/report/{user_id}")
async def report_user(
    user_id: str,
    request: ReportUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Report a user for inappropriate behavior."""
    notification_service = NotificationService(db)
    
    try:
        report = await notification_service.report_user(
            reporter_id=str(current_user.id),
            reported_id=user_id,
            category=request.category,
            description=request.description,
            evidence=request.evidence
        )
        
        return {
            "message": "User reported successfully",
            "report_id": str(report.id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to report user: {str(e)}"
        )



@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's notification preferences."""
    try:
        from sqlalchemy import select
        
        # Get or create preferences
        query = select(NotificationPreference).where(
            NotificationPreference.user_id == current_user.id
        )
        result = await db.execute(query)
        preferences = result.scalar_one_or_none()
        
        if not preferences:
            # Create default preferences
            preferences = NotificationPreference(user_id=current_user.id)
            db.add(preferences)
            await db.commit()
            await db.refresh(preferences)
        
        return NotificationPreferencesResponse(
            in_app_enabled=preferences.in_app_enabled,
            email_enabled=preferences.email_enabled,
            push_enabled=preferences.push_enabled,
            match_notifications=preferences.match_notifications,
            message_notifications=preferences.message_notifications,
            like_notifications=preferences.like_notifications,
            profile_view_notifications=preferences.profile_view_notifications,
            system_notifications=preferences.system_notifications,
            quiet_hours_start=preferences.quiet_hours_start,
            quiet_hours_end=preferences.quiet_hours_end,
            timezone=preferences.timezone,
            email_digest_frequency=preferences.email_digest_frequency
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification preferences: {str(e)}"
        )


@router.put("/preferences", response_model=NotificationPreferencesResponse)
async def update_notification_preferences(
    request: NotificationPreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's notification preferences."""
    try:
        from sqlalchemy import select
        
        # Get or create preferences
        query = select(NotificationPreference).where(
            NotificationPreference.user_id == current_user.id
        )
        result = await db.execute(query)
        preferences = result.scalar_one_or_none()
        
        if not preferences:
            preferences = NotificationPreference(user_id=current_user.id)
            db.add(preferences)
        
        # Update preferences
        if request.in_app_enabled is not None:
            preferences.in_app_enabled = request.in_app_enabled
        if request.email_enabled is not None:
            preferences.email_enabled = request.email_enabled
        if request.push_enabled is not None:
            preferences.push_enabled = request.push_enabled
        if request.match_notifications is not None:
            preferences.match_notifications = request.match_notifications
        if request.message_notifications is not None:
            preferences.message_notifications = request.message_notifications
        if request.like_notifications is not None:
            preferences.like_notifications = request.like_notifications
        if request.profile_view_notifications is not None:
            preferences.profile_view_notifications = request.profile_view_notifications
        if request.system_notifications is not None:
            preferences.system_notifications = request.system_notifications
        if request.quiet_hours_start is not None:
            preferences.quiet_hours_start = request.quiet_hours_start
        if request.quiet_hours_end is not None:
            preferences.quiet_hours_end = request.quiet_hours_end
        if request.timezone is not None:
            preferences.timezone = request.timezone
        if request.email_digest_frequency is not None:
            preferences.email_digest_frequency = request.email_digest_frequency
        
        await db.commit()
        await db.refresh(preferences)
        
        return NotificationPreferencesResponse(
            in_app_enabled=preferences.in_app_enabled,
            email_enabled=preferences.email_enabled,
            push_enabled=preferences.push_enabled,
            match_notifications=preferences.match_notifications,
            message_notifications=preferences.message_notifications,
            like_notifications=preferences.like_notifications,
            profile_view_notifications=preferences.profile_view_notifications,
            system_notifications=preferences.system_notifications,
            quiet_hours_start=preferences.quiet_hours_start,
            quiet_hours_end=preferences.quiet_hours_end,
            timezone=preferences.timezone,
            email_digest_frequency=preferences.email_digest_frequency
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification preferences: {str(e)}"
        )


@router.post("/push/subscribe")
async def subscribe_to_push_notifications(
    request: PushSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Subscribe to push notifications."""
    try:
        from sqlalchemy import select
        from datetime import datetime
        
        # Check if subscription already exists
        query = select(PushSubscription).where(
            PushSubscription.endpoint == request.endpoint
        )
        result = await db.execute(query)
        subscription = result.scalar_one_or_none()
        
        if subscription:
            # Update existing subscription
            subscription.user_id = current_user.id
            subscription.p256dh_key = request.keys.get('p256dh', '')
            subscription.auth_key = request.keys.get('auth', '')
            subscription.user_agent = request.user_agent
            subscription.device_name = request.device_name
            subscription.is_active = True
            subscription.last_used = datetime.utcnow()
        else:
            # Create new subscription
            subscription = PushSubscription(
                user_id=current_user.id,
                endpoint=request.endpoint,
                p256dh_key=request.keys.get('p256dh', ''),
                auth_key=request.keys.get('auth', ''),
                user_agent=request.user_agent,
                device_name=request.device_name,
                is_active=True,
                last_used=datetime.utcnow()
            )
            db.add(subscription)
        
        await db.commit()
        
        return {"message": "Successfully subscribed to push notifications"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to subscribe to push notifications: {str(e)}"
        )


@router.post("/push/unsubscribe")
async def unsubscribe_from_push_notifications(
    endpoint: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unsubscribe from push notifications."""
    try:
        from sqlalchemy import select, and_
        
        # Find and deactivate subscription
        query = select(PushSubscription).where(
            and_(
                PushSubscription.user_id == current_user.id,
                PushSubscription.endpoint == endpoint
            )
        )
        result = await db.execute(query)
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.is_active = False
            await db.commit()
            return {"message": "Successfully unsubscribed from push notifications"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unsubscribe from push notifications: {str(e)}"
        )
