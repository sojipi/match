"""
User management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid
import os

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserPhoto

router = APIRouter()


class UserProfile(BaseModel):
    """User profile response."""
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    location: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    photos: List[dict] = []
    profile_completeness: float = 0.0
    is_verified: bool = False
    subscription_tier: str = "free"


class ProfileUpdate(BaseModel):
    """Profile update request."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    gender: Optional[str] = None


class PrivacySettings(BaseModel):
    """Privacy settings model."""
    profile_visibility: str = "public"  # public, friends, private
    show_age: bool = True
    show_location: bool = True
    show_last_active: bool = True
    allow_messages_from: str = "matches"  # everyone, matches, none
    show_in_discovery: bool = True


class NotificationPreferences(BaseModel):
    """Notification preferences model."""
    email_matches: bool = True
    email_messages: bool = True
    email_reports: bool = True
    push_matches: bool = True
    push_messages: bool = True
    push_sessions: bool = True


class PhotoResponse(BaseModel):
    """Photo response model."""
    id: str
    file_url: str
    is_primary: bool
    order_index: int
    uploaded_at: str


class SubscriptionUpdate(BaseModel):
    """Subscription update request."""
    tier: str  # free, premium, pro


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user profile."""
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    
    try:
        # Load user with photos
        query = select(User).options(
            selectinload(User.photos),
            selectinload(User.personality_profile)
        ).where(User.id == current_user.id)
        
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Calculate profile completeness
        completeness = 0.0
        fields = [
            user.first_name,
            user.last_name,
            user.bio,
            user.location,
            user.date_of_birth,
            user.gender
        ]
        completeness += sum(1 for field in fields if field) / len(fields) * 0.5
        
        if user.photos:
            completeness += 0.2
        
        if user.personality_profile and user.personality_profile.completeness_score > 0.8:
            completeness += 0.3
        
        # Format photos
        photos = [
            {
                "id": str(photo.id),
                "file_url": photo.file_url,
                "is_primary": photo.is_primary,
                "order_index": photo.order_index,
                "uploaded_at": photo.uploaded_at.isoformat()
            }
            for photo in sorted(user.photos, key=lambda p: p.order_index)
        ] if user.photos else []
        
        return UserProfile(
            id=str(user.id),
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            bio=user.bio,
            location=user.location,
            date_of_birth=user.date_of_birth.isoformat() if user.date_of_birth else None,
            gender=user.gender,
            photos=photos,
            profile_completeness=min(completeness, 1.0),
            is_verified=user.is_verified,
            subscription_tier=user.subscription_tier or "free"
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in get_user_profile: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load profile: {str(e)}"
        )


@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile."""
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    
    # Load user
    query = select(User).options(
        selectinload(User.photos),
        selectinload(User.personality_profile)
    ).where(User.id == current_user.id)
    
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if profile_data.first_name is not None:
        user.first_name = profile_data.first_name
    if profile_data.last_name is not None:
        user.last_name = profile_data.last_name
    if profile_data.bio is not None:
        user.bio = profile_data.bio
    if profile_data.location is not None:
        user.location = profile_data.location
    if profile_data.gender is not None:
        user.gender = profile_data.gender
    
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    # Return updated profile
    return await get_user_profile(current_user=user, db=db)


@router.post("/photos/upload", response_model=PhotoResponse)
async def upload_photo(
    file: UploadFile = File(...),
    is_primary: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a profile photo."""
    from sqlalchemy import select
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and WebP images are allowed."
        )
    
    # Validate file size (max 5MB)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit."
        )
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # In production, upload to CDN (S3, CloudFlare, etc.)
    # For now, save locally
    upload_dir = "uploads/photos"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Create photo record
    # Get current photo count for order_index
    query = select(UserPhoto).where(UserPhoto.user_id == current_user.id)
    result = await db.execute(query)
    existing_photos = result.scalars().all()
    
    # If this is the first photo or marked as primary, update other photos
    if is_primary or len(existing_photos) == 0:
        for photo in existing_photos:
            photo.is_primary = False
        is_primary = True
    
    new_photo = UserPhoto(
        id=uuid.uuid4(),
        user_id=current_user.id,
        file_url=f"/uploads/photos/{unique_filename}",
        is_primary=is_primary,
        order_index=len(existing_photos),
        uploaded_at=datetime.utcnow()
    )
    
    db.add(new_photo)
    await db.commit()
    await db.refresh(new_photo)
    
    return PhotoResponse(
        id=str(new_photo.id),
        file_url=new_photo.file_url,
        is_primary=new_photo.is_primary,
        order_index=new_photo.order_index,
        uploaded_at=new_photo.uploaded_at.isoformat()
    )


@router.delete("/photos/{photo_id}")
async def delete_photo(
    photo_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a profile photo."""
    from sqlalchemy import select
    
    # Find photo
    query = select(UserPhoto).where(
        UserPhoto.id == photo_id,
        UserPhoto.user_id == current_user.id
    )
    result = await db.execute(query)
    photo = result.scalar_one_or_none()
    
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    
    # Delete file
    file_path = photo.file_url.lstrip('/')
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete record
    await db.delete(photo)
    await db.commit()
    
    return {"message": "Photo deleted successfully"}


@router.put("/photos/{photo_id}/primary")
async def set_primary_photo(
    photo_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Set a photo as primary."""
    from sqlalchemy import select
    
    # Find photo
    query = select(UserPhoto).where(
        UserPhoto.id == photo_id,
        UserPhoto.user_id == current_user.id
    )
    result = await db.execute(query)
    photo = result.scalar_one_or_none()
    
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    
    # Update all photos
    query = select(UserPhoto).where(UserPhoto.user_id == current_user.id)
    result = await db.execute(query)
    all_photos = result.scalars().all()
    
    for p in all_photos:
        p.is_primary = (p.id == photo.id)
    
    await db.commit()
    
    return {"message": "Primary photo updated"}


@router.get("/privacy", response_model=PrivacySettings)
async def get_privacy_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user privacy settings."""
    settings = current_user.privacy_settings or {}
    
    return PrivacySettings(
        profile_visibility=settings.get("profile_visibility", "public"),
        show_age=settings.get("show_age", True),
        show_location=settings.get("show_location", True),
        show_last_active=settings.get("show_last_active", True),
        allow_messages_from=settings.get("allow_messages_from", "matches"),
        show_in_discovery=settings.get("show_in_discovery", True)
    )


@router.put("/privacy", response_model=PrivacySettings)
async def update_privacy_settings(
    settings: PrivacySettings,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user privacy settings."""
    from sqlalchemy import select
    
    query = select(User).where(User.id == current_user.id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.privacy_settings = settings.dict()
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return settings


@router.get("/notifications/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user notification preferences."""
    prefs = current_user.notification_preferences or {}
    
    return NotificationPreferences(
        email_matches=prefs.get("email_matches", True),
        email_messages=prefs.get("email_messages", True),
        email_reports=prefs.get("email_reports", True),
        push_matches=prefs.get("push_matches", True),
        push_messages=prefs.get("push_messages", True),
        push_sessions=prefs.get("push_sessions", True)
    )


@router.put("/notifications/preferences", response_model=NotificationPreferences)
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user notification preferences."""
    from sqlalchemy import select
    
    query = select(User).where(User.id == current_user.id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.notification_preferences = preferences.dict()
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return preferences


@router.post("/verify/request")
async def request_verification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request profile verification."""
    # In production, this would trigger a verification workflow
    # For now, just return a success message
    return {
        "message": "Verification request submitted. You will be notified once your profile is reviewed.",
        "status": "pending"
    }


@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user subscription information."""
    return {
        "tier": current_user.subscription_tier or "free",
        "features": {
            "free": ["Basic matching", "Limited AI sessions", "Basic compatibility reports"],
            "premium": ["Unlimited matching", "Unlimited AI sessions", "Detailed reports", "Priority support"],
            "pro": ["All premium features", "Advanced analytics", "Custom scenarios", "API access"]
        }
    }


@router.put("/subscription", response_model=dict)
async def update_subscription(
    subscription: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user subscription tier."""
    from sqlalchemy import select
    
    valid_tiers = ["free", "premium", "pro"]
    if subscription.tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid subscription tier. Must be one of: {', '.join(valid_tiers)}"
        )
    
    query = select(User).where(User.id == current_user.id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.subscription_tier = subscription.tier
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "message": f"Subscription updated to {subscription.tier}",
        "tier": subscription.tier
    }


@router.get("/dashboard")
async def get_user_dashboard(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive user dashboard data with match history, insights, and recommendations."""
    from app.services.match_service import MatchService
    from app.services.compatibility_service import CompatibilityService
    from app.models.match import Match, MatchStatus, MatchSession, MatchSessionStatus
    from app.models.conversation import Conversation
    from app.models.notification import Notification
    from sqlalchemy import select, func, and_, or_, desc
    from datetime import datetime, timedelta
    
    user_id = str(current_user.id)
    match_service = MatchService(db)
    compatibility_service = CompatibilityService(db)
    
    # Get match statistics
    mutual_matches_query = select(func.count(Match.id)).where(
        and_(
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
            Match.status == MatchStatus.MUTUAL
        )
    )
    mutual_matches_result = await db.execute(mutual_matches_query)
    total_matches = mutual_matches_result.scalar() or 0
    
    # Get active conversations count
    active_conversations_query = select(func.count(Conversation.id)).where(
        and_(
            or_(Conversation.user1_id == user_id, Conversation.user2_id == user_id),
            Conversation.status == "active"
        )
    )
    active_conversations_result = await db.execute(active_conversations_query)
    active_conversations = active_conversations_result.scalar() or 0
    
    # Get compatibility reports count
    compatibility_reports_query = select(func.count()).select_from(
        select(Match.id).where(
            and_(
                or_(Match.user1_id == user_id, Match.user2_id == user_id),
                Match.compatibility_score.isnot(None)
            )
        ).subquery()
    )
    compatibility_reports_result = await db.execute(compatibility_reports_query)
    compatibility_reports = compatibility_reports_result.scalar() or 0
    
    # Get AI sessions count
    ai_sessions_query = select(func.count(MatchSession.id)).where(
        and_(
            or_(MatchSession.user1_id == user_id, MatchSession.user2_id == user_id),
            MatchSession.status == MatchSessionStatus.COMPLETED
        )
    )
    ai_sessions_result = await db.execute(ai_sessions_query)
    ai_sessions = ai_sessions_result.scalar() or 0
    
    # Get recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Recent matches
    recent_matches_query = select(Match).where(
        and_(
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
            Match.status == MatchStatus.MUTUAL,
            Match.created_at >= thirty_days_ago
        )
    ).order_by(desc(Match.created_at)).limit(10)
    recent_matches_result = await db.execute(recent_matches_query)
    recent_matches = recent_matches_result.scalars().all()
    
    # Recent sessions
    recent_sessions_query = select(MatchSession).where(
        and_(
            or_(MatchSession.user1_id == user_id, MatchSession.user2_id == user_id),
            MatchSession.created_at >= thirty_days_ago
        )
    ).order_by(desc(MatchSession.created_at)).limit(10)
    recent_sessions_result = await db.execute(recent_sessions_query)
    recent_sessions = recent_sessions_result.scalars().all()
    
    # Build activity feed
    activity_feed = []
    
    for match in recent_matches:
        activity_feed.append({
            "type": "match",
            "message": "New mutual match!",
            "timestamp": match.created_at.isoformat(),
            "match_id": str(match.id)
        })
    
    for session in recent_sessions:
        if session.status == MatchSessionStatus.COMPLETED:
            activity_feed.append({
                "type": "session_completed",
                "message": f"AI conversation completed",
                "timestamp": session.ended_at.isoformat() if session.ended_at else session.created_at.isoformat(),
                "session_id": str(session.id)
            })
    
    # Sort activity feed by timestamp
    activity_feed.sort(key=lambda x: x["timestamp"], reverse=True)
    activity_feed = activity_feed[:20]  # Limit to 20 most recent items
    
    # Get compatibility trends (average scores over time)
    compatibility_trends_query = select(
        func.date_trunc('week', Match.created_at).label('week'),
        func.avg(Match.compatibility_score).label('avg_score')
    ).where(
        and_(
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
            Match.compatibility_score.isnot(None),
            Match.created_at >= thirty_days_ago
        )
    ).group_by('week').order_by('week')
    
    compatibility_trends_result = await db.execute(compatibility_trends_query)
    compatibility_trends = [
        {
            "week": row.week.isoformat() if row.week else None,
            "avg_score": float(row.avg_score) if row.avg_score else 0.0
        }
        for row in compatibility_trends_result
    ]
    
    # Get personalized recommendations
    recommendations = []
    
    # Check profile completeness
    if not current_user.personality_profile or (
        current_user.personality_profile and 
        current_user.personality_profile.completeness_score < 0.8
    ):
        recommendations.append({
            "type": "profile",
            "priority": "high",
            "message": "Complete your personality assessment to improve match quality",
            "action_url": "/personality-assessment"
        })
    
    # Check for photos
    if not current_user.photos or len(current_user.photos) == 0:
        recommendations.append({
            "type": "photos",
            "priority": "high",
            "message": "Add photos to your profile to attract more matches",
            "action_url": "/profile/photos"
        })
    
    # Check for bio
    if not current_user.bio or len(current_user.bio) < 50:
        recommendations.append({
            "type": "bio",
            "priority": "medium",
            "message": "Write a compelling bio to showcase your personality",
            "action_url": "/profile/edit"
        })
    
    # Suggest exploring matches if they have few
    if total_matches < 3:
        recommendations.append({
            "type": "discovery",
            "priority": "medium",
            "message": "Explore potential matches to find compatible partners",
            "action_url": "/discover"
        })
    
    # Suggest AI conversations if they haven't tried
    if ai_sessions == 0 and total_matches > 0:
        recommendations.append({
            "type": "ai_session",
            "priority": "medium",
            "message": "Try an AI conversation to assess compatibility",
            "action_url": "/matches"
        })
    
    # Get unread notifications count
    unread_notifications_query = select(func.count(Notification.id)).where(
        and_(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    )
    unread_notifications_result = await db.execute(unread_notifications_query)
    unread_notifications = unread_notifications_result.scalar() or 0
    
    return {
        "stats": {
            "total_matches": total_matches,
            "active_conversations": active_conversations,
            "compatibility_reports": compatibility_reports,
            "ai_sessions": ai_sessions,
            "unread_notifications": unread_notifications
        },
        "activity_feed": activity_feed,
        "compatibility_trends": compatibility_trends,
        "recommendations": recommendations,
        "profile_completeness": current_user.personality_profile.completeness_score if current_user.personality_profile else 0.0
    }