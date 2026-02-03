"""
Match discovery and management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List

from app.core.database import get_db
from app.services.match_service import MatchService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


class PotentialMatch(BaseModel):
    """Potential match data."""
    user_id: str
    display_name: str
    age: Optional[int] = None
    location: str
    primary_photo_url: Optional[str] = None
    bio_preview: str
    compatibility_preview: float
    shared_interests: List[str] = []
    personality_highlights: List[str] = []
    is_online: bool = False
    mutual_connections: int = 0


class MatchFilters(BaseModel):
    """Match discovery filters."""
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    max_distance: Optional[int] = None
    interests: Optional[List[str]] = None


class MatchDiscoveryResponse(BaseModel):
    """Match discovery response."""
    matches: List[PotentialMatch]
    total_count: int
    has_more: bool
    filters_applied: Optional[MatchFilters] = None
    recommendations: List[str] = []


class LikeResponse(BaseModel):
    """Like action response."""
    message: str
    is_mutual: bool
    match_id: str


class PassResponse(BaseModel):
    """Pass action response."""
    message: str


class MatchHistoryItem(BaseModel):
    """Match history item."""
    id: str
    user: dict
    compatibility_score: float
    status: str
    conversation_count: int
    last_interaction: Optional[str] = None
    created_at: str


class MatchHistoryResponse(BaseModel):
    """Match history response."""
    matches: List[MatchHistoryItem]


@router.get("/discover", response_model=MatchDiscoveryResponse)
async def discover_matches(
    limit: int = 10,
    offset: int = 0,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    max_distance: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Discover potential matches."""
    match_service = MatchService(db)
    
    # Build filters
    filters = {}
    if age_min:
        filters['age_min'] = age_min
    if age_max:
        filters['age_max'] = age_max
    if max_distance:
        filters['max_distance'] = max_distance
    
    # Get matches
    matches, total_count = await match_service.discover_matches(
        user_id=str(current_user.id),
        limit=limit,
        offset=offset,
        filters=filters if filters else None
    )
    
    # Convert to response format
    potential_matches = [PotentialMatch(**match) for match in matches]
    
    return MatchDiscoveryResponse(
        matches=potential_matches,
        total_count=total_count,
        has_more=offset + limit < total_count,
        filters_applied=MatchFilters(
            age_min=age_min,
            age_max=age_max,
            max_distance=max_distance
        ) if any([age_min, age_max, max_distance]) else None,
        recommendations=[
            "Try expanding your age range for more matches",
            "Complete your personality assessment for better compatibility",
            "Add more photos to your profile"
        ]
    )


@router.post("/like/{target_user_id}", response_model=LikeResponse)
async def like_user(
    target_user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Like a potential match."""
    match_service = MatchService(db)
    
    try:
        result = await match_service.like_user(
            user_id=str(current_user.id),
            target_user_id=target_user_id
        )
        return LikeResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to like user: {str(e)}"
        )


@router.post("/pass/{target_user_id}", response_model=PassResponse)
async def pass_user(
    target_user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Pass on a potential match."""
    match_service = MatchService(db)
    
    try:
        result = await match_service.pass_user(
            user_id=str(current_user.id),
            target_user_id=target_user_id
        )
        return PassResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to pass on user: {str(e)}"
        )


@router.get("/history", response_model=MatchHistoryResponse)
async def get_match_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's match history."""
    match_service = MatchService(db)
    
    try:
        matches = await match_service.get_match_history(str(current_user.id))
        history_items = [MatchHistoryItem(**match) for match in matches]
        return MatchHistoryResponse(matches=history_items)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get match history: {str(e)}"
        )