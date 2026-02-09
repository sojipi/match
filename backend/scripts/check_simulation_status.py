"""
Check if simulationstatus enum exists in database.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


async def check_simulation_status_enum():
    """Check if simulationstatus enum exists."""

    print("Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL)

    try:
        async with engine.connect() as conn:
            # Check if enum type exists
            result = await conn.execute(text("""
                SELECT typname, typtype
                FROM pg_type
                WHERE typname = 'simulationstatus'
            """))

            row = result.fetchone()
            if row:
                print(f"\n[+] simulationstatus enum exists: {row[0]} (type: {row[1]})")

                # Get enum values
                result = await conn.execute(text("""
                    SELECT enumlabel
                    FROM pg_enum
                    WHERE enumtypid = (
                        SELECT oid FROM pg_type WHERE typname = 'simulationstatus'
                    )
                    ORDER BY enumsortorder
                """))

                enum_values = [r[0] for r in result.fetchall()]
                print(f"\nEnum values: {enum_values}")
            else:
                print("\n[!] simulationstatus enum does NOT exist in database")

            # Check simulation_sessions table status column
            result = await conn.execute(text("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'simulation_sessions'
                AND column_name = 'status'
            """))

            row = result.fetchone()
            if row:
                print(f"\nstatus column in simulation_sessions:")
                print(f"  Column: {row[0]}")
                print(f"  Data Type: {row[1]}")
                print(f"  UDT Name: {row[2]}")
            else:
                print("\n[!] status column not found in simulation_sessions")

    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_simulation_status_enum())
