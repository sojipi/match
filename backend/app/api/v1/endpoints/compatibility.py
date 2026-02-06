"""
Compatibility analysis and reporting API endpoints.
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.compatibility_service import CompatibilityService

router = APIRouter()


class CompatibilityReportResponse(BaseModel):
    """Compatibility report response."""
    report_id: str
    generated_at: str
    users: dict
    compatibility_scores: dict
    insights: dict
    trends: Optional[dict]
    recommendations: dict
    simulation_summary: dict


class CompatibilityDashboardResponse(BaseModel):
    """Compatibility dashboard response."""
    has_data: bool
    message: Optional[str] = None
    overview: Optional[dict] = None
    dimension_scores: Optional[dict] = None
    progress_over_time: Optional[list] = None
    scenario_performance: Optional[dict] = None
    communication_patterns: Optional[dict] = None
    key_insights: Optional[list] = None
    next_steps: Optional[list] = None


class CompatibilityTrendsResponse(BaseModel):
    """Compatibility trends response."""
    has_trends: bool
    message: Optional[str] = None
    timeline_data: Optional[list] = None
    overall_trend: Optional[str] = None
    collaboration_trend: Optional[str] = None
    improvement_rate: Optional[float] = None
    trend_summary: Optional[str] = None


@router.get("/report", response_model=CompatibilityReportResponse)
async def get_compatibility_report(
    user2_id: str = Query(..., description="ID of the other user"),
    match_id: Optional[str] = Query(None, description="Optional match ID"),
    include_trends: bool = Query(True, description="Include trend analysis"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate comprehensive compatibility report.
    
    Analyzes compatibility between the current user and another user based on
    personality profiles and simulation history. Includes detailed insights,
    recommendations, and trend analysis.
    """
    compatibility_service = CompatibilityService(db)
    
    try:
        report = await compatibility_service.generate_compatibility_report(
            user1_id=str(current_user.id),
            user2_id=user2_id,
            match_id=match_id,
            include_trends=include_trends
        )
        
        return CompatibilityReportResponse(**report)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate compatibility report: {str(e)}")


@router.get("/dashboard", response_model=CompatibilityDashboardResponse)
async def get_compatibility_dashboard(
    user2_id: str = Query(..., description="ID of the other user"),
    match_id: Optional[str] = Query(None, description="Optional match ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get compatibility dashboard data.
    
    Returns interactive dashboard data including charts, metrics, and insights
    for displaying compatibility analysis in a visual format.
    """
    compatibility_service = CompatibilityService(db)
    
    try:
        dashboard_data = await compatibility_service.get_compatibility_dashboard_data(
            user1_id=str(current_user.id),
            user2_id=user2_id,
            match_id=match_id
        )
        
        return CompatibilityDashboardResponse(**dashboard_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


@router.get("/trends", response_model=CompatibilityTrendsResponse)
async def get_compatibility_trends(
    user2_id: str = Query(..., description="ID of the other user"),
    time_period_days: int = Query(30, ge=7, le=365, description="Time period in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get compatibility trends over time.
    
    Analyzes how compatibility has changed over the specified time period
    based on simulation results and interactions.
    """
    compatibility_service = CompatibilityService(db)
    
    try:
        trends = await compatibility_service.track_compatibility_trends(
            user1_id=str(current_user.id),
            user2_id=user2_id,
            time_period_days=time_period_days
        )
        
        return CompatibilityTrendsResponse(**trends)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get compatibility trends: {str(e)}")


@router.get("/scores", response_model=dict)
async def get_compatibility_scores(
    user2_id: str = Query(..., description="ID of the other user"),
    match_id: Optional[str] = Query(None, description="Optional match ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current compatibility scores.
    
    Returns the latest compatibility scores across all dimensions
    without the full report details.
    """
    compatibility_service = CompatibilityService(db)
    
    try:
        # Get users and simulation history
        users = await compatibility_service._get_user_profiles(
            str(current_user.id), user2_id
        )
        if not users:
            raise HTTPException(status_code=404, detail="Users not found")
        
        user1, user2 = users
        simulation_history = await compatibility_service._get_simulation_history(
            str(current_user.id), user2_id, match_id
        )
        
        scores = await compatibility_service._calculate_compatibility_scores(
            user1, user2, simulation_history
        )
        
        return {
            "user1_id": str(current_user.id),
            "user2_id": user2_id,
            "match_id": match_id,
            "scores": scores,
            "last_updated": simulation_history[-1].updated_at.isoformat() if simulation_history else None,
            "sessions_count": len(simulation_history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get compatibility scores: {str(e)}")


@router.get("/insights", response_model=dict)
async def get_compatibility_insights(
    user2_id: str = Query(..., description="ID of the other user"),
    match_id: Optional[str] = Query(None, description="Optional match ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get compatibility insights and analysis.
    
    Returns detailed insights about relationship strengths, challenges,
    and opportunities without the full report.
    """
    compatibility_service = CompatibilityService(db)
    
    try:
        # Get users and simulation history
        users = await compatibility_service._get_user_profiles(
            str(current_user.id), user2_id
        )
        if not users:
            raise HTTPException(status_code=404, detail="Users not found")
        
        user1, user2 = users
        simulation_history = await compatibility_service._get_simulation_history(
            str(current_user.id), user2_id, match_id
        )
        
        scores = await compatibility_service._calculate_compatibility_scores(
            user1, user2, simulation_history
        )
        
        insights = await compatibility_service._generate_compatibility_insights(
            user1, user2, simulation_history, scores
        )
        
        return {
            "user1_id": str(current_user.id),
            "user2_id": user2_id,
            "match_id": match_id,
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get compatibility insights: {str(e)}")


@router.get("/recommendations", response_model=dict)
async def get_compatibility_recommendations(
    user2_id: str = Query(..., description="ID of the other user"),
    match_id: Optional[str] = Query(None, description="Optional match ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get compatibility recommendations.
    
    Returns actionable recommendations for improving compatibility
    based on current analysis.
    """
    compatibility_service = CompatibilityService(db)
    
    try:
        # Get users and simulation history
        users = await compatibility_service._get_user_profiles(
            str(current_user.id), user2_id
        )
        if not users:
            raise HTTPException(status_code=404, detail="Users not found")
        
        user1, user2 = users
        simulation_history = await compatibility_service._get_simulation_history(
            str(current_user.id), user2_id, match_id
        )
        
        scores = await compatibility_service._calculate_compatibility_scores(
            user1, user2, simulation_history
        )
        
        insights = await compatibility_service._generate_compatibility_insights(
            user1, user2, simulation_history, scores
        )
        
        recommendations = await compatibility_service._generate_recommendations(
            user1, user2, scores, insights, simulation_history
        )
        
        return {
            "user1_id": str(current_user.id),
            "user2_id": user2_id,
            "match_id": match_id,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")