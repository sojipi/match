#!/usr/bin/env python3
"""
Test script to verify backend imports work correctly.
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test all critical imports."""
    print("Testing backend imports...")
    
    try:
        print("  ✓ Testing core config...")
        from app.core.config import settings
        
        print("  ✓ Testing database...")
        from app.core.database import Base, get_db, init_db
        
        print("  ✓ Testing models...")
        from app.models import user, match, conversation
        
        print("  ✓ Testing API router...")
        from app.api.v1.api import api_router
        
        print("  ✓ Testing websocket manager...")
        from app.websocket.manager import router as websocket_router
        
        print("  ✓ Testing main application...")
        from main import app
        
        print("✓ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)