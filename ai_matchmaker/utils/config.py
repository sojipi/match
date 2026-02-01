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


class APIConfig(BaseSettings):
    """Configuration for external API services."""
    
    gemini_api_key: Optional[str] = Field(None, env="GEMINI_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    google_translate_api_key: Optional[str] = Field(None, env="GOOGLE_TRANSLATE_API_KEY")
    
    class Config:
        env_file = ".env"


class DatabaseConfig(BaseSettings):
    """Configuration for database and memory storage."""
    
    chroma_db_path: str = Field("./data/chroma_db", env="CHROMA_DB_PATH")
    mem0_config_path: str = Field("./config/mem0_config.yaml", env="MEM0_CONFIG_PATH")
    
    class Config:
        env_file = ".env"


class AgentConfig(BaseSettings):
    """Configuration for AI agents and conversations."""
    
    max_conversation_turns: int = Field(20, env="MAX_CONVERSATION_TURNS")
    conversation_timeout_seconds: int = Field(1800, env="CONVERSATION_TIMEOUT_SECONDS")
    agent_response_timeout_seconds: int = Field(30, env="AGENT_RESPONSE_TIMEOUT_SECONDS")
    
    class Config:
        env_file = ".env"


class LocalizationConfig(BaseSettings):
    """Configuration for internationalization and localization."""
    
    default_language: str = Field("en", env="DEFAULT_LANGUAGE")
    supported_languages: List[str] = Field(
        ["en", "es", "fr", "de", "zh", "ja"], 
        env="SUPPORTED_LANGUAGES"
    )
    
    class Config:
        env_file = ".env"
        
    @property
    def supported_languages_list(self) -> List[str]:
        """Convert comma-separated string to list if needed."""
        if isinstance(self.supported_languages, str):
            return [lang.strip() for lang in self.supported_languages.split(",")]
        return self.supported_languages


class AppConfig(BaseSettings):
    """Main application configuration."""
    
    log_level: str = Field("INFO", env="LOG_LEVEL")
    debug: bool = Field(False, env="DEBUG")
    environment: str = Field("development", env="ENVIRONMENT")
    test_mode: bool = Field(False, env="TEST_MODE")
    mock_external_apis: bool = Field(False, env="MOCK_EXTERNAL_APIS")
    
    # Sub-configurations
    api: APIConfig = Field(default_factory=APIConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    localization: LocalizationConfig = Field(default_factory=LocalizationConfig)
    
    class Config:
        env_file = ".env"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize sub-configurations
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.agent = AgentConfig()
        self.localization = LocalizationConfig()
    
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
            Path(self.database.chroma_db_path).parent,
            Path(self.database.mem0_config_path).parent,
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