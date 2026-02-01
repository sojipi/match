"""
User and personality profile data models.

Contains data classes for user profiles, personality traits, and preferences.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field, validator
from .enums import (
    TrainingStatus, 
    CommunicationStyle, 
    ConflictResolutionStyle
)


class PersonalityTraits(BaseModel):
    """Big Five personality traits with additional custom dimensions."""
    
    # Big Five personality dimensions (0.0 to 1.0)
    openness: float = Field(ge=0.0, le=1.0, description="Openness to experience")
    conscientiousness: float = Field(ge=0.0, le=1.0, description="Conscientiousness")
    extraversion: float = Field(ge=0.0, le=1.0, description="Extraversion")
    agreeableness: float = Field(ge=0.0, le=1.0, description="Agreeableness")
    neuroticism: float = Field(ge=0.0, le=1.0, description="Neuroticism")
    
    # Custom values with importance ratings (0.0 to 1.0)
    values: Dict[str, float] = Field(
        default_factory=dict,
        description="Personal values with importance ratings"
    )
    
    # Communication and conflict styles
    communication_style: CommunicationStyle
    conflict_resolution_style: ConflictResolutionStyle
    
    @validator('values')
    def validate_values(cls, v):
        """Ensure all value ratings are between 0.0 and 1.0."""
        for key, rating in v.items():
            if not 0.0 <= rating <= 1.0:
                raise ValueError(f"Value rating for '{key}' must be between 0.0 and 1.0")
        return v


class UserPreferences(BaseModel):
    """User preferences for matching and lifestyle."""
    
    age_range: Tuple[int, int] = Field(description="Preferred age range for matches")
    location_preferences: List[str] = Field(
        default_factory=list,
        description="Preferred locations or regions"
    )
    lifestyle_preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="Lifestyle preferences and requirements"
    )
    deal_breakers: List[str] = Field(
        default_factory=list,
        description="Absolute deal breakers in relationships"
    )
    relationship_goals: List[str] = Field(
        default_factory=list,
        description="Long-term relationship goals"
    )
    
    @validator('age_range')
    def validate_age_range(cls, v):
        """Ensure age range is valid."""
        min_age, max_age = v
        if min_age < 18:
            raise ValueError("Minimum age must be at least 18")
        if max_age < min_age:
            raise ValueError("Maximum age must be greater than minimum age")
        if max_age > 100:
            raise ValueError("Maximum age must be reasonable (≤100)")
        return v


class BasicInfo(BaseModel):
    """Basic user information."""
    
    name: str = Field(min_length=1, description="User's name")
    age: int = Field(ge=18, le=100, description="User's age")
    location: str = Field(description="User's current location")
    occupation: Optional[str] = Field(default=None, description="User's occupation")
    education: Optional[str] = Field(default=None, description="User's education level")
    bio: Optional[str] = Field(default=None, description="User's biography")


class PersonalityProfile(BaseModel):
    """Complete personality profile for a user."""
    
    user_id: str = Field(description="Unique user identifier")
    personality_traits: PersonalityTraits
    preferences: UserPreferences
    completeness_score: float = Field(
        ge=0.0, le=1.0, 
        default=0.0,
        description="Profile completeness score"
    )
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    def get_relevant_traits(self, context: str) -> Dict[str, Any]:
        """
        Retrieve personality aspects relevant to specific contexts.
        
        Args:
            context: The context for which to retrieve relevant traits
            
        Returns:
            Dictionary of relevant personality traits and values
        """
        # This is a simplified implementation - in practice, this would use
        # semantic search and context matching
        relevant_traits = {
            "personality_traits": self.personality_traits.dict(),
            "communication_style": self.personality_traits.communication_style.value,
            "conflict_style": self.personality_traits.conflict_resolution_style.value,
        }
        
        # Add context-specific values if they exist
        context_keywords = context.lower().split()
        relevant_values = {}
        for value_name, importance in self.personality_traits.values.items():
            if any(keyword in value_name.lower() for keyword in context_keywords):
                relevant_values[value_name] = importance
        
        if relevant_values:
            relevant_traits["relevant_values"] = relevant_values
            
        return relevant_traits
    
    def calculate_completeness(self) -> float:
        """
        Calculate the completeness score of the personality profile.
        
        Returns:
            Completeness score between 0.0 and 1.0
        """
        score = 0.0
        total_components = 7  # Number of components to check
        
        # Check Big Five traits (all should be set, not default 0.0)
        big_five_traits = [
            self.personality_traits.openness,
            self.personality_traits.conscientiousness,
            self.personality_traits.extraversion,
            self.personality_traits.agreeableness,
            self.personality_traits.neuroticism
        ]
        
        if all(trait > 0.0 for trait in big_five_traits):
            score += 1.0
        
        # Check if values are defined (at least 3 values)
        if len(self.personality_traits.values) >= 3:
            score += 1.0
            
        # Check communication style
        if self.personality_traits.communication_style:
            score += 1.0
            
        # Check conflict resolution style
        if self.personality_traits.conflict_resolution_style:
            score += 1.0
            
        # Check preferences
        if self.preferences.age_range and self.preferences.age_range != (18, 100):
            score += 1.0
            
        if len(self.preferences.relationship_goals) > 0:
            score += 1.0
            
        if len(self.preferences.lifestyle_preferences) > 0:
            score += 1.0
        
        return score / total_components


class UserProfile(BaseModel):
    """Complete user profile including basic info and personality."""
    
    user_id: str = Field(description="Unique user identifier")
    basic_info: BasicInfo
    personality_profile: Optional[PersonalityProfile] = None
    training_status: TrainingStatus = TrainingStatus.NOT_STARTED
    language: str = Field(default="en", description="Primary language")
    culture: str = Field(default="western", description="Cultural background")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def is_training_complete(self) -> bool:
        """Check if user training is complete."""
        return (
            self.training_status == TrainingStatus.COMPLETED and
            self.personality_profile is not None and
            self.personality_profile.completeness_score >= 0.8
        )
    
    def update_timestamp(self):
        """Update the last modified timestamp."""
        self.updated_at = datetime.utcnow()
        if self.personality_profile:
            self.personality_profile.last_updated = datetime.utcnow()


# Validation functions for data integrity
def validate_personality_profile(profile: PersonalityProfile) -> List[str]:
    """
    Validate a personality profile for completeness and consistency.
    
    Args:
        profile: The personality profile to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check Big Five traits are within valid range
    traits = profile.personality_traits
    big_five = [
        ("openness", traits.openness),
        ("conscientiousness", traits.conscientiousness),
        ("extraversion", traits.extraversion),
        ("agreeableness", traits.agreeableness),
        ("neuroticism", traits.neuroticism)
    ]
    
    for trait_name, value in big_five:
        if not 0.0 <= value <= 1.0:
            errors.append(f"{trait_name} must be between 0.0 and 1.0")
    
    # Check minimum number of values
    if len(traits.values) < 3:
        errors.append("At least 3 personal values must be defined")
    
    # Check age range validity
    min_age, max_age = profile.preferences.age_range
    if min_age >= max_age:
        errors.append("Age range minimum must be less than maximum")
    
    return errors


def validate_user_profile(profile: UserProfile) -> List[str]:
    """
    Validate a complete user profile.
    
    Args:
        profile: The user profile to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check basic info
    if not profile.basic_info.name.strip():
        errors.append("Name cannot be empty")
    
    if profile.basic_info.age < 18:
        errors.append("User must be at least 18 years old")
    
    # Check personality profile if present
    if profile.personality_profile:
        personality_errors = validate_personality_profile(profile.personality_profile)
        errors.extend(personality_errors)
    
    return errors