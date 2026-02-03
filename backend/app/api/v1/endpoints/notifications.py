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
from app.models.notification import NotificationType

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