"""
Authentication endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, verify_password, get_password_hash
from app.models.user import User

router = APIRouter()
security = HTTPBearer()


class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if user already exists
    # This is a placeholder - implement actual database queries
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user (placeholder)
    user_dict = {
        "id": "placeholder-id",
        "email": user_data.email,
        "username": user_data.username,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
    }
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_dict["id"]})
    refresh_token = create_refresh_token(data={"sub": user_dict["id"]})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_dict
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user."""
    # This is a placeholder - implement actual authentication
    
    # Mock user data
    user_dict = {
        "id": "placeholder-id",
        "email": user_data.email,
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
    }
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_dict["id"]})
    refresh_token = create_refresh_token(data={"sub": user_dict["id"]})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_dict
    )


@router.post("/logout")
async def logout():
    """Logout user."""
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user():
    """Get current user information."""
    # This is a placeholder - implement actual user retrieval
    return {
        "id": "placeholder-id",
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
    }