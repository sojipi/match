"""
Test basic project structure and imports.
"""

import pytest
from pathlib import Path


def test_project_structure():
    """Test that all required directories exist."""
    base_path = Path("ai_matchmaker")
    
    required_dirs = [
        "agents",
        "memory", 
        "models",
        "controllers",
        "communication",
        "localization",
        "utils"
    ]
    
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        assert dir_path.exists(), f"Directory {dir_path} should exist"
        assert (dir_path / "__init__.py").exists(), f"__init__.py should exist in {dir_path}"


def test_config_import():
    """Test that configuration can be imported."""
    from ai_matchmaker.utils.config import get_config
    
    config = get_config()
    assert config is not None
    assert hasattr(config, 'environment')
    assert hasattr(config, 'log_level')
    assert hasattr(config, 'gemini_api_key')
    assert hasattr(config, 'chroma_db_path')


def test_logging_import():
    """Test that logging can be imported."""
    from ai_matchmaker.utils.logging import get_logger
    
    logger = get_logger(__name__)
    assert logger is not None


def test_exceptions_import():
    """Test that exceptions can be imported."""
    from ai_matchmaker.utils.exceptions import AIMatchmakerError, ConfigurationError
    
    # Test basic exception creation
    error = AIMatchmakerError("Test error")
    assert str(error) == "Test error"
    
    config_error = ConfigurationError("Config test error")
    assert str(config_error) == "Config test error"


def test_cli_import():
    """Test that CLI can be imported."""
    from ai_matchmaker.cli import main
    assert main is not None