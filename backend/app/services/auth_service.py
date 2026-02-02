"""
Authentication service for user management and authentication.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status, Request
import uuid
import secrets

from app.models.user import User, PersonalityProfile, DatingPreferences
from app.models.notification import Notification, NotificationType
from app.models.redis_models import UserSession, UserOnlineStatus, redis_client
from app.schemas.auth import (
    UserCreate, UserUpdate, UserLogin, UserLoginResponse, 
    PasswordChange, PasswordReset, PasswordResetConfirm,
    UserResponse, UserProfileCompleteness, UserStats
)
from app.core.security import (
    get_password_hash, verify_password, create_access_token, 
    create_refresh_token, create_user_session, generate_verification_token,
    generate_reset_token, AuthenticationError, AuthorizationError
)
from app.core.config import settings


class AuthService:
    """Authentication service class."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register_user(
        self, 
        user_data: UserCreate, 
        request: Request
    ) -> UserLoginResponse:
        """Register a new user."""
        
        # Check if email already exists
        existing_user = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_username = await self.db.execute(
            select(User).where(User.username == user_data.username.lower())
        )
        if existing_username.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            username=user_data.username.lower(),
            password_hash=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            date_of_birth=user_data.date_of_birth,
            gender=user_data.gender,
            location=user_data.location,
            bio=user_data.bio,
            is_verified=False,  # Email verification required
            is_active=True
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        # Create empty personality profile and dating preferences
        personality_profile = PersonalityProfile(
            id=uuid.uuid4(),
            user_id=user.id,
            completeness_score=0.0
        )
        
        dating_preferences = DatingPreferences(
            id=uuid.uuid4(),
            user_id=user.id
        )
        
        self.db.add(personality_profile)
        self.db.add(dating_preferences)
        
        # Create welcome notification
        welcome_notification = Notification(
            id=uuid.uuid4(),
            user_id=user.id,
            type=NotificationType.SYSTEM_ANNOUNCEMENT,
            title="Welcome to AI Matchmaker!",
            message="Complete your personality assessment to start finding compatible matches.",
            priority=2,
            action_url="/onboarding/personality"
        )
        
        self.db.add(welcome_notification)
        await self.db.commit()
        
        # TODO: Send email verification
        # await self.send_verification_email(user)
        
        # Create session and return login response
        session = await create_user_session(user, request)
        
        access_token = create_access_token({
            "sub": str(user.id),
            "session": session.session_token
        })
        
        return UserLoginResponse(
            access_token=access_token,
            refresh_token=session.refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )
    
    async def authenticate_user(
        self, 
        login_data: UserLogin, 
        request: Request
    ) -> UserLoginResponse:
        """Authenticate user and create session."""
        
        # Get user by email
        result = await self.db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")
        
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        
        # Update last active timestamp
        user.last_active = datetime.utcnow()
        await self.db.commit()
        
        # Create session
        session = await create_user_session(user, request, login_data.device_info)
        
        # Create access token
        token_data = {"sub": str(user.id), "session": session.session_token}
        access_token = create_access_token(token_data)
        
        # Update online status
        online_status = UserOnlineStatus(
            user_id=str(user.id),
            is_online=True,
            current_activity="browsing",
            device_type=login_data.device_info.get("type", "web") if login_data.device_info else "web"
        )
        await online_status.save_online_status()
        
        return UserLoginResponse(
            access_token=access_token,
            refresh_token=session.refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )
    
    async def update_user_profile(
        self, 
        user: User, 
        update_data: UserUpdate
    ) -> UserResponse:
        """Update user profile."""
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        if update_dict:
            for field, value in update_dict.items():
                setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(user)
        
        return UserResponse.model_validate(user)
    
    async def change_password(
        self, 
        user: User, 
        password_data: PasswordChange
    ) -> Dict[str, str]:
        """Change user password."""
        
        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.password_hash = get_password_hash(password_data.new_password)
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # TODO: Revoke all existing sessions except current one
        # await revoke_all_user_sessions(str(user.id))
        
        return {"message": "Password changed successfully"}
    
    async def request_password_reset(
        self, 
        reset_data: PasswordReset
    ) -> Dict[str, str]:
        """Request password reset."""
        
        # Get user by email
        result = await self.db.execute(
            select(User).where(User.email == reset_data.email)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Generate reset token
            reset_token = generate_reset_token()
            
            # Store reset token in Redis with 1 hour expiry
            redis_client.setex(
                f"password_reset:{reset_token}",
                3600,  # 1 hour
                str(user.id)
            )
            
            # TODO: Send password reset email
            # await self.send_password_reset_email(user, reset_token)
        
        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a password reset link has been sent"}
    
    async def confirm_password_reset(
        self, 
        reset_data: PasswordResetConfirm
    ) -> Dict[str, str]:
        """Confirm password reset with token."""
        
        # Get user ID from Redis
        user_id = redis_client.get(f"password_reset:{reset_data.token}")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Get user
        user = await self.db.get(User, uuid.UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        user.password_hash = get_password_hash(reset_data.new_password)
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # Delete reset token
        redis_client.delete(f"password_reset:{reset_data.token}")
        
        # TODO: Revoke all existing sessions
        # await revoke_all_user_sessions(str(user.id))
        
        return {"message": "Password reset successfully"}
    
    async def verify_email(self, token: str) -> Dict[str, str]:
        """Verify user email with token."""
        
        # Get user ID from Redis
        user_id = redis_client.get(f"email_verification:{token}")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Get user
        user = await self.db.get(User, uuid.UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update verification status
        user.is_verified = True
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # Delete verification token
        redis_client.delete(f"email_verification:{token}")
        
        return {"message": "Email verified successfully"}
    
    async def get_user_profile_completeness(self, user: User) -> UserProfileCompleteness:
        """Calculate user profile completeness."""
        
        sections = {}
        missing_items = []
        suggestions = []
        
        # Basic profile section
        basic_score = 0
        basic_total = 6
        
        if user.first_name:
            basic_score += 1
        else:
            missing_items.append("First name")
            
        if user.last_name:
            basic_score += 1
        else:
            missing_items.append("Last name")
            
        if user.date_of_birth:
            basic_score += 1
        else:
            missing_items.append("Date of birth")
            
        if user.gender:
            basic_score += 1
        else:
            missing_items.append("Gender")
            
        if user.location:
            basic_score += 1
        else:
            missing_items.append("Location")
            
        if user.bio:
            basic_score += 1
        else:
            missing_items.append("Bio")
            
        sections["basic_profile"] = basic_score / basic_total
        
        # Photos section
        # TODO: Check for user photos
        sections["photos"] = 0.0
        missing_items.append("Profile photos")
        
        # Personality profile section
        # TODO: Check personality profile completeness
        sections["personality"] = 0.0
        missing_items.append("Personality assessment")
        
        # Dating preferences section
        # TODO: Check dating preferences completeness
        sections["preferences"] = 0.0
        missing_items.append("Dating preferences")
        
        # Calculate overall score
        overall_score = sum(sections.values()) / len(sections)
        
        # Generate suggestions
        if overall_score < 0.5:
            suggestions.append("Complete your basic profile information")
            suggestions.append("Take the personality assessment")
            suggestions.append("Upload profile photos")
        elif overall_score < 0.8:
            suggestions.append("Add more details to your bio")
            suggestions.append("Set your dating preferences")
        else:
            suggestions.append("Your profile looks great!")
        
        return UserProfileCompleteness(
            overall_score=overall_score,
            sections=sections,
            missing_items=missing_items,
            suggestions=suggestions
        )
    
    async def get_user_stats(self, user: User) -> UserStats:
        """Get user statistics."""
        
        # TODO: Implement actual statistics queries
        # For now, return mock data
        
        return UserStats(
            total_matches=0,
            mutual_matches=0,
            conversations_started=0,
            profile_views=0,
            compatibility_reports=0,
            average_compatibility_score=None,
            join_date=user.created_at,
            last_active=user.last_active
        )
    
    async def deactivate_account(self, user: User) -> Dict[str, str]:
        """Deactivate user account."""
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # TODO: Revoke all sessions
        # await revoke_all_user_sessions(str(user.id))
        
        return {"message": "Account deactivated successfully"}
    
    async def delete_account(self, user: User) -> Dict[str, str]:
        """Delete user account (soft delete)."""
        
        # In a real application, you might want to:
        # 1. Anonymize user data instead of deleting
        # 2. Keep some data for legal/business reasons
        # 3. Implement a grace period before actual deletion
        
        user.is_active = False
        user.email = f"deleted_{user.id}@deleted.com"
        user.username = f"deleted_{user.id}"
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # TODO: Clean up related data
        # TODO: Revoke all sessions
        
        return {"message": "Account deletion initiated"}