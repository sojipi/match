"""
Check database column type for category.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


async def check_column_type():
    """Check database column type for category."""

    print("Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL)

    try:
        async with engine.connect() as conn:
            # Check column type
            result = await conn.execute(text("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'scenario_templates'
                AND column_name = 'category'
            """))

            row = result.fetchone()
            if row:
                print(f"\nColumn: {row[0]}")
                print(f"Data Type: {row[1]}")
                print(f"UDT Name: {row[2]}")
            else:
                print("\nCategory column not found!")

            # Check if there's an enum type
            result = await conn.execute(text("""
                SELECT typname, typtype
                FROM pg_type
                WHERE typname LIKE '%scenario%'
            """))

            rows = result.fetchall()
            if rows:
                print("\nPostgreSQL types related to scenario:")
                for row in rows:
                    print(f"  - {row[0]} (type: {row[1]})")

    except Exception as e:
        print(f"\n[!] Error: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_column_type())
