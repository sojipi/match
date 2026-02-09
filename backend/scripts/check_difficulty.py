"""
Check and fix difficulty_level column.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


async def check_difficulty():
    """Check difficulty_level column type and values."""

    print("Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL)

    try:
        async with engine.connect() as conn:
            # Check column type
            result = await conn.execute(text("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'scenario_templates'
                AND column_name = 'difficulty_level'
            """))

            row = result.fetchone()
            print(f"\nColumn: {row[0]}")
            print(f"Data Type: {row[1]}")
            print(f"UDT Name: {row[2]}")

            # Check distinct values
            result = await conn.execute(text("""
                SELECT DISTINCT difficulty_level FROM scenario_templates
            """))

            values = [row[0] for row in result.fetchall()]
            print(f"\nDistinct difficulty_level values: {values}")

            # Check enum values
            result = await conn.execute(text("""
                SELECT enumlabel
                FROM pg_enum
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'scenariodifficulty'
                )
                ORDER BY enumsortorder
            """))

            enum_values = [row[0] for row in result.fetchall()]
            print(f"\nEnum values in database: {enum_values}")

    except Exception as e:
        print(f"\n[!] Error: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_difficulty())
