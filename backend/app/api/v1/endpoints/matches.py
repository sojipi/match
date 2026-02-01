"""
Match discovery and management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List

from app.core.database import get_db

router = APIRouter()


class PotentialMatch(BaseModel):
    """Potential match data."""
    user_id: str
    display_name: str
    age: int
    location: str
    primary_photo_url: Optional[str] = None
    bio_preview: str
    compatibility_preview: float
    shared_interests: List[str] = []
    is_online: bool = False


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


@router.get("/discover", response_model=MatchDiscoveryResponse)
async def discover_matches(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Discover potential matches."""
    # This is a placeholder - implement actual match discovery
    mock_matches = [
        PotentialMatch(
            user_id=f"user-{i}",
            display_name=f"User {i}",
            age=25 + i,
            location="San Francisco, CA",
            bio_preview="Looking for meaningful connections...",
            compatibility_preview=0.85 - (i * 0.05),
            shared_interests=["hiking", "reading"],
            is_online=i % 2 == 0
        )
        for i in range(1, 6)
    ]
    
    return MatchDiscoveryResponse(
        matches=mock_matches[offset:offset + limit],
        total_count=len(mock_matches),
        has_more=offset + limit < len(mock_matches)
    )


@router.post("/like/{user_id}")
async def like_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Like a potential match."""
    # This is a placeholder - implement actual like functionality
    return {"message": f"Liked user {user_id}", "is_mutual": False}


@router.post("/pass/{user_id}")
async def pass_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Pass on a potential match."""
    # This is a placeholder - implement actual pass functionality
    return {"message": f"Passed on user {user_id}"}


@router.get("/history")
async def get_match_history(
    db: AsyncSession = Depends(get_db)
):
    """Get user's match history."""
    # This is a placeholder - implement actual match history
    return {
        "matches": [
            {
                "id": "match-1",
                "user": {"name": "Sarah", "photo_url": None},
                "compatibility_score": 0.89,
                "status": "mutual",
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": "match-2",
                "user": {"name": "Alex", "photo_url": None},
                "compatibility_score": 0.76,
                "status": "mutual",
                "created_at": "2024-01-14T15:20:00Z"
            }
        ]
    }