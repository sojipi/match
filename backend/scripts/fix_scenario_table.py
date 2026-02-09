"""
Fix scenario_templates table by adding missing columns.
Run from project root with venv activated: python backend/scripts/fix_scenario_table.py
"""
import asyncio
import sys
import os

# Ensure we're running from the correct directory
if not os.path.exists('backend'):
    print("Error: Please run this script from the project root directory")
    print("Usage: python backend/scripts/fix_scenario_table.py")
    sys.exit(1)

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


async def fix_table():
    """Add missing columns to scenario_templates table."""
    
    print("Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    try:
        async with engine.begin() as conn:
            print("\nChecking for missing columns...")
            
            # Check if setup_prompt exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'scenario_templates' 
                AND column_name = 'setup_prompt'
            """))
            
            if result.fetchone() is None:
                print("\n[+] Adding setup_prompt column...")
                await conn.execute(text("""
                    ALTER TABLE scenario_templates
                    ADD COLUMN setup_prompt TEXT
                """))

                print("[+] Setting default values...")
                await conn.execute(text("""
                    UPDATE scenario_templates
                    SET setup_prompt = COALESCE(description, title, 'Default setup prompt')
                    WHERE setup_prompt IS NULL
                """))

                print("[+] Making column NOT NULL...")
                await conn.execute(text("""
                    ALTER TABLE scenario_templates
                    ALTER COLUMN setup_prompt SET NOT NULL
                """))

                print("\n[+] setup_prompt column added successfully!")
            else:
                print("\n[+] setup_prompt column already exists")
            
            # Verify all required columns exist
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
        
        print("\n[+] Table structure fixed successfully!")
        print("\nYou can now:")
        print("  1. Restart the backend server")
        print("  2. Test the scenario API endpoints")

    except Exception as e:
        print(f"\n[!] Error fixing table: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(fix_table())
