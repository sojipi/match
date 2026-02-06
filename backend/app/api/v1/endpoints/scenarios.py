"""
Scenario and simulation API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.scenario_service import ScenarioService

router = APIRouter()


class ScenarioResponse(BaseModel):
    """Scenario template response."""
    id: str
    name: str
    title: str
    description: str
    category: str
    difficulty_level: int
    estimated_duration_minutes: int
    personality_dimensions: List[str]
    value_dimensions: List[str]
    tags: List[str]
    user_rating: float
    usage_count: int
    success_rate: float
    content_warnings: List[str]


class ScenarioRecommendationResponse(BaseModel):
    """Scenario recommendation response."""
    id: str
    name: str
    title: str
    description: str
    category: str
    difficulty_level: int
    estimated_duration_minutes: int
    personality_match_score: float
    tags: List[str]
    user_rating: float


class CreateSimulationRequest(BaseModel):
    """Request to create a simulation session."""
    user2_id: str = Field(..., description="ID of the other user")
    scenario_id: str = Field(..., description="ID of the scenario template")
    match_id: Optional[str] = Field(None, description="Optional match ID")
    cultural_context: Optional[str] = Field(None, description="Cultural adaptation context")
    language: str = Field("en", description="Language preference")


class SimulationSessionResponse(BaseModel):
    """Simulation session response."""
    session_id: str
    match_id: Optional[str]
    scenario: dict
    participants: List[dict]
    status: str
    current_phase: str
    started_at: Optional[str]
    ended_at: Optional[str]
    duration_seconds: Optional[int]
    message_count: int
    engagement_score: float
    scenario_completion_score: Optional[float]
    collaboration_score: Optional[float]
    messages: List[dict]


class SimulationMessageRequest(BaseModel):
    """Request to add a message to simulation."""
    content: str = Field(..., description="Message content")
    sender_type: str = Field("user_avatar", description="Type of sender")
    message_type: str = Field("text", description="Type of message")


class SimulationMessageResponse(BaseModel):
    """Simulation message response."""
    message_id: str
    sender_name: str
    sender_type: str
    content: str
    message_type: str
    scenario_phase: str
    turn_number: int
    timestamp: str


@router.get("/library", response_model=List[ScenarioResponse])
async def get_scenario_library(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[int] = Query(None, ge=1, le=5, description="Filter by difficulty level"),
    cultural_context: Optional[str] = Query(None, description="Cultural adaptation context"),
    language: str = Query("en", description="Language preference"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get available scenarios from the library.
    
    Returns a list of scenario templates that can be used for simulations,
    optionally filtered by category, difficulty, and cultural context.
    """
    scenario_service = ScenarioService(db)
    
    try:
        scenarios = await scenario_service.get_scenario_library(
            category=category,
            difficulty=difficulty,
            cultural_context=cultural_context,
            language=language
        )
        
        return [ScenarioResponse(**scenario) for scenario in scenarios]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scenario library: {str(e)}")


@router.get("/recommendations", response_model=List[ScenarioRecommendationResponse])
async def get_scenario_recommendations(
    user2_id: str = Query(..., description="ID of the other user"),
    match_id: Optional[str] = Query(None, description="Optional match ID"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of recommendations"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized scenario recommendations based on user personalities.
    
    Analyzes the personalities of both users and their match history to
    recommend scenarios that would be most insightful for their compatibility.
    """
    scenario_service = ScenarioService(db)
    
    try:
        recommendations = await scenario_service.get_recommended_scenarios(
            user1_id=str(current_user.id),
            user2_id=user2_id,
            match_id=match_id,
            limit=limit
        )
        
        return [ScenarioRecommendationResponse(**rec) for rec in recommendations]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.post("/simulations", response_model=dict)
async def create_simulation_session(
    request: CreateSimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new simulation session.
    
    Creates a simulation session between the current user and another user
    using the specified scenario template. The session will be culturally
    adapted based on the provided context and language.
    """
    scenario_service = ScenarioService(db)
    
    try:
        session_data = await scenario_service.create_simulation_session(
            user1_id=str(current_user.id),
            user2_id=request.user2_id,
            scenario_id=request.scenario_id,
            match_id=request.match_id,
            cultural_context=request.cultural_context,
            language=request.language
        )
        
        return session_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create simulation: {str(e)}")


@router.post("/simulations/{session_id}/start", response_model=dict)
async def start_simulation(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a simulation session.
    
    Begins the simulation by presenting the scenario to the participants
    and transitioning the session to active status.
    """
    scenario_service = ScenarioService(db)
    
    try:
        session_data = await scenario_service.start_simulation(session_id)
        return session_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start simulation: {str(e)}")


@router.get("/simulations/{session_id}", response_model=SimulationSessionResponse)
async def get_simulation_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get simulation session details.
    
    Returns comprehensive information about a simulation session including
    messages, current status, and progress metrics.
    """
    scenario_service = ScenarioService(db)
    
    try:
        session_data = await scenario_service.get_simulation_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Simulation session not found")
        
        # Check if user is a participant
        user_id = str(current_user.id)
        participant_ids = [p["user_id"] for p in session_data["participants"]]
        
        if user_id not in participant_ids:
            raise HTTPException(status_code=403, detail="Access denied to this simulation session")
        
        return SimulationSessionResponse(**session_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get simulation session: {str(e)}")


@router.post("/simulations/{session_id}/messages", response_model=SimulationMessageResponse)
async def add_simulation_message(
    session_id: str,
    request: SimulationMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a message to a simulation session.
    
    Adds a message from the current user's avatar to the simulation session.
    This is typically used by AI agents representing the users.
    """
    scenario_service = ScenarioService(db)
    
    try:
        # Verify user has access to this session
        session_data = await scenario_service.get_simulation_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Simulation session not found")
        
        user_id = str(current_user.id)
        participant_ids = [p["user_id"] for p in session_data["participants"]]
        
        if user_id not in participant_ids:
            raise HTTPException(status_code=403, detail="Access denied to this simulation session")
        
        # Add message
        message_data = await scenario_service.add_simulation_message(
            session_id=session_id,
            sender_id=user_id,
            sender_type=request.sender_type,
            sender_name=f"{current_user.first_name} {current_user.last_name[0]}.",
            content=request.content,
            message_type=request.message_type
        )
        
        return SimulationMessageResponse(**message_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


@router.post("/simulations/{session_id}/complete", response_model=dict)
async def complete_simulation(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Complete a simulation session.
    
    Ends the simulation session and generates comprehensive results
    including compatibility analysis and recommendations.
    """
    scenario_service = ScenarioService(db)
    
    try:
        # Verify user has access to this session
        session_data = await scenario_service.get_simulation_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Simulation session not found")
        
        user_id = str(current_user.id)
        participant_ids = [p["user_id"] for p in session_data["participants"]]
        
        if user_id not in participant_ids:
            raise HTTPException(status_code=403, detail="Access denied to this simulation session")
        
        # Complete simulation
        completion_data = await scenario_service.complete_simulation(session_id)
        return completion_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete simulation: {str(e)}")


@router.get("/categories", response_model=List[dict])
async def get_scenario_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get available scenario categories.
    
    Returns a list of all available scenario categories with descriptions.
    """
    categories = [
        {"value": "financial", "label": "Financial Decisions", "description": "Money management and financial planning scenarios"},
        {"value": "family", "label": "Family Matters", "description": "Family relationships and parenting scenarios"},
        {"value": "lifestyle", "label": "Lifestyle Choices", "description": "Daily life and lifestyle preference scenarios"},
        {"value": "career", "label": "Career & Work", "description": "Professional life and career decision scenarios"},
        {"value": "social", "label": "Social Situations", "description": "Social interactions and friendship scenarios"},
        {"value": "conflict_resolution", "label": "Conflict Resolution", "description": "Disagreement and conflict handling scenarios"},
        {"value": "values", "label": "Values & Beliefs", "description": "Core values and belief system scenarios"},
        {"value": "communication", "label": "Communication", "description": "Communication style and expression scenarios"},
        {"value": "future_planning", "label": "Future Planning", "description": "Long-term goals and planning scenarios"},
        {"value": "daily_life", "label": "Daily Life", "description": "Everyday situations and routine scenarios"}
    ]
    
    return categories


@router.get("/difficulty-levels", response_model=List[dict])
async def get_difficulty_levels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get available difficulty levels.
    
    Returns a list of difficulty levels with descriptions.
    """
    levels = [
        {"value": 1, "label": "Easy", "description": "Simple scenarios for getting started"},
        {"value": 2, "label": "Moderate", "description": "Standard scenarios with some complexity"},
        {"value": 3, "label": "Challenging", "description": "Complex scenarios requiring deeper discussion"},
        {"value": 4, "label": "Difficult", "description": "Advanced scenarios with multiple considerations"},
        {"value": 5, "label": "Expert", "description": "Highly complex scenarios for experienced users"}
    ]
    
    return levels