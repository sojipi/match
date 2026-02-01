"""
Custom exceptions for the AI Matchmaker application.

Defines application-specific exceptions with proper error handling and logging.
"""

from typing import List, Optional, Dict, Any
import traceback
from .logging import get_logger

logger = get_logger(__name__)


class AIMatchmakerError(Exception):
    """Base exception for all AI Matchmaker application errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, **context):
        self.message = message
        self.error_code = error_code
        self.context = context
        super().__init__(message)
        
        # Log the error
        logger.error(
            f"AIMatchmakerError: {message}",
            error_code=error_code,
            **context
        )


class ConfigurationError(AIMatchmakerError):
    """Raised when there are configuration or setup issues."""
    
    def __init__(self, message: str, missing_config: Optional[str] = None, **context):
        self.missing_config = missing_config
        super().__init__(
            message, 
            error_code="CONFIG_ERROR",
            missing_config=missing_config,
            **context
        )


class AgentError(AIMatchmakerError):
    """Base class for agent-related errors."""
    
    def __init__(self, message: str, agent_id: Optional[str] = None, 
                 agent_type: Optional[str] = None, **context):
        self.agent_id = agent_id
        self.agent_type = agent_type
        super().__init__(
            message,
            error_code="AGENT_ERROR",
            agent_id=agent_id,
            agent_type=agent_type,
            **context
        )


class AgentCommunicationError(AgentError):
    """Raised when agents fail to communicate properly."""
    
    def __init__(self, agent_id: str, error_type: str, details: str, **context):
        self.error_type = error_type
        self.details = details
        super().__init__(
            f"Agent {agent_id} communication error: {error_type}",
            agent_id=agent_id,
            error_code="AGENT_COMM_ERROR",
            error_type=error_type,
            details=details,
            **context
        )


class ConversationTimeoutError(AgentError):
    """Raised when conversations exceed maximum duration."""
    
    def __init__(self, session_id: str, duration: int, max_duration: int, **context):
        self.session_id = session_id
        self.duration = duration
        self.max_duration = max_duration
        super().__init__(
            f"Session {session_id} timed out after {duration}s (max: {max_duration}s)",
            error_code="CONVERSATION_TIMEOUT",
            session_id=session_id,
            duration=duration,
            max_duration=max_duration,
            **context
        )


class MemoryError(AIMatchmakerError):
    """Base class for memory-related errors."""
    
    def __init__(self, message: str, user_id: Optional[str] = None, **context):
        self.user_id = user_id
        super().__init__(
            message,
            error_code="MEMORY_ERROR",
            user_id=user_id,
            **context
        )


class MemoryRetrievalError(MemoryError):
    """Raised when memory retrieval fails."""
    
    def __init__(self, user_id: str, query: str, error_details: str, **context):
        self.query = query
        self.error_details = error_details
        super().__init__(
            f"Memory retrieval failed for user {user_id}: {error_details}",
            user_id=user_id,
            error_code="MEMORY_RETRIEVAL_ERROR",
            query=query,
            error_details=error_details,
            **context
        )


class ProfileIncompleteError(MemoryError):
    """Raised when user profile lacks sufficient data."""
    
    def __init__(self, user_id: str, missing_components: List[str], **context):
        self.missing_components = missing_components
        super().__init__(
            f"Profile incomplete for user {user_id}: missing {missing_components}",
            user_id=user_id,
            error_code="PROFILE_INCOMPLETE",
            missing_components=missing_components,
            **context
        )


class APIError(AIMatchmakerError):
    """Raised when external API calls fail."""
    
    def __init__(self, service: str, message: str, status_code: Optional[int] = None, 
                 response_data: Optional[Dict[str, Any]] = None, **context):
        self.service = service
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(
            f"{service} API error: {message}",
            error_code="API_ERROR",
            service=service,
            status_code=status_code,
            response_data=response_data,
            **context
        )


class ValidationError(AIMatchmakerError):
    """Raised when data validation fails."""
    
    def __init__(self, field: str, value: Any, message: str, **context):
        self.field = field
        self.value = value
        super().__init__(
            f"Validation error for {field}: {message}",
            error_code="VALIDATION_ERROR",
            field=field,
            value=str(value),
            validation_message=message,
            **context
        )


class LocalizationError(AIMatchmakerError):
    """Raised when localization or translation fails."""
    
    def __init__(self, language: str, message: str, **context):
        self.language = language
        super().__init__(
            f"Localization error for {language}: {message}",
            error_code="LOCALIZATION_ERROR",
            language=language,
            **context
        )


def handle_exception(func):
    """
    Decorator for handling exceptions with proper logging and context.
    
    Usage:
        @handle_exception
        def my_function():
            # Function code here
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AIMatchmakerError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Convert unexpected exceptions to our base exception
            logger.error(
                f"Unexpected error in {func.__name__}",
                function=func.__name__,
                error_type=type(e).__name__,
                error_message=str(e),
                traceback=traceback.format_exc()
            )
            raise AIMatchmakerError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                function=func.__name__,
                original_error=str(e)
            ) from e
    
    return wrapper


class ErrorHandler:
    """
    Centralized error handling and recovery strategies.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.error_counts = {}
        self.max_retries = 3
    
    def should_retry(self, error: Exception, operation: str) -> bool:
        """
        Determine if an operation should be retried based on the error type.
        
        Args:
            error: The exception that occurred
            operation: Name of the operation that failed
            
        Returns:
            True if the operation should be retried
        """
        # Track error counts
        error_key = f"{operation}:{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Don't retry if we've exceeded max attempts
        if self.error_counts[error_key] >= self.max_retries:
            return False
        
        # Retry for certain types of errors
        retryable_errors = (
            APIError,
            AgentCommunicationError,
            MemoryRetrievalError,
        )
        
        return isinstance(error, retryable_errors)
    
    def reset_error_count(self, operation: str, error_type: type):
        """Reset error count for a specific operation and error type."""
        error_key = f"{operation}:{error_type.__name__}"
        self.error_counts.pop(error_key, None)
    
    def get_fallback_response(self, error: Exception, context: Dict[str, Any]) -> Optional[Any]:
        """
        Get a fallback response for certain types of errors.
        
        Args:
            error: The exception that occurred
            context: Context information about the operation
            
        Returns:
            Fallback response if available, None otherwise
        """
        if isinstance(error, APIError):
            # Return a generic response for API failures
            return {
                "status": "error",
                "message": "Service temporarily unavailable",
                "fallback": True
            }
        
        if isinstance(error, MemoryRetrievalError):
            # Return empty results for memory failures
            return []
        
        return None


# Global error handler instance
error_handler = ErrorHandler()