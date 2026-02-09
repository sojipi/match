"""
Create scenario tables in the database.
Run from project root with venv activated: python backend/scripts/create_scenario_tables.py
"""
import asyncio
import sys
import os

# Ensure we're running from the correct directory
if not os.path.exists('backend'):
    print("Error: Please run this script from the project root directory")
    print("Usage: python backend/scripts/create_scenario_tables.py")
    sys.exit(1)

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.database import Base
from app.models.scenario import ScenarioTemplate, SimulationSession, SimulationMessage, ScenarioResult


async def create_tables():
    """Create all scenario-related tables."""
    
    print("Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    try:
        print("\nCreating scenario tables...")
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            from app.models import user, match, scenario
            
            # Create only scenario tables
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        
        print("\n✓ Scenario tables created successfully!")
        print("\nCreated tables:")
        print("  - scenario_templates")
        print("  - simulation_sessions")
        print("  - simulation_messages")
        print("  - scenario_results")
        print("\nYou can now run: python backend/scripts/seed_scenarios.py")
        
    except Exception as e:
        print(f"\n✗ Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_tables())
