"""
Fix difficulty_level column to use proper enum type.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


async def fix_difficulty_column():
    """Fix difficulty_level column to use the scenariodifficulty enum type."""

    print("Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    try:
        async with engine.begin() as conn:
            print("\n[+] Step 1: Mapping integer values to enum values...")

            # Map: 1=EASY, 2=MODERATE, 3=CHALLENGING, 4=DIFFICULT, 5=EXPERT
            # First, create a temporary column
            await conn.execute(text("""
                ALTER TABLE scenario_templates
                ADD COLUMN difficulty_level_temp scenariodifficulty
            """))

            print("\n[+] Step 2: Converting integer values to enum...")
            await conn.execute(text("""
                UPDATE scenario_templates
                SET difficulty_level_temp = CASE difficulty_level
                    WHEN 1 THEN 'EASY'::scenariodifficulty
                    WHEN 2 THEN 'MODERATE'::scenariodifficulty
                    WHEN 3 THEN 'CHALLENGING'::scenariodifficulty
                    WHEN 4 THEN 'DIFFICULT'::scenariodifficulty
                    WHEN 5 THEN 'EXPERT'::scenariodifficulty
                    ELSE 'MODERATE'::scenariodifficulty
                END
            """))

            print("\n[+] Step 3: Dropping old column...")
            await conn.execute(text("""
                ALTER TABLE scenario_templates
                DROP COLUMN difficulty_level
            """))

            print("\n[+] Step 4: Renaming new column...")
            await conn.execute(text("""
                ALTER TABLE scenario_templates
                RENAME COLUMN difficulty_level_temp TO difficulty_level
            """))

            print("\n[+] Step 5: Verifying column type...")
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

            # Verify values
            result = await conn.execute(text("""
                SELECT DISTINCT difficulty_level FROM scenario_templates
            """))
            values = [row[0] for row in result.fetchall()]
            print(f"\nDistinct values: {values}")

        print("\n[+] Difficulty level column fixed successfully!")
        print("\nYou can now:")
        print("  1. Restart the backend server")
        print("  2. Test the scenario API endpoints")

    except Exception as e:
        print(f"\n[!] Error fixing column: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(fix_difficulty_column())
