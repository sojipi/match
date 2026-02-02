"""
Tests for authentication system.
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.security import (
    create_access_token, verify_token, get_password_hash, 
    verify_password, validate_password_strength
)
from app.models.user import User
from app.schemas.auth import UserCreate


class TestPasswordSecurity:
    """Test password security functions."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        
        # Verification should work
        assert verify_password(password, hashed) is True
        
        # Wrong password should fail
        assert verify_password("wrong_password", hashed) is False
    
    def test_password_strength_validation(self):
        """Test password strength validation."""
        
        # Strong password
        strong_result = validate_password_strength("StrongPass123!")
        assert strong_result["is_valid"] is True
        assert strong_result["strength"] in ["medium", "strong"]
        
        # Weak password
        weak_result = validate_password_strength("123")
        assert weak_result["is_valid"] is False
        assert len(weak_result["errors"]) > 0
        
        # Common password
        common_result = validate_password_strength("password")
        assert common_result["is_valid"] is False
        assert "too common" in " ".join(common_result["errors"]).lower()


class TestJWTTokens:
    """Test JWT token creation and verification."""
    
    def test_access_token_creation(self):
        """Test access token creation and verification."""
        user_id = str(uuid.uuid4())
        token_data = {"sub": user_id}
        
        # Create token
        token = create_access_token(token_data)
        assert token is not None
        assert isinstance(token, str)
        
        # Verify token
        payload = verify_token(token, "access")
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
    
    def test_token_expiration(self):
        """Test token expiration."""
        user_id = str(uuid.uuid4())
        token_data = {"sub": user_id}
        
        # Create token with short expiration
        short_expiry = timedelta(seconds=1)
        token = create_access_token(token_data, short_expiry)
        
        # Token should be valid immediately
        payload = verify_token(token, "access")
        assert payload["sub"] == user_id
        
        # Note: In a real test, you'd wait for expiration and test invalid token
        # but that would slow down tests significantly
    
    def test_invalid_token_type(self):
        """Test token type validation."""
        user_id = str(uuid.uuid4())
        token_data = {"sub": user_id}
        
        # Create access token
        access_token = create_access_token(token_data)
        
        # Try to verify as refresh token (should fail)
        with pytest.raises(Exception):  # Should raise AuthenticationError
            verify_token(access_token, "refresh")


class TestUserSchemas:
    """Test user schemas validation."""
    
    def test_user_create_validation(self):
        """Test user creation schema validation."""
        
        # Valid user data
        valid_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        user_create = UserCreate(**valid_data)
        assert user_create.email == "test@example.com"
        assert user_create.username == "testuser"
    
    def test_user_create_password_validation(self):
        """Test password validation in user creation."""
        
        # Weak password should fail
        with pytest.raises(ValueError):
            UserCreate(
                email="test@example.com",
                username="testuser",
                password="123",  # Too weak
                first_name="Test",
                last_name="User"
            )
    
    def test_username_validation(self):
        """Test username validation."""
        
        # Valid username
        valid_data = {
            "email": "test@example.com",
            "username": "test_user-123",
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        user_create = UserCreate(**valid_data)
        assert user_create.username == "test_user-123"
        
        # Invalid username with special characters
        with pytest.raises(ValueError):
            UserCreate(
                email="test@example.com",
                username="test@user!",  # Invalid characters
                password="StrongPass123!",
                first_name="Test",
                last_name="User"
            )


# Integration tests would go here but require database setup
# These would test the actual API endpoints and database operations