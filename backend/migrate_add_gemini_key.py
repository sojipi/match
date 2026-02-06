#!/usr/bin/env python3
"""
Database migration script to add gemini_api_key column to users table.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine


async def migrate():
    """Add gemini_api_key column to users table."""
    print("🔄 Starting database migration...")
    
    async with engine.begin() as conn:
        try:
            # Check if column already exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='gemini_api_key'
            """))
            
            if result.fetchone():
                print("✅ Column 'gemini_api_key' already exists, skipping migration")
                return
            
            # Add the column
            await conn.execute(text("""
                ALTER TABLE users ADD COLUMN gemini_api_key VARCHAR(255)
            """))
            
            print("✅ Successfully added 'gemini_api_key' column to users table")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(migrate())
    print("🎉 Migration completed!")