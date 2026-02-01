"""
Scenario and simulation data models.

Contains data classes for scenarios, scenario results, and compatibility reports.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from .enums import ScenarioCategory


class Scenario(BaseModel):
    """A marriage simulation scenario."""
    
    scenario_id: str = Field(description="Unique scenario identifier")
    category: ScenarioCategory = Field(description="Scenario category")
    title: str = Field(description="Scenario title")
    description: str = Field(description="Detailed scenario description")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context and parameters"
    )
    difficulty_level: int = Field(
        ge=1, le=10,
        description="Scenario difficulty level (1-10)"
    )
    expected_duration: int = Field(
        ge=1,
        description="Expected duration in minutes"
    )
    success_criteria: List[str] = Field(
        default_factory=list,
        description="Criteria for successful scenario completion"
    )
    cultural_adaptations: Dict[str, Any] = Field(
        default_factory=dict,
        description="Cultural adaptations for different backgrounds"
    )
    
    def adapt_for_culture(self, culture: str) -> 'Scenario':
        """
        Adapt scenario for a specific cultural context.
        
        Args:
            culture: Cultural background identifier
            
        Returns:
            Adapted scenario instance
        """
        if culture in self.cultural_adaptations:
            adaptations = self.cultural_adaptations[culture]
            
            # Create a copy with cultural adaptations
            adapted_scenario = self.copy()
            
            # Apply cultural adaptations
            if "description" in adaptations:
                adapted_scenario.description = adaptations["description"]
            
            if "context" in adaptations:
                adapted_scenario.context.update(adaptations["context"])
            
            if "success_criteria" in adaptations:
                adapted_scenario.success_criteria = adaptations["success_criteria"]
            
            return adapted_scenario
        
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scenario to dictionary for serialization."""
        return {
            "scenario_id": self.scenario_id,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "context": self.context,
            "difficulty_level": self.difficulty_level,
            "expected_duration": self.expected_duration,
            "success_criteria": self.success_criteria,
            "cultural_adaptations": self.cultural_adaptations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scenario':
        """Create scenario from dictionary."""
        return cls(
            scenario_id=data["scenario_id"],
            category=ScenarioCategory(data["category"]),
            title=data["title"],
            description=data["description"],
            context=data.get("context", {}),
            difficulty_level=data["difficulty_level"],
            expected_duration=data["expected_duration"],
            success_criteria=data.get("success_criteria", []),
            cultural_adaptations=data.get("cultural_adaptations", {})
        )


class Response(BaseModel):
    """A participant's response to a scenario."""
    
    participant_id: str = Field(description="ID of the responding participant")
    content: str = Field(description="Response content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    emotional_tone: Optional[str] = Field(
        default=None,
        description="Detected emotional tone of the response"
    )
    values_expressed: List[str] = Field(
        default_factory=list,
        description="Personal values expressed in the response"
    )
    conflict_indicators: List[str] = Field(
        default_factory=list,
        description="Indicators of conflict or disagreement"
    )


class ScenarioResult(BaseModel):
    """Results from a completed scenario simulation."""
    
    scenario_id: str = Field(description="ID of the completed scenario")
    participants: List[str] = Field(description="Participant user IDs")
    responses: List[Response] = Field(
        default_factory=list,
        description="All responses during the scenario"
    )
    collaboration_score: float = Field(
        ge=0.0, le=1.0,
        description="How well participants collaborated"
    )
    conflict_resolution_score: float = Field(
        ge=0.0, le=1.0,
        description="Effectiveness of conflict resolution"
    )
    value_alignment_score: float = Field(
        ge=0.0, le=1.0,
        description="Alignment of expressed values"
    )
    completion_time: int = Field(description="Time taken to complete scenario (minutes)")
    notes: str = Field(default="", description="Additional notes and observations")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def calculate_overall_score(self) -> float:
        """Calculate overall scenario performance score."""
        return (
            self.collaboration_score * 0.4 +
            self.conflict_resolution_score * 0.3 +
            self.value_alignment_score * 0.3
        )
    
    def get_responses_by_participant(self, participant_id: str) -> List[Response]:
        """Get all responses from a specific participant."""
        return [resp for resp in self.responses if resp.participant_id == participant_id]


class CompatibilityReport(BaseModel):
    """Comprehensive compatibility assessment report."""
    
    report_id: str = Field(description="Unique report identifier")
    session_id: str = Field(description="Associated session ID")
    user_ids: tuple[str, str] = Field(description="IDs of the two users being assessed")
    overall_score: float = Field(
        ge=0.0, le=1.0,
        description="Overall compatibility score"
    )
    dimension_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Scores for different compatibility dimensions"
    )
    scenario_results: List[ScenarioResult] = Field(
        default_factory=list,
        description="Results from all completed scenarios"
    )
    interaction_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of interaction patterns"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Identified relationship strengths"
    )
    challenges: List[str] = Field(
        default_factory=list,
        description="Potential relationship challenges"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations"
    )
    confidence_level: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in the assessment"
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def add_scenario_result(self, result: ScenarioResult) -> None:
        """Add a scenario result to the report."""
        self.scenario_results.append(result)
        self._recalculate_scores()
    
    def _recalculate_scores(self) -> None:
        """Recalculate overall scores based on scenario results."""
        if not self.scenario_results:
            return
        
        # Calculate average scores across all scenarios
        total_collaboration = sum(r.collaboration_score for r in self.scenario_results)
        total_conflict_resolution = sum(r.conflict_resolution_score for r in self.scenario_results)
        total_value_alignment = sum(r.value_alignment_score for r in self.scenario_results)
        
        num_scenarios = len(self.scenario_results)
        
        self.dimension_scores = {
            "collaboration": total_collaboration / num_scenarios,
            "conflict_resolution": total_conflict_resolution / num_scenarios,
            "value_alignment": total_value_alignment / num_scenarios,
        }
        
        # Calculate overall score
        self.overall_score = sum(self.dimension_scores.values()) / len(self.dimension_scores)
        
        # Update confidence based on number of scenarios
        self.confidence_level = min(1.0, num_scenarios / 5.0)  # Full confidence with 5+ scenarios
    
    def get_scenario_results_by_category(self, category: ScenarioCategory) -> List[ScenarioResult]:
        """Get scenario results filtered by category."""
        # This would require access to scenario data to filter by category
        # For now, return all results (would be enhanced with scenario lookup)
        return self.scenario_results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            "report_id": self.report_id,
            "session_id": self.session_id,
            "user_ids": list(self.user_ids),
            "overall_score": self.overall_score,
            "dimension_scores": self.dimension_scores,
            "scenario_results": [result.dict() for result in self.scenario_results],
            "interaction_summary": self.interaction_summary,
            "strengths": self.strengths,
            "challenges": self.challenges,
            "recommendations": self.recommendations,
            "confidence_level": self.confidence_level,
            "generated_at": self.generated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompatibilityReport':
        """Create report from dictionary."""
        scenario_results = [
            ScenarioResult(**result_data) 
            for result_data in data.get("scenario_results", [])
        ]
        
        return cls(
            report_id=data["report_id"],
            session_id=data["session_id"],
            user_ids=tuple(data["user_ids"]),
            overall_score=data["overall_score"],
            dimension_scores=data.get("dimension_scores", {}),
            scenario_results=scenario_results,
            interaction_summary=data.get("interaction_summary", {}),
            strengths=data.get("strengths", []),
            challenges=data.get("challenges", []),
            recommendations=data.get("recommendations", []),
            confidence_level=data["confidence_level"],
            generated_at=datetime.fromisoformat(data["generated_at"])
        )