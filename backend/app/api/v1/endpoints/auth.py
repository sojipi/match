"""
Authentication endpoints.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    get_current_user, get_current_verified_user, refresh_access_token,
    revoke_session, revoke_all_user_sessions
)
from app.models.user import User
from app.schemas.auth import (
    UserCreate, UserUpdate, UserLogin, UserLoginResponse,
    TokenRefresh, TokenResponse, PasswordChange, PasswordReset,
    PasswordResetConfirm, EmailVerification, UserResponse,
    UserProfileCompleteness, UserStats, SocialLoginRequest
)
from app.services.auth_service import AuthService
from app.services.social_auth_service import SocialAuthService

router = APIRouter()


@router.post("/register", response_model=UserLoginResponse)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    auth_service = AuthService(db)
    return await auth_service.register_user(user_data, request)


@router.post("/login", response_model=UserLoginResponse)
async def login(
    user_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Login user."""
    auth_service = AuthService(db)
    return await auth_service.authenticate_user(user_data, request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh):
    """Refresh access token."""
    return await refresh_access_token(token_data.refresh_token)


@router.post("/logout")
async def logout(
    session_token: str = None,
    current_user: User = Depends(get_current_user)
):
    """Logout user (revoke session)."""
    if session_token:
        success = await revoke_session(session_token)
        if success:
            return {"message": "Session revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to revoke session"
            )
    
    return {"message": "Logout successful"}


@router.post("/logout-all")
async def logout_all(current_user: User = Depends(get_current_user)):
    """Logout from all devices (revoke all sessions)."""
    success = await revoke_all_user_sessions(str(current_user.id))
    if success:
        return {"message": "All sessions revoked successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke all sessions"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile."""
    auth_service = AuthService(db)
    return await auth_service.update_user_profile(current_user, update_data)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Change user password."""
    auth_service = AuthService(db)
    return await auth_service.change_password(current_user, password_data)


@router.post("/request-password-reset")
async def request_password_reset(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Request password reset."""
    auth_service = AuthService(db)
    return await auth_service.request_password_reset(reset_data)


@router.post("/confirm-password-reset")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Confirm password reset with token."""
    auth_service = AuthService(db)
    return await auth_service.confirm_password_reset(reset_data)


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerification,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Verify user email with token."""
    auth_service = AuthService(db)
    return await auth_service.verify_email(verification_data.token)


@router.get("/profile-completeness", response_model=UserProfileCompleteness)
async def get_profile_completeness(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user profile completeness score."""
    auth_service = AuthService(db)
    return await auth_service.get_user_profile_completeness(current_user)


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user statistics."""
    auth_service = AuthService(db)
    return await auth_service.get_user_stats(current_user)


@router.post("/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Deactivate user account."""
    auth_service = AuthService(db)
    return await auth_service.deactivate_account(current_user)


@router.delete("/delete")
async def delete_account(
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Delete user account."""
    auth_service = AuthService(db)
    return await auth_service.delete_account(current_user)


@router.post("/social/google", response_model=UserLoginResponse)
async def google_login(
    social_data: SocialLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Login with Google OAuth."""
    if social_data.provider != "google":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider for Google login"
        )
    
    social_auth_service = SocialAuthService(db)
    return await social_auth_service.authenticate_google(social_data, request)


@router.post("/social/facebook", response_model=UserLoginResponse)
async def facebook_login(
    social_data: SocialLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Login with Facebook OAuth."""
    if social_data.provider != "facebook":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider for Facebook login"
        )
    
    social_auth_service = SocialAuthService(db)
    return await social_auth_service.authenticate_facebook(social_data, request)