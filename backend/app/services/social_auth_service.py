"""
Social authentication service for Google and Facebook login.
"""
from typing import Optional, Dict, Any
from datetime import datetime
import httpx
from fastapi import HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.models.user import User, PersonalityProfile, DatingPreferences
from app.schemas.auth import SocialLoginRequest, UserLoginResponse, UserResponse
from app.core.security import create_user_session, create_access_token
from app.core.config import settings


class SocialAuthService:
    """Social authentication service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def authenticate_google(
        self, 
        social_data: SocialLoginRequest, 
        request: Request
    ) -> UserLoginResponse:
        """Authenticate user with Google OAuth."""
        
        # Verify Google access token
        user_info = await self._verify_google_token(social_data.access_token)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google access token"
            )
        
        # Get or create user
        user = await self._get_or_create_social_user(
            email=user_info["email"],
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
            provider="google",
            provider_id=user_info["id"]
        )
        
        # Create session and return response
        return await self._create_login_response(user, request, social_data.device_info)
    
    async def authenticate_facebook(
        self, 
        social_data: SocialLoginRequest, 
        request: Request
    ) -> UserLoginResponse:
        """Authenticate user with Facebook OAuth."""
        
        # Verify Facebook access token
        user_info = await self._verify_facebook_token(social_data.access_token)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Facebook access token"
            )
        
        # Get or create user
        user = await self._get_or_create_social_user(
            email=user_info["email"],
            first_name=user_info.get("first_name", ""),
            last_name=user_info.get("last_name", ""),
            provider="facebook",
            provider_id=user_info["id"]
        )
        
        # Create session and return response
        return await self._create_login_response(user, request, social_data.device_info)
    
    async def _verify_google_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Verify Google access token and get user info."""
        
        try:
            async with httpx.AsyncClient() as client:
                # Get user info from Google
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                
        except Exception:
            pass
        
        return None
    
    async def _verify_facebook_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Verify Facebook access token and get user info."""
        
        try:
            async with httpx.AsyncClient() as client:
                # Verify token with Facebook
                verify_response = await client.get(
                    f"https://graph.facebook.com/debug_token",
                    params={
                        "input_token": access_token,
                        "access_token": f"{settings.FACEBOOK_APP_ID}|{settings.FACEBOOK_APP_SECRET}"
                    }
                )
                
                if verify_response.status_code != 200:
                    return None
                
                verify_data = verify_response.json()
                if not verify_data.get("data", {}).get("is_valid"):
                    return None
                
                # Get user info
                user_response = await client.get(
                    "https://graph.facebook.com/me",
                    params={
                        "fields": "id,email,first_name,last_name",
                        "access_token": access_token
                    }
                )
                
                if user_response.status_code == 200:
                    return user_response.json()
                
        except Exception:
            pass
        
        return None
    
    async def _get_or_create_social_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        provider: str,
        provider_id: str
    ) -> User:
        """Get existing user or create new one for social login."""
        
        # Try to find existing user by email
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Update user if needed
            if not user.is_verified:
                user.is_verified = True  # Social logins are pre-verified
                await self.db.commit()
            return user
        
        # Create new user
        username = await self._generate_unique_username(email, first_name, last_name)
        
        user = User(
            id=uuid.uuid4(),
            email=email,
            username=username,
            password_hash="",  # No password for social users
            first_name=first_name,
            last_name=last_name,
            is_verified=True,  # Social logins are pre-verified
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
        await self.db.commit()
        
        return user
    
    async def _generate_unique_username(
        self, 
        email: str, 
        first_name: str, 
        last_name: str
    ) -> str:
        """Generate a unique username for social login."""
        
        # Start with email prefix
        base_username = email.split("@")[0].lower()
        
        # Clean up username (remove special characters)
        base_username = "".join(c for c in base_username if c.isalnum() or c in "_-")
        
        # If empty, use first name + last name
        if not base_username:
            base_username = f"{first_name.lower()}{last_name.lower()}"
            base_username = "".join(c for c in base_username if c.isalnum())
        
        # If still empty, use default
        if not base_username:
            base_username = "user"
        
        # Check if username exists and make it unique
        username = base_username
        counter = 1
        
        while True:
            result = await self.db.execute(
                select(User).where(User.username == username)
            )
            if not result.scalar_one_or_none():
                break
            
            username = f"{base_username}{counter}"
            counter += 1
        
        return username
    
    async def _create_login_response(
        self,
        user: User,
        request: Request,
        device_info: Optional[Dict[str, Any]] = None
    ) -> UserLoginResponse:
        """Create login response with session and tokens."""
        
        # Update last active
        user.last_active = datetime.utcnow()
        await self.db.commit()
        
        # Create session
        session = await create_user_session(user, request, device_info)
        
        # Create access token
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