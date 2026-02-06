import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine

async def fix_database():
    """Add sender_id column to conversation_messages table."""
    try:
        async with engine.begin() as conn:
            print("Checking conversation_messages table...")

            # Check if column exists
            result = await conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'conversation_messages'
                AND column_name = 'sender_id'
            """))

            exists = result.fetchone()

            if exists:
                print("✅ sender_id column already exists")
            else:
                print("Adding sender_id column...")
                await conn.execute(text("""
                    ALTER TABLE conversation_messages
                    ADD COLUMN sender_id VARCHAR(100) NOT NULL DEFAULT ''
                """))
                print("✅ sender_id column added successfully!")

            print("\nDatabase schema is now correct!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(fix_database())
