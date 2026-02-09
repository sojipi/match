"""
Fix category values and column type.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


async def fix_category_values():
    """Fix category values to match enum and convert column type."""

    print("Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    try:
        async with engine.begin() as conn:
            print("\n[+] Step 1: Updating category values to uppercase...")

            # Update all category values to uppercase
            await conn.execute(text("""
                UPDATE scenario_templates
                SET category = UPPER(category)
            """))

            print("\n[+] Step 2: Verifying updated values...")
            result = await conn.execute(text("""
                SELECT DISTINCT category FROM scenario_templates
            """))
            categories = [row[0] for row in result.fetchall()]
            print(f"Categories after update: {categories}")

            print("\n[+] Step 3: Converting column to enum type...")
            await conn.execute(text("""
                ALTER TABLE scenario_templates
                ALTER COLUMN category TYPE scenariocategory
                USING category::scenariocategory
            """))

            print("\n[+] Step 4: Verifying column type...")
            result = await conn.execute(text("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'scenario_templates'
                AND column_name = 'category'
            """))

            row = result.fetchone()
            print(f"\nColumn: {row[0]}")
            print(f"Data Type: {row[1]}")
            print(f"UDT Name: {row[2]}")

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
    asyncio.run(fix_category_values())
