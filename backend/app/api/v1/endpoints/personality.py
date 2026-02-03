"""
Personality assessment endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid

from app.core.database import get_db
from app.models.user import User, PersonalityProfile

router = APIRouter()


class PersonalityQuestion(BaseModel):
    """Personality assessment question."""
    id: str
    category: str
    question: str
    question_type: str  # "scale", "multiple_choice", "ranking"
    options: Optional[List[str]] = None
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    scale_labels: Optional[Dict[str, str]] = None


class PersonalityAnswer(BaseModel):
    """User's answer to a personality question."""
    question_id: str
    answer: Any  # Can be int, str, or list depending on question type
    confidence: Optional[float] = None


class PersonalityAssessmentRequest(BaseModel):
    """Request to submit personality assessment answers."""
    answers: List[PersonalityAnswer]
    assessment_version: str = "1.0"


class PersonalityProfileResponse(BaseModel):
    """Personality profile response."""
    id: str
    user_id: str
    openness: Optional[float] = None
    conscientiousness: Optional[float] = None
    extraversion: Optional[float] = None
    agreeableness: Optional[float] = None
    neuroticism: Optional[float] = None
    values: Dict[str, Any] = Field(default_factory=dict)
    communication_style: Optional[str] = None
    conflict_resolution_style: Optional[str] = None
    completeness_score: float = 0.0
    assessment_version: Optional[str] = None
    created_at: str
    updated_at: str


class PersonalityInsight(BaseModel):
    """Real-time personality insight."""
    trait: str
    score: float
    description: str
    confidence: float


class AssessmentProgress(BaseModel):
    """Assessment progress tracking."""
    current_step: int
    total_steps: int
    completion_percentage: float
    estimated_time_remaining: int  # in minutes
    insights: List[PersonalityInsight] = Field(default_factory=list)


# Predefined personality questions
PERSONALITY_QUESTIONS = [
    # Openness questions
    PersonalityQuestion(
        id="open_1",
        category="openness",
        question="I enjoy exploring new ideas and concepts",
        question_type="scale",
        scale_min=1,
        scale_max=7,
        scale_labels={"1": "Strongly Disagree", "4": "Neutral", "7": "Strongly Agree"}
    ),
    PersonalityQuestion(
        id="open_2",
        category="openness",
        question="I prefer routine and familiar experiences",
        question_type="scale",
        scale_min=1,
        scale_max=7,
        scale_labels={"1": "Strongly Disagree", "4": "Neutral", "7": "Strongly Agree"}
    ),
    PersonalityQuestion(
        id="open_3",
        category="openness",
        question="Which activities appeal to you most?",
        question_type="multiple_choice",
        options=["Art galleries and museums", "Outdoor adventures", "Reading and learning", "Social gatherings", "Creative projects"]
    ),
    
    # Conscientiousness questions
    PersonalityQuestion(
        id="cons_1",
        category="conscientiousness",
        question="I am always prepared and organized",
        question_type="scale",
        scale_min=1,
        scale_max=7,
        scale_labels={"1": "Strongly Disagree", "4": "Neutral", "7": "Strongly Agree"}
    ),
    PersonalityQuestion(
        id="cons_2",
        category="conscientiousness",
        question="I often leave tasks until the last minute",
        question_type="scale",
        scale_min=1,
        scale_max=7,
        scale_labels={"1": "Strongly Disagree", "4": "Neutral", "7": "Strongly Agree"}
    ),
    
    # Extraversion questions
    PersonalityQuestion(
        id="extra_1",
        category="extraversion",
        question="I feel energized by social interactions",
        question_type="scale",
        scale_min=1,
        scale_max=7,
        scale_labels={"1": "Strongly Disagree", "4": "Neutral", "7": "Strongly Agree"}
    ),
    PersonalityQuestion(
        id="extra_2",
        category="extraversion",
        question="I prefer quiet, intimate gatherings over large parties",
        question_type="scale",
        scale_min=1,
        scale_max=7,
        scale_labels={"1": "Strongly Disagree", "4": "Neutral", "7": "Strongly Agree"}
    ),
    
    # Agreeableness questions
    PersonalityQuestion(
        id="agree_1",
        category="agreeableness",
        question="I try to be cooperative and avoid conflicts",
        question_type="scale",
        scale_min=1,
        scale_max=7,
        scale_labels={"1": "Strongly Disagree", "4": "Neutral", "7": "Strongly Agree"}
    ),
    PersonalityQuestion(
        id="agree_2",
        category="agreeableness",
        question="I tend to be skeptical of others' motives",
        question_type="scale",
        scale_min=1,
        scale_max=7,
        scale_labels={"1": "Strongly Disagree", "4": "Neutral", "7": "Strongly Agree"}
    ),
    
    # Neuroticism questions
    PersonalityQuestion(
        id="neuro_1",
        category="neuroticism",
        question="I often feel anxious or worried",
        question_type="scale",
        scale_min=1,
        scale_max=7,
        scale_labels={"1": "Strongly Disagree", "4": "Neutral", "7": "Strongly Agree"}
    ),
    PersonalityQuestion(
        id="neuro_2",
        category="neuroticism",
        question="I remain calm under pressure",
        question_type="scale",
        scale_min=1,
        scale_max=7,
        scale_labels={"1": "Strongly Disagree", "4": "Neutral", "7": "Strongly Agree"}
    ),
    
    # Values questions
    PersonalityQuestion(
        id="values_1",
        category="values",
        question="Rank these values by importance to you",
        question_type="ranking",
        options=["Family", "Career Success", "Personal Growth", "Adventure", "Security", "Creativity"]
    ),
    PersonalityQuestion(
        id="values_2",
        category="values",
        question="What matters most in a relationship?",
        question_type="multiple_choice",
        options=["Trust and honesty", "Shared interests", "Physical attraction", "Emotional support", "Intellectual connection"]
    ),
    
    # Communication style questions
    PersonalityQuestion(
        id="comm_1",
        category="communication",
        question="How do you prefer to resolve disagreements?",
        question_type="multiple_choice",
        options=["Direct discussion", "Give it time to cool down", "Seek compromise", "Avoid confrontation", "Get help from others"]
    ),
    PersonalityQuestion(
        id="comm_2",
        category="communication",
        question="Your communication style is more:",
        question_type="multiple_choice",
        options=["Direct and straightforward", "Diplomatic and tactful", "Emotional and expressive", "Logical and analytical"]
    )
]


@router.get("/questions", response_model=List[PersonalityQuestion])
async def get_personality_questions(
    step: Optional[int] = None,
    previous_answers: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get personality assessment questions.
    Supports adaptive questioning based on previous answers.
    """
    # For now, return all questions. In a real implementation,
    # this would adapt based on previous answers
    if step is not None:
        # Return questions for specific step (5 questions per step)
        start_idx = (step - 1) * 5
        end_idx = start_idx + 5
        return PERSONALITY_QUESTIONS[start_idx:end_idx]
    
    return PERSONALITY_QUESTIONS


@router.get("/progress/{user_id}", response_model=AssessmentProgress)
async def get_assessment_progress(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get user's assessment progress and real-time insights."""
    # Check if user exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get existing personality profile if any
    result = await db.execute(
        select(PersonalityProfile).where(PersonalityProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    
    # Calculate progress based on existing data
    total_questions = len(PERSONALITY_QUESTIONS)
    completed_questions = 0
    insights = []
    
    if profile:
        # Count completed traits
        traits = [profile.openness, profile.conscientiousness, profile.extraversion, 
                 profile.agreeableness, profile.neuroticism]
        completed_questions = sum(1 for trait in traits if trait is not None) * 2  # Rough estimate
        
        # Generate insights
        if profile.openness is not None:
            insights.append(PersonalityInsight(
                trait="Openness",
                score=profile.openness,
                description="Your openness to new experiences",
                confidence=0.8
            ))
        if profile.extraversion is not None:
            insights.append(PersonalityInsight(
                trait="Extraversion",
                score=profile.extraversion,
                description="Your social energy and outgoingness",
                confidence=0.8
            ))
    
    completion_percentage = (completed_questions / total_questions) * 100
    estimated_time = max(1, int((total_questions - completed_questions) * 0.5))  # 30 seconds per question
    
    return AssessmentProgress(
        current_step=min(completed_questions // 5 + 1, total_questions // 5),
        total_steps=total_questions // 5,
        completion_percentage=completion_percentage,
        estimated_time_remaining=estimated_time,
        insights=insights
    )


@router.post("/submit", response_model=PersonalityProfileResponse)
async def submit_personality_assessment(
    user_id: UUID,
    assessment_data: PersonalityAssessmentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Submit personality assessment answers and generate profile."""
    # Check if user exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Process answers and calculate personality scores
    scores = _calculate_personality_scores(assessment_data.answers)
    
    # Get or create personality profile
    result = await db.execute(
        select(PersonalityProfile).where(PersonalityProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    
    if profile:
        # Update existing profile
        profile.openness = scores.get("openness")
        profile.conscientiousness = scores.get("conscientiousness")
        profile.extraversion = scores.get("extraversion")
        profile.agreeableness = scores.get("agreeableness")
        profile.neuroticism = scores.get("neuroticism")
        profile.values = scores.get("values", {})
        profile.communication_style = scores.get("communication_style")
        profile.conflict_resolution_style = scores.get("conflict_resolution_style")
        profile.assessment_version = assessment_data.assessment_version
        profile.completeness_score = _calculate_completeness_score(scores)
    else:
        # Create new profile
        profile = PersonalityProfile(
            id=uuid.uuid4(),
            user_id=user_id,
            openness=scores.get("openness"),
            conscientiousness=scores.get("conscientiousness"),
            extraversion=scores.get("extraversion"),
            agreeableness=scores.get("agreeableness"),
            neuroticism=scores.get("neuroticism"),
            values=scores.get("values", {}),
            communication_style=scores.get("communication_style"),
            conflict_resolution_style=scores.get("conflict_resolution_style"),
            assessment_version=assessment_data.assessment_version,
            completeness_score=_calculate_completeness_score(scores)
        )
        db.add(profile)
    
    await db.commit()
    await db.refresh(profile)
    
    return PersonalityProfileResponse(
        id=str(profile.id),
        user_id=str(profile.user_id),
        openness=profile.openness,
        conscientiousness=profile.conscientiousness,
        extraversion=profile.extraversion,
        agreeableness=profile.agreeableness,
        neuroticism=profile.neuroticism,
        values=profile.values,
        communication_style=profile.communication_style,
        conflict_resolution_style=profile.conflict_resolution_style,
        completeness_score=profile.completeness_score,
        assessment_version=profile.assessment_version,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat()
    )


@router.get("/profile/{user_id}", response_model=PersonalityProfileResponse)
async def get_personality_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get user's personality profile."""
    result = await db.execute(
        select(PersonalityProfile).where(PersonalityProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Personality profile not found")
    
    return PersonalityProfileResponse(
        id=str(profile.id),
        user_id=str(profile.user_id),
        openness=profile.openness,
        conscientiousness=profile.conscientiousness,
        extraversion=profile.extraversion,
        agreeableness=profile.agreeableness,
        neuroticism=profile.neuroticism,
        values=profile.values,
        communication_style=profile.communication_style,
        conflict_resolution_style=profile.conflict_resolution_style,
        completeness_score=profile.completeness_score,
        assessment_version=profile.assessment_version,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat()
    )


def _calculate_personality_scores(answers: List[PersonalityAnswer]) -> Dict[str, Any]:
    """Calculate personality scores from assessment answers."""
    scores = {
        "openness": 0.0,
        "conscientiousness": 0.0,
        "extraversion": 0.0,
        "agreeableness": 0.0,
        "neuroticism": 0.0,
        "values": {},
        "communication_style": None,
        "conflict_resolution_style": None
    }
    
    # Create answer lookup
    answer_map = {answer.question_id: answer.answer for answer in answers}
    
    # Calculate Big Five scores (simplified algorithm)
    # Openness
    open_scores = []
    if "open_1" in answer_map:
        open_scores.append(answer_map["open_1"] / 7.0)
    if "open_2" in answer_map:
        open_scores.append(1.0 - (answer_map["open_2"] / 7.0))  # Reverse scored
    if open_scores:
        scores["openness"] = sum(open_scores) / len(open_scores)
    
    # Conscientiousness
    cons_scores = []
    if "cons_1" in answer_map:
        cons_scores.append(answer_map["cons_1"] / 7.0)
    if "cons_2" in answer_map:
        cons_scores.append(1.0 - (answer_map["cons_2"] / 7.0))  # Reverse scored
    if cons_scores:
        scores["conscientiousness"] = sum(cons_scores) / len(cons_scores)
    
    # Extraversion
    extra_scores = []
    if "extra_1" in answer_map:
        extra_scores.append(answer_map["extra_1"] / 7.0)
    if "extra_2" in answer_map:
        extra_scores.append(1.0 - (answer_map["extra_2"] / 7.0))  # Reverse scored
    if extra_scores:
        scores["extraversion"] = sum(extra_scores) / len(extra_scores)
    
    # Agreeableness
    agree_scores = []
    if "agree_1" in answer_map:
        agree_scores.append(answer_map["agree_1"] / 7.0)
    if "agree_2" in answer_map:
        agree_scores.append(1.0 - (answer_map["agree_2"] / 7.0))  # Reverse scored
    if agree_scores:
        scores["agreeableness"] = sum(agree_scores) / len(agree_scores)
    
    # Neuroticism
    neuro_scores = []
    if "neuro_1" in answer_map:
        neuro_scores.append(answer_map["neuro_1"] / 7.0)
    if "neuro_2" in answer_map:
        neuro_scores.append(1.0 - (answer_map["neuro_2"] / 7.0))  # Reverse scored
    if neuro_scores:
        scores["neuroticism"] = sum(neuro_scores) / len(neuro_scores)
    
    # Process values
    if "values_1" in answer_map and isinstance(answer_map["values_1"], list):
        # Convert ranking to importance scores
        values_ranking = answer_map["values_1"]
        for i, value in enumerate(values_ranking):
            scores["values"][value] = 1.0 - (i / len(values_ranking))
    
    # Communication style
    if "comm_2" in answer_map:
        comm_styles = ["Direct and straightforward", "Diplomatic and tactful", 
                      "Emotional and expressive", "Logical and analytical"]
        if answer_map["comm_2"] in comm_styles:
            scores["communication_style"] = answer_map["comm_2"]
    
    # Conflict resolution style
    if "comm_1" in answer_map:
        conflict_styles = ["Direct discussion", "Give it time to cool down", 
                          "Seek compromise", "Avoid confrontation", "Get help from others"]
        if answer_map["comm_1"] in conflict_styles:
            scores["conflict_resolution_style"] = answer_map["comm_1"]
    
    return scores


def _calculate_completeness_score(scores: Dict[str, Any]) -> float:
    """Calculate profile completeness score."""
    required_fields = ["openness", "conscientiousness", "extraversion", 
                      "agreeableness", "neuroticism"]
    completed_fields = sum(1 for field in required_fields if scores.get(field) is not None)
    
    base_score = completed_fields / len(required_fields)
    
    # Bonus for additional data
    if scores.get("values"):
        base_score += 0.1
    if scores.get("communication_style"):
        base_score += 0.05
    if scores.get("conflict_resolution_style"):
        base_score += 0.05
    
    return min(1.0, base_score)