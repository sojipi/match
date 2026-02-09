"""
Comprehensive script to fix all scenario_templates table issues.
Run this script to fix all enum and column issues in one go.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


async def fix_all_issues():
    """Fix all scenario_templates table issues."""

    print("=" * 60)
    print("SCENARIO TEMPLATES TABLE FIX SCRIPT")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Add missing columns (resolution_prompts, etc.)")
    print("  2. Fix category column to use enum type")
    print("  3. Fix difficulty_level column to use enum type")
    print("=" * 60)

    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    try:
        async with engine.begin() as conn:
            # Step 1: Add missing columns
            print("\n[1/3] Adding missing columns...")

            missing_columns = [
                ("resolution_prompts", "JSONB DEFAULT '[]'::jsonb"),
                ("completion_rate", "DOUBLE PRECISION DEFAULT 0.0"),
                ("content_warnings", "JSONB DEFAULT '[]'::jsonb"),
                ("tags", "JSONB DEFAULT '[]'::jsonb"),
                ("keywords", "JSONB DEFAULT '[]'::jsonb"),
                ("language_variants", "JSONB DEFAULT '{}'::jsonb"),
            ]

            for col_name, col_type in missing_columns:
                try:
                    await conn.execute(text(f"""
                        ALTER TABLE scenario_templates
                        ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                    """))
                    print(f"  [+] Added {col_name}")
                except Exception as e:
                    print(f"  [!] {col_name} already exists or error: {e}")

            # Step 2: Fix category column
            print("\n[2/3] Fixing category column...")

            # Check current type
            result = await conn.execute(text("""
                SELECT data_type FROM information_schema.columns
                WHERE table_name = 'scenario_templates' AND column_name = 'category'
            """))
            current_type = result.fetchone()[0]

            if current_type != 'USER-DEFINED':
                print("  [+] Converting category values to uppercase...")
                await conn.execute(text("""
                    UPDATE scenario_templates
                    SET category = UPPER(category)
                    WHERE category != UPPER(category)
                """))

                print("  [+] Converting category column to enum type...")
                await conn.execute(text("""
                    ALTER TABLE scenario_templates
                    ALTER COLUMN category TYPE scenariocategory
                    USING category::scenariocategory
                """))
                print("  [+] Category column fixed!")
            else:
                print("  [+] Category column already using enum type")

            # Step 3: Fix difficulty_level column
            print("\n[3/3] Fixing difficulty_level column...")

            # Check current type
            result = await conn.execute(text("""
                SELECT data_type FROM information_schema.columns
                WHERE table_name = 'scenario_templates' AND column_name = 'difficulty_level'
            """))
            current_type = result.fetchone()[0]

            if current_type == 'integer':
                print("  [+] Creating temporary column...")
                await conn.execute(text("""
                    ALTER TABLE scenario_templates
                    ADD COLUMN difficulty_level_temp scenariodifficulty
                """))

                print("  [+] Converting integer values to enum...")
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

                print("  [+] Replacing old column...")
                await conn.execute(text("""
                    ALTER TABLE scenario_templates DROP COLUMN difficulty_level
                """))
                await conn.execute(text("""
                    ALTER TABLE scenario_templates
                    RENAME COLUMN difficulty_level_temp TO difficulty_level
                """))
                print("  [+] Difficulty level column fixed!")
            else:
                print("  [+] Difficulty level column already using enum type")

            # Verify final state
            print("\n" + "=" * 60)
            print("VERIFICATION")
            print("=" * 60)

            result = await conn.execute(text("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'scenario_templates'
                AND column_name IN ('category', 'difficulty_level', 'resolution_prompts')
                ORDER BY column_name
            """))

            print("\nKey columns:")
            for row in result.fetchall():
                print(f"  - {row[0]}: {row[1]} ({row[2]})")

        print("\n" + "=" * 60)
        print("ALL FIXES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Restart your backend server")
        print("  2. Test the scenario API endpoints")
        print("  3. The errors should now be resolved")

    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(fix_all_issues())
