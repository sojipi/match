"""
Add missing columns to scenario_templates table.
Run from project root with venv activated: python backend/scripts/add_missing_columns.py
"""
import asyncio
import sys
import os

# Ensure we're running from the correct directory
if not os.path.exists('backend'):
    print("Error: Please run this script from the project root directory")
    print("Usage: python backend/scripts/add_missing_columns.py")
    sys.exit(1)

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


async def add_missing_columns():
    """Add missing columns to scenario_templates table."""

    print("Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    try:
        async with engine.begin() as conn:
            print("\nAdding missing columns...")

            # Add resolution_prompts
            print("\n[+] Adding resolution_prompts column...")
            await conn.execute(text("""
                ALTER TABLE scenario_templates
                ADD COLUMN IF NOT EXISTS resolution_prompts JSONB DEFAULT '[]'::jsonb
            """))

            # Add completion_rate
            print("[+] Adding completion_rate column...")
            await conn.execute(text("""
                ALTER TABLE scenario_templates
                ADD COLUMN IF NOT EXISTS completion_rate DOUBLE PRECISION DEFAULT 0.0
            """))

            # Add content_warnings
            print("[+] Adding content_warnings column...")
            await conn.execute(text("""
                ALTER TABLE scenario_templates
                ADD COLUMN IF NOT EXISTS content_warnings JSONB DEFAULT '[]'::jsonb
            """))

            # Add tags
            print("[+] Adding tags column...")
            await conn.execute(text("""
                ALTER TABLE scenario_templates
                ADD COLUMN IF NOT EXISTS tags JSONB DEFAULT '[]'::jsonb
            """))

            # Add keywords
            print("[+] Adding keywords column...")
            await conn.execute(text("""
                ALTER TABLE scenario_templates
                ADD COLUMN IF NOT EXISTS keywords JSONB DEFAULT '[]'::jsonb
            """))

            # Add language_variants
            print("[+] Adding language_variants column...")
            await conn.execute(text("""
                ALTER TABLE scenario_templates
                ADD COLUMN IF NOT EXISTS language_variants JSONB DEFAULT '{}'::jsonb
            """))

            # Verify all columns exist
            print("\nVerifying table structure...")
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'scenario_templates'
                ORDER BY ordinal_position
            """))

            columns = result.fetchall()
            print(f"\nFound {len(columns)} columns in scenario_templates table:")
            for col in columns:
                nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                print(f"  - {col[0]}: {col[1]} ({nullable})")

        print("\n[+] All missing columns added successfully!")
        print("\nYou can now:")
        print("  1. Restart the backend server")
        print("  2. Test the scenario API endpoints")

    except Exception as e:
        print(f"\n[!] Error adding columns: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_missing_columns())
