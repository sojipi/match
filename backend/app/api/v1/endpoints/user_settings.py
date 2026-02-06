"""
User settings API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


class UserSettingsUpdate(BaseModel):
    """User settings update model."""
    gemini_api_key: Optional[str] = None


class UserSettingsResponse(BaseModel):
    """User settings response model."""
    gemini_api_key: Optional[str] = None


@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user settings."""
    # Mask the API key for security (show only last 4 characters)
    masked_key = None
    if hasattr(current_user, 'gemini_api_key') and current_user.gemini_api_key:
        key = current_user.gemini_api_key
        if len(key) > 8:
            masked_key = f"{'*' * (len(key) - 4)}{key[-4:]}"
        else:
            masked_key = "*" * len(key)
    
    return UserSettingsResponse(
        gemini_api_key=masked_key
    )


@router.put("/settings")
async def update_user_settings(
    settings: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user settings."""
    try:
        # Update user's Gemini API key
        if settings.gemini_api_key is not None:
            # Validate API key format (basic validation)
            if settings.gemini_api_key and not settings.gemini_api_key.startswith('AIza'):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid Gemini API key format. Key should start with 'AIza'"
                )
            
            # Update in database
            await db.execute(
                update(User)
                .where(User.id == current_user.id)
                .values(gemini_api_key=settings.gemini_api_key)
            )
            await db.commit()
        
        return {"message": "Settings updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")