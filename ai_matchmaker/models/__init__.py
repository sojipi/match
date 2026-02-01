"""
Data models module for the matchmaker application.

Contains data classes and schemas for users, conversations, and scenarios.
"""

from .enums import (
    AgentType,
    SessionType,
    SessionStatus,
    ScenarioCategory,
    TrainingStatus,
    CommunicationStyle,
    ConflictResolutionStyle,
)

from .profiles import (
    PersonalityTraits,
    UserPreferences,
    BasicInfo,
    PersonalityProfile,
    UserProfile,
    validate_personality_profile,
    validate_user_profile,
)

from .conversations import (
    Message,
    ConversationSession,
    InteractionAnalysis,
    ConversationSummary,
)

from .scenarios import (
    Scenario,
    Response,
    ScenarioResult,
    CompatibilityReport,
)

__all__ = [
    # Enums
    "AgentType",
    "SessionType", 
    "SessionStatus",
    "ScenarioCategory",
    "TrainingStatus",
    "CommunicationStyle",
    "ConflictResolutionStyle",
    
    # Profile models
    "PersonalityTraits",
    "UserPreferences", 
    "BasicInfo",
    "PersonalityProfile",
    "UserProfile",
    "validate_personality_profile",
    "validate_user_profile",
    
    # Conversation models
    "Message",
    "ConversationSession",
    "InteractionAnalysis", 
    "ConversationSummary",
    
    # Scenario models
    "Scenario",
    "Response",
    "ScenarioResult",
    "CompatibilityReport",
]