"""
Logging configuration and utilities for the AI Matchmaker application.

Provides structured logging with different output formats for development and production.
"""

import sys
import logging
from pathlib import Path
from typing import Optional
import structlog
from colorama import init as colorama_init, Fore, Style

from .config import get_config

# Initialize colorama for cross-platform colored output
colorama_init(autoreset=True)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_colors: bool = True
) -> None:
    """
    Set up structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        enable_colors: Whether to enable colored console output
    """
    config = get_config()
    
    # Use provided log level or fall back to config
    level = log_level or config.log_level
    log_level_int = getattr(logging, level.upper(), logging.INFO)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level_int,
    )
    
    # Processors for structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    # Add appropriate renderer based on environment
    if config.is_development and enable_colors:
        processors.append(ColoredConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level_int),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Set up file logging if specified
    if log_file:
        setup_file_logging(log_file, log_level_int)


def setup_file_logging(log_file: str, log_level: int) -> None:
    """
    Set up file-based logging.
    
    Args:
        log_file: Path to the log file
        log_level: Logging level as integer
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(log_level)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)


class ColoredConsoleRenderer:
    """
    Custom renderer for colored console output in development.
    """
    
    LEVEL_COLORS = {
        "debug": Fore.CYAN,
        "info": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "critical": Fore.MAGENTA + Style.BRIGHT,
    }
    
    def __call__(self, logger, method_name, event_dict):
        """Render log entry with colors."""
        level = event_dict.get("level", "info").lower()
        color = self.LEVEL_COLORS.get(level, "")
        
        timestamp = event_dict.get("timestamp", "")
        logger_name = event_dict.get("logger", "")
        message = event_dict.get("event", "")
        
        # Format the log line
        formatted = f"{timestamp} [{color}{level.upper()}{Style.RESET_ALL}] {logger_name}: {message}"
        
        # Add any additional context
        context_items = []
        for key, value in event_dict.items():
            if key not in ("timestamp", "level", "logger", "event"):
                context_items.append(f"{key}={value}")
        
        if context_items:
            formatted += f" | {' '.join(context_items)}"
        
        return formatted


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class AgentLogger:
    """
    Specialized logger for AI agents with context tracking.
    """
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.logger = get_logger(f"agent.{agent_type}")
        
    def log_message(self, direction: str, message: str, **context):
        """Log agent message with context."""
        self.logger.info(
            f"Agent {direction} message",
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            message=message[:100] + "..." if len(message) > 100 else message,
            **context
        )
    
    def log_action(self, action: str, **context):
        """Log agent action with context."""
        self.logger.info(
            f"Agent action: {action}",
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            **context
        )
    
    def log_error(self, error: str, **context):
        """Log agent error with context."""
        self.logger.error(
            f"Agent error: {error}",
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            **context
        )


# Initialize logging on module import
setup_logging()