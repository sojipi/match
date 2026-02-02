"""
Security utilities for authentication and authorization.
"""
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
import hashlib
import uuid

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.redis_models import UserSession, redis_client

# HTTP Bearer token scheme
security = HTTPBearer()


class AuthenticationError(HTTPException):
    """Custom authentication error."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom authorization error."""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != token_type:
            raise AuthenticationError("Invalid token type")
        return payload
    except JWTError:
        raise AuthenticationError("Could not validate credentials")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    # Truncate password to 72 bytes for bcrypt
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Convert hash string to bytes if needed
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password."""
    # Bcrypt has a 72 byte limit, truncate if necessary
    # Using UTF-8 encoding to count bytes properly
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode('utf-8')


def generate_verification_token() -> str:
    """Generate email verification token."""
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """Generate password reset token."""
    return secrets.token_urlsafe(32)


def create_session_token() -> str:
    """Create unique session token."""
    return secrets.token_urlsafe(32)


async def create_user_session(
    user: User,
    request: Request,
    device_info: Optional[Dict[str, Any]] = None
) -> UserSession:
    """Create a new user session."""
    
    session_token = create_session_token()
    refresh_token = create_refresh_token({"sub": str(user.id), "session": session_token})
    
    # Extract request information
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Create session
    session = UserSession(
        user_id=str(user.id),
        session_token=session_token,
        refresh_token=refresh_token,
        device_info=device_info or {},
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    # Save to Redis
    session.save_session()
    
    return session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    
    token = credentials.credentials
    
    try:
        # Verify access token
        payload = verify_token(token, "access")
        user_id = payload.get("sub")
        session_token = payload.get("session")
        
        if not user_id:
            raise AuthenticationError("Invalid token payload")
        
        # Check if session exists in Redis (optional but recommended)
        if session_token:
            session = UserSession.get_session(session_token)
            if not session or session.user_id != user_id:
                raise AuthenticationError("Session not found or invalid")
        
        # Get user from database
        user = await db.get(User, uuid.UUID(user_id))
        if not user:
            raise AuthenticationError("User not found")
        
        if not user.is_active:
            raise AuthenticationError("User account is disabled")
        
        return user
        
    except JWTError:
        raise AuthenticationError("Could not validate credentials")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (alias for consistency)."""
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current verified user."""
    if not current_user.is_verified:
        raise AuthorizationError("Email verification required")
    return current_user


async def refresh_access_token(refresh_token: str) -> Dict[str, str]:
    """Refresh access token using refresh token."""
    
    try:
        # Verify refresh token
        payload = verify_token(refresh_token, "refresh")
        user_id = payload.get("sub")
        session_token = payload.get("session")
        
        if not user_id or not session_token:
            raise AuthenticationError("Invalid refresh token payload")
        
        # Check if session exists
        session = UserSession.get_session(session_token)
        if not session or session.user_id != user_id:
            raise AuthenticationError("Session not found or expired")
        
        # Create new access token
        access_token = create_access_token({
            "sub": user_id,
            "session": session_token
        })
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise AuthenticationError("Invalid refresh token")


async def revoke_session(session_token: str) -> bool:
    """Revoke a user session."""
    session = UserSession.get_session(session_token)
    if session:
        return session.delete_session()
    return False


async def revoke_all_user_sessions(user_id: str) -> bool:
    """Revoke all sessions for a user."""
    try:
        # Get all session keys for the user
        pattern = "session:*"
        keys = redis_client.keys(pattern)
        
        sessions_to_delete = []
        for key in keys:
            session_data = redis_client.get(key)
            if session_data:
                try:
                    session = UserSession.model_validate_json(session_data)
                    if session.user_id == user_id:
                        sessions_to_delete.append(key)
                except Exception:
                    continue
        
        if sessions_to_delete:
            redis_client.delete(*sessions_to_delete)
        
        return True
    except Exception:
        return False


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength."""

    errors = []
    score = 0

    # Length check
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    else:
        score += 1

    # Maximum length check (bcrypt limitation)
    if len(password.encode('utf-8')) > 72:
        errors.append("Password cannot exceed 72 bytes")
    else:
        score += 1
    
    # Character variety checks
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if not has_lower:
        errors.append("Password must contain at least one lowercase letter")
    else:
        score += 1
        
    if not has_upper:
        errors.append("Password must contain at least one uppercase letter")
    else:
        score += 1
        
    if not has_digit:
        errors.append("Password must contain at least one number")
    else:
        score += 1
        
    if not has_special:
        errors.append("Password must contain at least one special character")
    else:
        score += 1
    
    # Common password check (basic)
    common_passwords = [
        "password", "123456", "password123", "admin", "qwerty",
        "letmein", "welcome", "monkey", "dragon"
    ]
    
    if password.lower() in common_passwords:
        errors.append("Password is too common")
        score = max(0, score - 2)
    
    # Determine strength
    if score >= 5:
        strength = "strong"
    elif score >= 3:
        strength = "medium"
    else:
        strength = "weak"
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "strength": strength,
        "score": score
    }


def generate_api_key(user_id: str) -> str:
    """Generate API key for user."""
    # Create a unique API key based on user ID and timestamp
    timestamp = str(int(datetime.utcnow().timestamp()))
    data = f"{user_id}:{timestamp}:{secrets.token_hex(16)}"
    
    # Hash the data to create the API key
    api_key = hashlib.sha256(data.encode()).hexdigest()
    
    return f"ak_{api_key[:32]}"  # Prefix with 'ak_' for identification


async def verify_api_key(api_key: str, db: AsyncSession) -> Optional[User]:
    """Verify API key and return associated user."""
    # This is a simplified implementation
    # In production, you'd store API keys in database with proper hashing
    
    if not api_key.startswith("ak_"):
        return None
    
    # For now, we'll use a simple Redis-based storage
    # In production, use proper database storage with hashing
    user_id = redis_client.get(f"api_key:{api_key}")
    
    if user_id:
        user = await db.get(User, uuid.UUID(user_id))
        if user and user.is_active:
            return user
    
    return None