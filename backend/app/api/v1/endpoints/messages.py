"""
Direct messaging endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.messaging_service import MessagingService
from app.models.user import User

router = APIRouter()


class SendMessageRequest(BaseModel):
    """Send message request."""
    recipient_id: str
    content: str
    message_type: str = "text"
    media_url: Optional[str] = None
    media_type: Optional[str] = None


class MessageResponse(BaseModel):
    """Message response."""
    id: str
    sender_id: str
    sender_name: str
    content: str
    message_type: str
    media_url: Optional[str] = None
    is_read: bool
    created_at: str


class ConversationResponse(BaseModel):
    """Conversation response."""
    id: str
    match_id: str
    other_user: Dict[str, Any]
    last_message: Optional[Dict[str, Any]]
    unread_count: int
    is_muted: bool
    is_archived: bool
    last_message_at: Optional[str]
    created_at: str


class ProfileViewRequest(BaseModel):
    """Profile view request."""
    viewed_user_id: str
    source: str = "discover"
    duration_seconds: Optional[int] = None


@router.post("/send", response_model=MessageResponse)
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a direct message to a matched user."""
    messaging_service = MessagingService(db)
    
    try:
        message = await messaging_service.send_message(
            sender_id=str(current_user.id),
            recipient_id=request.recipient_id,
            content=request.content,
            message_type=request.message_type,
            media_url=request.media_url,
            media_type=request.media_type
        )
        
        return MessageResponse(
            id=str(message.id),
            sender_id=str(message.sender_id),
            sender_name=f"{current_user.first_name} {current_user.last_name}",
            content=message.content,
            message_type=message.message_type,
            media_url=message.media_url,
            is_read=message.is_read,
            created_at=message.created_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    include_archived: bool = False,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's conversations."""
    messaging_service = MessagingService(db)
    
    try:
        conversations = await messaging_service.get_conversations(
            user_id=str(current_user.id),
            include_archived=include_archived,
            limit=limit,
            offset=offset
        )
        
        return [ConversationResponse(**conv) for conv in conversations]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversations: {str(e)}"
        )


@router.get("/conversation/{match_id}", response_model=List[MessageResponse])
async def get_messages(
    match_id: str,
    limit: int = Query(50, ge=1, le=100),
    before_message_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a conversation."""
    messaging_service = MessagingService(db)
    
    try:
        messages = await messaging_service.get_messages(
            user_id=str(current_user.id),
            match_id=match_id,
            limit=limit,
            before_message_id=before_message_id
        )
        
        return [MessageResponse(**msg) for msg in messages]
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}"
        )


@router.post("/conversation/{match_id}/read")
async def mark_conversation_read(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all messages in a conversation as read."""
    messaging_service = MessagingService(db)
    
    try:
        success = await messaging_service.mark_conversation_read(
            user_id=str(current_user.id),
            match_id=match_id
        )
        
        if success:
            return {"message": "Conversation marked as read"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark conversation as read: {str(e)}"
        )


@router.post("/conversation/{match_id}/archive")
async def archive_conversation(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Archive a conversation."""
    messaging_service = MessagingService(db)
    
    try:
        success = await messaging_service.archive_conversation(
            user_id=str(current_user.id),
            match_id=match_id
        )
        
        if success:
            return {"message": "Conversation archived"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to archive conversation: {str(e)}"
        )


@router.post("/conversation/{match_id}/unarchive")
async def unarchive_conversation(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unarchive a conversation."""
    messaging_service = MessagingService(db)
    
    try:
        success = await messaging_service.unarchive_conversation(
            user_id=str(current_user.id),
            match_id=match_id
        )
        
        if success:
            return {"message": "Conversation unarchived"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unarchive conversation: {str(e)}"
        )


@router.post("/conversation/{match_id}/mute")
async def mute_conversation(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mute notifications for a conversation."""
    messaging_service = MessagingService(db)
    
    try:
        success = await messaging_service.mute_conversation(
            user_id=str(current_user.id),
            match_id=match_id
        )
        
        if success:
            return {"message": "Conversation muted"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mute conversation: {str(e)}"
        )


@router.post("/conversation/{match_id}/unmute")
async def unmute_conversation(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unmute notifications for a conversation."""
    messaging_service = MessagingService(db)
    
    try:
        success = await messaging_service.unmute_conversation(
            user_id=str(current_user.id),
            match_id=match_id
        )
        
        if success:
            return {"message": "Conversation unmuted"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unmute conversation: {str(e)}"
        )


@router.delete("/message/{message_id}")
async def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a message."""
    messaging_service = MessagingService(db)
    
    try:
        success = await messaging_service.delete_message(
            user_id=str(current_user.id),
            message_id=message_id
        )
        
        if success:
            return {"message": "Message deleted"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found or you don't have permission to delete it"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete message: {str(e)}"
        )


@router.post("/profile-view")
async def record_profile_view(
    request: ProfileViewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record a profile view."""
    messaging_service = MessagingService(db)
    
    try:
        await messaging_service.record_profile_view(
            viewer_id=str(current_user.id),
            viewed_user_id=request.viewed_user_id,
            source=request.source,
            duration_seconds=request.duration_seconds
        )
        
        return {"message": "Profile view recorded"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record profile view: {str(e)}"
        )


@router.get("/profile-views")
async def get_profile_views(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent profile views."""
    messaging_service = MessagingService(db)
    
    try:
        views = await messaging_service.get_profile_views(
            user_id=str(current_user.id),
            limit=limit
        )
        
        return {"views": views}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile views: {str(e)}"
        )


@router.get("/mutual-connections/{user_id}")
async def get_mutual_connections(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get mutual connections with another user."""
    messaging_service = MessagingService(db)
    
    try:
        connections = await messaging_service.get_mutual_connections(
            user1_id=str(current_user.id),
            user2_id=user_id
        )
        
        return connections
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mutual connections: {str(e)}"
        )
