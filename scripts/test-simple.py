#!/usr/bin/env python3
"""
Simple connection test script for AI Matchmaker.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed, using environment variables only")

async def test_database():
    """Test database connection."""
    print("Testing database connection...")
    try:
        # Import with better error handling
        try:
            from app.core.config import settings
            print(f"  Database URL: {settings.DATABASE_URL[:50]}...")
        except Exception as config_error:
            print(f"  Config error: {config_error}")
            return False
            
        from app.core.database import engine
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_redis():
    """Test Redis connection."""
    print("Testing Redis connection...")
    try:
        import redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        print(f"  Redis URL: {redis_url[:50]}...")
        
        r = redis.from_url(redis_url)
        r.ping()
        print("✓ Redis connection successful")
        return True
    except ImportError:
        print("✗ Redis module not installed. Run: pip install redis")
        return False
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False

async def main():
    """Main test function."""
    print("AI Matchmaker Connection Test")
    print("=" * 40)
    
    # Check environment variables
    print("Environment check:")
    db_url = os.getenv('DATABASE_URL')
    redis_url = os.getenv('REDIS_URL')
    
    if not db_url:
        print("  ✗ DATABASE_URL not set")
    else:
        print(f"  ✓ DATABASE_URL: {db_url[:50]}...")
        
    if not redis_url:
        print("  ✗ REDIS_URL not set")
    else:
        print(f"  ✓ REDIS_URL: {redis_url[:50]}...")
    
    print()
    
    # Test database
    db_ok = await test_database()
    
    # Test Redis
    redis_ok = test_redis()
    
    print("=" * 40)
    if db_ok and redis_ok:
        print("✓ All connections successful!")
        return 0
    else:
        print("✗ Some connections failed!")
        print("\nTroubleshooting:")
        if not db_ok:
            print("- Check DATABASE_URL in .env file")
            print("- Ensure remote PostgreSQL is accessible")
        if not redis_ok:
            print("- Run: pip install redis")
            print("- Check REDIS_URL in .env file")
            print("- Ensure remote Redis is accessible")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)