"""
Fix database schema for conversation_messages table.
Add missing sender_id column.
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def fix_schema():
    async with engine.begin() as conn:
        print("Checking conversation_messages table schema...")

        # Check if sender_id column exists
        result = await conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'conversation_messages'
            AND column_name = 'sender_id'
        """))

        exists = result.fetchone()

        if not exists:
            print("Adding sender_id column...")
            await conn.execute(text("""
                ALTER TABLE conversation_messages
                ADD COLUMN sender_id VARCHAR(100) NOT NULL DEFAULT ''
            """))
            print("✅ Added sender_id column successfully!")
        else:
            print("✅ sender_id column already exists")

        # Show current table structure
        result = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'conversation_messages'
            ORDER BY ordinal_position
        """))

        print("\nCurrent table structure:")
        for row in result:
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")

if __name__ == "__main__":
    asyncio.run(fix_schema())
