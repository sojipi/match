#!/usr/bin/env python3
"""
Database initialization script.
Creates all tables and optionally seeds development data.
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import init_db
from app.core.seed_data import seed_development_data


async def main():
    """Initialize database and optionally seed data."""
    
    print("🚀 Initializing database...")
    
    try:
        # Create all tables
        await init_db()
        print("✅ Database tables created successfully!")
        
        # Ask if user wants to seed development data
        seed_data = input("\n🌱 Would you like to seed development data? (y/N): ").lower().strip()
        
        if seed_data in ['y', 'yes']:
            print("\n🌱 Seeding development data...")
            await seed_development_data()
            print("✅ Development data seeded successfully!")
        else:
            print("⏭️  Skipping development data seeding.")
        
        print("\n🎉 Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())