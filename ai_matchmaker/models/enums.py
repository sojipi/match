"""
Enums for the AI Matchmaker application.

Defines various types and categories used throughout the system.
"""

from enum import Enum, auto


class AgentType(Enum):
    """Types of AI agents in the system."""
    TRAINING_AGENT = "training_agent"
    USER_AVATAR = "user_avatar"
    MATCHMAKER_AGENT = "matchmaker_agent"
    SCENARIO_GENERATOR = "scenario_generator"
    EVALUATOR_AGENT = "evaluator_agent"


class SessionType(Enum):
    """Types of conversation sessions."""
    TRAINING = "training"
    MATCHMAKING = "matchmaking"
    SIMULATION = "simulation"


class SessionStatus(Enum):
    """Status of conversation sessions."""
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    ERROR = "error"


class ScenarioCategory(Enum):
    """Categories of marriage simulation scenarios."""
    FINANCIAL = "financial"
    FAMILY = "family"
    PARENTING = "parenting"
    CAREER = "career"
    LIFESTYLE = "lifestyle"
    COMMUNICATION = "communication"
    CONFLICT_RESOLUTION = "conflict_resolution"


class TrainingStatus(Enum):
    """Status of user training progress."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"


class CommunicationStyle(Enum):
    """Communication styles for personality profiles."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    ASSERTIVE = "assertive"
    PASSIVE = "passive"
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"


class ConflictResolutionStyle(Enum):
    """Conflict resolution styles for personality profiles."""
    ACCOMMODATING = "accommodating"
    AVOIDING = "avoiding"
    COLLABORATING = "collaborating"
    COMPETING = "competing"
    COMPROMISING = "compromising"