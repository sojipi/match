"""
Check category values in scenario_templates table.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


async def check_categories():
    """Check category values in database."""

    print("Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL)

    try:
        async with engine.connect() as conn:
            # Check distinct categories
            result = await conn.execute(text("""
                SELECT DISTINCT category FROM scenario_templates
            """))

            rows = result.fetchall()
            print("\nCategories in database:")
            for row in rows:
                print(f"  - '{row[0]}' (type: {type(row[0]).__name__})")

            # Check count per category
            result = await conn.execute(text("""
                SELECT category, COUNT(*) as count
                FROM scenario_templates
                GROUP BY category
                ORDER BY count DESC
            """))

            rows = result.fetchall()
            print("\nCategory counts:")
            for row in rows:
                print(f"  - {row[0]}: {row[1]} scenarios")

    except Exception as e:
        print(f"\n[!] Error: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_categories())
