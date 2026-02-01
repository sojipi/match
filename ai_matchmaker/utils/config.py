"""
Configuration management for the AI Matchmaker application.

Handles environment variables, API keys, and application settings.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AppConfig(BaseSettings):
    """Main application configuration."""
    
    # API Configuration
    gemini_api_key: Optional[str] = Field(None, env="GEMINI_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    google_translate_api_key: Optional[str] = Field(None, env="GOOGLE_TRANSLATE_API_KEY")
    
    # Database Configuration
    chroma_db_path: str = Field("./data/chroma_db", env="CHROMA_DB_PATH")
    mem0_config_path: str = Field("./config/mem0_config.yaml", env="MEM0_CONFIG_PATH")
    
    # Agent Configuration
    max_conversation_turns: int = Field(20, env="MAX_CONVERSATION_TURNS")
    conversation_timeout_seconds: int = Field(1800, env="CONVERSATION_TIMEOUT_SECONDS")
    agent_response_timeout_seconds: int = Field(30, env="AGENT_RESPONSE_TIMEOUT_SECONDS")
    
    # Localization Configuration
    default_language: str = Field("en", env="DEFAULT_LANGUAGE")
    supported_languages: str = Field("en,es,fr,de,zh,ja", env="SUPPORTED_LANGUAGES")
    
    # Application Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    debug: bool = Field(False, env="DEBUG")
    environment: str = Field("development", env="ENVIRONMENT")
    test_mode: bool = Field(False, env="TEST_MODE")
    mock_external_apis: bool = Field(False, env="MOCK_EXTERNAL_APIS")
    
    model_config = {"env_file": ".env"}
    
    @property
    def supported_languages_list(self) -> List[str]:
        """Convert comma-separated string to list."""
        return [lang.strip() for lang in self.supported_languages.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        directories = [
            Path(self.chroma_db_path).parent,
            Path(self.mem0_config_path).parent,
            Path("logs"),
            Path("data"),
            Path("config"),
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = AppConfig()

# Ensure required directories exist on import
config.ensure_directories()


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config


def reload_config() -> AppConfig:
    """Reload configuration from environment variables."""
    global config
    config = AppConfig()
    config.ensure_directories()
    return config