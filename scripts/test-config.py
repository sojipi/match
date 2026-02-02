#!/usr/bin/env python3
"""
Test script to verify configuration reads .env file correctly.
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

def test_config():
    """Test configuration loading."""
    print("Testing configuration loading...")
    
    try:
        from app.core.config import settings, ENV_FILE_PATH
        
        print(f"  ✓ ENV file path: {ENV_FILE_PATH}")
        print(f"  ✓ ENV file exists: {ENV_FILE_PATH.exists()}")
        
        # Test some key configuration values
        print(f"  ✓ DEBUG: {settings.DEBUG}")
        print(f"  ✓ ENVIRONMENT: {settings.ENVIRONMENT}")
        print(f"  ✓ SECRET_KEY: {settings.SECRET_KEY[:20]}...")
        print(f"  ✓ DATABASE_URL: {settings.DATABASE_URL[:50]}...")
        print(f"  ✓ REDIS_URL: {settings.REDIS_URL[:50]}...")
        print(f"  ✓ GEMINI_API_KEY: {settings.GEMINI_API_KEY[:20]}...")
        
        # Check if values are coming from .env (not defaults)
        if settings.SECRET_KEY == "your-secret-key-change-in-production":
            print("  ⚠ WARNING: SECRET_KEY is using default value, not from .env")
        else:
            print("  ✓ SECRET_KEY loaded from .env")
            
        if settings.DATABASE_URL.startswith("postgresql+asyncpg://user:pass@localhost"):
            print("  ⚠ WARNING: DATABASE_URL is using default value, not from .env")
        else:
            print("  ✓ DATABASE_URL loaded from .env")
            
        if settings.REDIS_URL == "redis://localhost:6379":
            print("  ⚠ WARNING: REDIS_URL is using default value, not from .env")
        else:
            print("  ✓ REDIS_URL loaded from .env")
        
        print("✓ Configuration test completed!")
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)