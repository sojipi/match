"""
Authentication and user schemas.
"""
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID

from app.core.security import validate_password_strength


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        validation = validate_password_strength(v)
        if not validation['is_valid']:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v.lower()


class UserUpdate(BaseModel):
    """User update schema."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    privacy_settings: Optional[Dict[str, Any]] = None
    notification_preferences: Optional[Dict[str, bool]] = None


class UserResponse(UserBase):
    """User response schema."""
    id: UUID
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool
    is_active: bool
    subscription_tier: str
    created_at: datetime
    last_active: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str
    remember_me: bool = False
    device_info: Optional[Dict[str, Any]] = None


class UserLoginResponse(BaseModel):
    """User login response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenRefresh(BaseModel):
    """Token refresh schema."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordReset(BaseModel):
    """Password reset request schema."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        validation = validate_password_strength(v)
        if not validation['is_valid']:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v


class PasswordChange(BaseModel):
    """Password change schema."""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        validation = validate_password_strength(v)
        if not validation['is_valid']:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v


class EmailVerification(BaseModel):
    """Email verification schema."""
    token: str


class SocialLoginRequest(BaseModel):
    """Social login request schema."""
    provider: str = Field(..., regex="^(google|facebook)$")
    access_token: str
    device_info: Optional[Dict[str, Any]] = None


class UserSession(BaseModel):
    """User session schema."""
    session_id: str
    device_info: Dict[str, Any]
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    is_current: bool = False


class UserSessionsResponse(BaseModel):
    """User sessions response schema."""
    sessions: List[UserSession]
    total_count: int


class APIKeyCreate(BaseModel):
    """API key creation schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    expires_at: Optional[datetime] = None


class APIKeyResponse(BaseModel):
    """API key response schema."""
    id: UUID
    name: str
    description: Optional[str] = None
    key_preview: str  # Only first 8 characters
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool


class UserProfileCompleteness(BaseModel):
    """User profile completeness schema."""
    overall_score: float = Field(..., ge=0.0, le=1.0)
    sections: Dict[str, float]
    missing_items: List[str]
    suggestions: List[str]


class UserStats(BaseModel):
    """User statistics schema."""
    total_matches: int
    mutual_matches: int
    conversations_started: int
    profile_views: int
    compatibility_reports: int
    average_compatibility_score: Optional[float] = None
    join_date: datetime
    last_active: Optional[datetime] = None