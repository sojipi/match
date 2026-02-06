"""
Application configuration settings.
"""
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
import os
from pathlib import Path


# Find the project root directory (where .env should be located)
def find_project_root() -> Path:
    """Find the project root directory by looking for .env file."""
    current = Path(__file__).resolve()
    
    # Go up the directory tree looking for .env file
    for parent in current.parents:
        if (parent / ".env").exists():
            return parent
    
    # If not found, assume it's two levels up from this file
    return current.parent.parent.parent


PROJECT_ROOT = find_project_root()
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "AI Matchmaker"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/ai_matchmaker"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS - can be string or list
    ALLOWED_HOSTS: Union[str, List[str]] = "http://localhost:3000,http://127.0.0.1:3000"
    
    # AI Services
    GEMINI_API_KEY: str = "your-gemini-api-key"
    OPENAI_API_KEY: Optional[str] = None
    
    # Memory and Database Configuration
    CHROMA_DB_PATH: str = "./data/chroma_db"
    MEM0_CONFIG_PATH: str = "./config/mem0_config.yaml"
    
    # File Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    
    # Email
    EMAIL_ENABLED: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@aimatchmaker.com"
    FROM_NAME: str = "AI Matchmaker"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Push Notifications (PWA)
    PUSH_NOTIFICATIONS_ENABLED: bool = False
    VAPID_PUBLIC_KEY: Optional[str] = None
    VAPID_PRIVATE_KEY: Optional[str] = None
    
    # Social Authentication
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Internationalization
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: str = "en,es,fr,de,zh,ja"
    
    # Translation Service
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = None
    
    # Agent Configuration
    MAX_CONVERSATION_TURNS: int = 20
    CONVERSATION_TIMEOUT_SECONDS: int = 1800
    AGENT_RESPONSE_TIMEOUT_SECONDS: int = 30
    
    # Testing Configuration
    TEST_MODE: bool = False
    MOCK_EXTERNAL_APIS: bool = False
    
    def get_allowed_hosts(self) -> List[str]:
        """Get ALLOWED_HOSTS as a list."""
        if isinstance(self.ALLOWED_HOSTS, str):
            return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
        return self.ALLOWED_HOSTS
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages as a list."""
        return [lang.strip() for lang in self.SUPPORTED_LANGUAGES.split(",")]
    
    model_config = {
        "env_file": str(ENV_FILE_PATH),  # Use dynamic path to .env file
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra fields instead of raising errors
    }


settings = Settings()