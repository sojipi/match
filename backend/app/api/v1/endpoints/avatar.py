"""
AI Avatar management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.user import User
from app.models.avatar import AIAvatar, AvatarCustomization, AvatarTrainingSession
from app.services.avatar_service import AvatarService

router = APIRouter()


class AvatarResponse(BaseModel):
    """AI Avatar response model."""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    avatar_version: str
    personality_traits: Dict[str, Any] = Field(default_factory=dict)
    communication_patterns: Dict[str, Any] = Field(default_factory=dict)
    response_style: Dict[str, Any] = Field(default_factory=dict)
    conversation_skills: Dict[str, Any] = Field(default_factory=dict)
    emotional_range: Dict[str, Any] = Field(default_factory=dict)
    completeness_score: float
    authenticity_score: float
    consistency_score: float
    status: str
    improvement_areas: List[str] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
    training_iterations: int
    last_training_date: Optional[str] = None
    created_at: str
    updated_at: str


class AvatarCustomizationRequest(BaseModel):
    """Request to customize avatar."""
    customization_type: str  # "personality_adjustment", "communication_style", "response_style"
    field_name: str
    custom_value: Any
    reason: Optional[str] = None


class AvatarCustomizationResponse(BaseModel):
    """Avatar customization response."""
    id: str
    avatar_id: str
    customization_type: str
    field_name: str
    original_value: Any
    custom_value: Any
    reason: Optional[str] = None
    confidence: float
    impact_score: float
    is_active: bool
    created_at: str


class AvatarCompletenessAnalysis(BaseModel):
    """Avatar completeness analysis response."""
    overall_score: float
    authenticity_score: float
    consistency_score: float
    areas: Dict[str, Dict[str, Any]]
    improvement_areas: List[str]
    suggested_actions: List[str]
    training_status: Dict[str, Any]


class AvatarTrainingResponse(BaseModel):
    """Avatar training session response."""
    id: str
    avatar_id: str
    training_type: str
    trigger_reason: str
    success: bool
    error_message: Optional[str] = None
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[int] = None


@router.post("/create/{user_id}", response_model=AvatarResponse)
async def create_avatar(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Create AI avatar from user's personality profile."""
    
    # Check if user exists and load personality profile
    result = await db.execute(
        select(User)
        .options(selectinload(User.personality_profile))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has personality profile
    if not user.personality_profile:
        raise HTTPException(
            status_code=400, 
            detail="User must complete personality assessment before creating avatar"
        )
    
    try:
        avatar_service = AvatarService(db)
        avatar = await avatar_service.create_avatar_from_personality(
            str(user_id), 
            str(user.personality_profile.id)
        )
        
        return AvatarResponse(
            id=str(avatar.id),
            user_id=str(avatar.user_id),
            name=avatar.name,
            description=avatar.description,
            avatar_version=avatar.avatar_version,
            personality_traits=avatar.personality_traits,
            communication_patterns=avatar.communication_patterns,
            response_style=avatar.response_style,
            conversation_skills=avatar.conversation_skills,
            emotional_range=avatar.emotional_range,
            completeness_score=avatar.completeness_score,
            authenticity_score=avatar.authenticity_score,
            consistency_score=avatar.consistency_score,
            status=avatar.status,
            improvement_areas=avatar.improvement_areas,
            suggested_actions=avatar.suggested_actions,
            training_iterations=avatar.training_iterations,
            last_training_date=avatar.last_training_date.isoformat() if avatar.last_training_date else None,
            created_at=avatar.created_at.isoformat() if avatar.created_at else datetime.utcnow().isoformat(),
            updated_at=avatar.updated_at.isoformat() if avatar.updated_at else datetime.utcnow().isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the actual error for debugging
        import logging
        logging.error(f"Avatar creation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create avatar: {str(e)}")


@router.get("/{user_id}", response_model=AvatarResponse)
async def get_avatar(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get user's AI avatar."""
    
    avatar_service = AvatarService(db)
    avatar = await avatar_service.get_avatar_by_user_id(str(user_id))
    
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    return AvatarResponse(
        id=str(avatar.id),
        user_id=str(avatar.user_id),
        name=avatar.name,
        description=avatar.description,
        avatar_version=avatar.avatar_version,
        personality_traits=avatar.personality_traits,
        communication_patterns=avatar.communication_patterns,
        response_style=avatar.response_style,
        conversation_skills=avatar.conversation_skills,
        emotional_range=avatar.emotional_range,
        completeness_score=avatar.completeness_score,
        authenticity_score=avatar.authenticity_score,
        consistency_score=avatar.consistency_score,
        status=avatar.status,
        improvement_areas=avatar.improvement_areas,
        suggested_actions=avatar.suggested_actions,
        training_iterations=avatar.training_iterations,
        last_training_date=avatar.last_training_date.isoformat() if avatar.last_training_date else None,
        created_at=avatar.created_at.isoformat() if avatar.created_at else datetime.utcnow().isoformat(),
        updated_at=avatar.updated_at.isoformat() if avatar.updated_at else datetime.utcnow().isoformat()
    )


@router.put("/update/{user_id}", response_model=AvatarResponse)
async def update_avatar_from_personality(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Update avatar when personality profile changes."""
    
    # Check if user exists and has personality profile
    result = await db.execute(
        select(User)
        .options(selectinload(User.personality_profile))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.personality_profile:
        raise HTTPException(status_code=400, detail="User has no personality profile")
    
    try:
        avatar_service = AvatarService(db)
        avatar = await avatar_service.get_avatar_by_user_id(str(user_id))
        
        if not avatar:
            # Create new avatar if none exists
            avatar = await avatar_service.create_avatar_from_personality(
                str(user_id), 
                str(user.personality_profile.id)
            )
        else:
            # Update existing avatar
            avatar = await avatar_service.update_avatar_from_personality(
                str(avatar.id),
                str(user.personality_profile.id)
            )
        
        return AvatarResponse(
            id=str(avatar.id),
            user_id=str(avatar.user_id),
            name=avatar.name,
            description=avatar.description,
            avatar_version=avatar.avatar_version,
            personality_traits=avatar.personality_traits,
            communication_patterns=avatar.communication_patterns,
            response_style=avatar.response_style,
            conversation_skills=avatar.conversation_skills,
            emotional_range=avatar.emotional_range,
            completeness_score=avatar.completeness_score,
            authenticity_score=avatar.authenticity_score,
            consistency_score=avatar.consistency_score,
            status=avatar.status,
            improvement_areas=avatar.improvement_areas,
            suggested_actions=avatar.suggested_actions,
            training_iterations=avatar.training_iterations,
            last_training_date=avatar.last_training_date.isoformat() if avatar.last_training_date else None,
            created_at=avatar.created_at.isoformat() if avatar.created_at else datetime.utcnow().isoformat(),
            updated_at=avatar.updated_at.isoformat() if avatar.updated_at else datetime.utcnow().isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the actual error for debugging
        import logging
        logging.error(f"Avatar update failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update avatar: {str(e)}")


@router.post("/{avatar_id}/customize", response_model=AvatarCustomizationResponse)
async def customize_avatar(
    avatar_id: UUID,
    customization_data: AvatarCustomizationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Apply user customization to avatar."""
    
    try:
        avatar_service = AvatarService(db)
        customization = await avatar_service.customize_avatar(
            str(avatar_id),
            customization_data.customization_type,
            customization_data.field_name,
            customization_data.custom_value,
            customization_data.reason
        )
        
        return AvatarCustomizationResponse(
            id=str(customization.id),
            avatar_id=str(customization.avatar_id),
            customization_type=customization.customization_type,
            field_name=customization.field_name,
            original_value=customization.original_value,
            custom_value=customization.custom_value,
            reason=customization.reason,
            confidence=customization.confidence,
            impact_score=customization.impact_score,
            is_active=customization.is_active,
            created_at=customization.created_at.isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to customize avatar")


@router.get("/{avatar_id}/customizations", response_model=List[AvatarCustomizationResponse])
async def get_avatar_customizations(
    avatar_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all customizations for an avatar."""
    
    result = await db.execute(
        select(AvatarCustomization)
        .where(AvatarCustomization.avatar_id == avatar_id)
        .where(AvatarCustomization.is_active == True)
    )
    customizations = result.scalars().all()
    
    return [
        AvatarCustomizationResponse(
            id=str(customization.id),
            avatar_id=str(customization.avatar_id),
            customization_type=customization.customization_type,
            field_name=customization.field_name,
            original_value=customization.original_value,
            custom_value=customization.custom_value,
            reason=customization.reason,
            confidence=customization.confidence,
            impact_score=customization.impact_score,
            is_active=customization.is_active,
            created_at=customization.created_at.isoformat()
        )
        for customization in customizations
    ]


@router.get("/{avatar_id}/completeness", response_model=AvatarCompletenessAnalysis)
async def get_avatar_completeness_analysis(
    avatar_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed completeness analysis and improvement suggestions."""
    
    try:
        avatar_service = AvatarService(db)
        analysis = await avatar_service.get_avatar_completeness_analysis(str(avatar_id))
        
        return AvatarCompletenessAnalysis(
            overall_score=analysis["overall_score"],
            authenticity_score=analysis["authenticity_score"],
            consistency_score=analysis["consistency_score"],
            areas=analysis["areas"],
            improvement_areas=analysis["improvement_areas"],
            suggested_actions=analysis["suggested_actions"],
            training_status=analysis["training_status"]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to analyze avatar completeness")


@router.get("/{avatar_id}/training-history", response_model=List[AvatarTrainingResponse])
async def get_avatar_training_history(
    avatar_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get avatar training history."""
    
    result = await db.execute(
        select(AvatarTrainingSession)
        .where(AvatarTrainingSession.avatar_id == avatar_id)
        .order_by(AvatarTrainingSession.started_at.desc())
    )
    training_sessions = result.scalars().all()
    
    return [
        AvatarTrainingResponse(
            id=str(session.id),
            avatar_id=str(session.avatar_id),
            training_type=session.training_type,
            trigger_reason=session.trigger_reason,
            success=session.success,
            error_message=session.error_message,
            started_at=session.started_at.isoformat(),
            completed_at=session.completed_at.isoformat() if session.completed_at else None,
            duration_seconds=session.duration_seconds
        )
        for session in training_sessions
    ]


@router.post("/{avatar_id}/retrain", response_model=AvatarResponse)
async def retrain_avatar(
    avatar_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger avatar retraining."""
    
    # Get avatar
    result = await db.execute(select(AIAvatar).where(AIAvatar.id == avatar_id))
    avatar = result.scalar_one_or_none()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    try:
        avatar_service = AvatarService(db)
        
        # Start retraining
        await avatar_service._start_avatar_training(
            str(avatar_id), 
            "manual_retrain", 
            "User requested retraining"
        )
        
        # Get updated avatar
        result = await db.execute(select(AIAvatar).where(AIAvatar.id == avatar_id))
        updated_avatar = result.scalar_one()
        
        return AvatarResponse(
            id=str(updated_avatar.id),
            user_id=str(updated_avatar.user_id),
            name=updated_avatar.name,
            description=updated_avatar.description,
            avatar_version=updated_avatar.avatar_version,
            personality_traits=updated_avatar.personality_traits,
            communication_patterns=updated_avatar.communication_patterns,
            response_style=updated_avatar.response_style,
            conversation_skills=updated_avatar.conversation_skills,
            emotional_range=updated_avatar.emotional_range,
            completeness_score=updated_avatar.completeness_score,
            authenticity_score=updated_avatar.authenticity_score,
            consistency_score=updated_avatar.consistency_score,
            status=updated_avatar.status,
            improvement_areas=updated_avatar.improvement_areas,
            suggested_actions=updated_avatar.suggested_actions,
            training_iterations=updated_avatar.training_iterations,
            last_training_date=updated_avatar.last_training_date.isoformat() if updated_avatar.last_training_date else None,
            created_at=updated_avatar.created_at.isoformat() if updated_avatar.created_at else datetime.utcnow().isoformat(),
            updated_at=updated_avatar.updated_at.isoformat() if updated_avatar.updated_at else datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrain avatar")