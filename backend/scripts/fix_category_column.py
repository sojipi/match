"""
Fix category column to use the proper enum type.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


async def fix_category_column():
    """Fix category column to use the scenariocategory enum type."""

    print("Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    try:
        async with engine.begin() as conn:
            print("\n[+] Altering category column to use scenariocategory enum...")

            # First, check if the enum type exists and has the right values
            result = await conn.execute(text("""
                SELECT enumlabel
                FROM pg_enum
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'scenariocategory'
                )
                ORDER BY enumsortorder
            """))

            enum_values = [row[0] for row in result.fetchall()]
            print(f"\nEnum values in database: {enum_values}")

            # Alter the column to use the enum type
            await conn.execute(text("""
                ALTER TABLE scenario_templates
                ALTER COLUMN category TYPE scenariocategory
                USING category::scenariocategory
            """))

            print("\n[+] Category column updated to use scenariocategory enum!")

            # Verify the change
            result = await conn.execute(text("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'scenario_templates'
                AND column_name = 'category'
            """))

            row = result.fetchone()
            print(f"\nVerification:")
            print(f"  Column: {row[0]}")
            print(f"  Data Type: {row[1]}")
            print(f"  UDT Name: {row[2]}")

        print("\n[+] Category column fixed successfully!")
        print("\nYou can now:")
        print("  1. Restart the backend server")
        print("  2. Test the scenario API endpoints")

    except Exception as e:
        print(f"\n[!] Error fixing column: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(fix_category_column())
