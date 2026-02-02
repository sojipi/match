#!/usr/bin/env python3
"""
Simple database migration script for AI Matchmaker.
"""
import asyncio
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

async def main():
    """Run database migrations."""
    print("AI Matchmaker Database Migration")
    print("=" * 40)
    
    try:
        from app.core.database import init_db
        
        print("Initializing database tables...")
        await init_db()
        print("✓ Database initialization complete!")
        return 0
        
    except Exception as e:
        print(f"✗ Database migration failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)