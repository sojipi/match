#!/usr/bin/env python3
"""
Basic connection test script for AI Matchmaker (without config validation).
"""
import asyncio
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed, using environment variables only")

async def test_database():
    """Test database connection directly."""
    print("Testing database connection...")
    try:
        import asyncpg
        
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("✗ DATABASE_URL not set")
            return False
            
        print(f"  Connecting to: {db_url[:50]}...")
        
        # Parse the URL manually for asyncpg
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        conn = await asyncpg.connect(db_url)
        result = await conn.fetchval('SELECT 1')
        await conn.close()
        
        print("✓ Database connection successful")
        return True
        
    except ImportError:
        print("✗ asyncpg module not installed. Run: pip install asyncpg")
        return False
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_redis():
    """Test Redis connection directly."""
    print("Testing Redis connection...")
    try:
        import redis
        
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        print(f"  Connecting to: {redis_url[:50]}...")
        
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
    print("AI Matchmaker Basic Connection Test")
    print("=" * 45)
    
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
    
    # Test connections
    db_ok = await test_database()
    redis_ok = test_redis()
    
    print("=" * 45)
    if db_ok and redis_ok:
        print("✓ All connections successful!")
        return 0
    else:
        print("✗ Some connections failed!")
        print("\nNext steps:")
        if not db_ok:
            print("- Run: pip install asyncpg")
            print("- Check DATABASE_URL in .env file")
        if not redis_ok:
            print("- Run: pip install redis")
            print("- Check REDIS_URL in .env file")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)