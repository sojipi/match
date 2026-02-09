"""
Test scenario endpoints to verify the fix.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.scenario import ScenarioTemplate


async def test_scenario_query():
    """Test querying scenarios to verify enum works."""

    print("Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            print("\n[+] Testing scenario query with SQLAlchemy ORM...")

            # Query all active scenarios
            result = await session.execute(
                select(ScenarioTemplate)
                .where(ScenarioTemplate.is_active == True)
                .where(ScenarioTemplate.is_approved == True)
            )

            scenarios = result.scalars().all()
            print(f"\nFound {len(scenarios)} scenarios:")
            for scenario in scenarios:
                print(f"  - {scenario.name} (category: {scenario.category.value})")

            print("\n[+] Query successful! Enum conversion is working.")

    except Exception as e:
        print(f"\n[!] Error querying scenarios: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_scenario_query())
