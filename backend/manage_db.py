"""
Database management utility script.
Provides common database operations for development and maintenance.
"""
import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine, Base
from app.models import *  # Import all models


async def create_all_tables():
    """Create all database tables."""
    print("Creating all database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ All tables created successfully")


async def drop_all_tables():
    """Drop all database tables."""
    print("WARNING: This will delete all data!")
    confirm = input("Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("Operation cancelled")
        return

    print("Dropping all database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("✓ All tables dropped successfully")


async def reset_database():
    """Reset database (drop and recreate all tables)."""
    await drop_all_tables()
    await create_all_tables()


async def show_tables():
    """Show all tables in the database."""
    print("\nDatabase Tables:")
    print("-" * 80)
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = result.fetchall()
        for i, (table_name,) in enumerate(tables, 1):
            print(f"{i:2}. {table_name}")
    print("-" * 80)
    print(f"Total: {len(tables)} tables")


async def show_table_info(table_name: str):
    """Show detailed information about a specific table."""
    print(f"\nTable: {table_name}")
    print("=" * 80)

    async with engine.begin() as conn:
        # Get column information
        result = await conn.execute(text("""
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = :table_name
            ORDER BY ordinal_position
        """), {"table_name": table_name})

        columns = result.fetchall()
        if not columns:
            print(f"Table '{table_name}' not found")
            return

        print("\nColumns:")
        print("-" * 80)
        print(f"{'Name':<30} {'Type':<20} {'Nullable':<10} {'Default'}")
        print("-" * 80)
        for col_name, data_type, is_nullable, col_default in columns:
            nullable = "YES" if is_nullable == 'YES' else "NO"
            default = col_default if col_default else ""
            print(f"{col_name:<30} {data_type:<20} {nullable:<10} {default}")

        # Get row count
        result = await conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        print("-" * 80)
        print(f"Total rows: {count}")


async def check_database_health():
    """Check database health and connectivity."""
    print("\nDatabase Health Check")
    print("=" * 80)

    try:
        async with engine.begin() as conn:
            # Check connection
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Database connection: OK")
            print(f"  PostgreSQL version: {version}")

            # Check tables
            result = await conn.execute(text("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            print(f"✓ Tables: {table_count} found")

            # Check for required tables
            required_tables = [
                'users', 'personality_profiles', 'dating_preferences',
                'notifications', 'matches', 'ai_avatars'
            ]

            result = await conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = ANY(:tables)
            """), {"tables": required_tables})

            existing_tables = {row[0] for row in result}
            missing_tables = set(required_tables) - existing_tables

            if missing_tables:
                print(f"⚠ Missing tables: {', '.join(missing_tables)}")
            else:
                print(f"✓ All required tables exist")

            # Check enum types
            result = await conn.execute(text("""
                SELECT typname
                FROM pg_type
                WHERE typtype = 'e'
                ORDER BY typname
            """))
            enum_types = [row[0] for row in result]
            print(f"✓ Enum types: {', '.join(enum_types)}")

        print("\n" + "=" * 80)
        print("Database health check completed successfully")

    except Exception as e:
        print(f"\n✗ Database health check failed: {e}")
        import traceback
        traceback.print_exc()


async def vacuum_database():
    """Run VACUUM ANALYZE on the database."""
    print("Running VACUUM ANALYZE...")
    async with engine.begin() as conn:
        await conn.execute(text("VACUUM ANALYZE"))
    print("✓ Database vacuumed successfully")


async def show_database_size():
    """Show database size information."""
    print("\nDatabase Size Information")
    print("=" * 80)

    async with engine.begin() as conn:
        # Total database size
        result = await conn.execute(text("""
            SELECT pg_size_pretty(pg_database_size(current_database()))
        """))
        db_size = result.scalar()
        print(f"Total database size: {db_size}")

        # Table sizes
        result = await conn.execute(text("""
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """))

        print("\nTable sizes:")
        print("-" * 80)
        print(f"{'Schema':<15} {'Table':<30} {'Size'}")
        print("-" * 80)
        for schema, table, size in result:
            print(f"{schema:<15} {table:<30} {size}")


def print_menu():
    """Print the main menu."""
    print("\n" + "=" * 80)
    print("DATABASE MANAGEMENT UTILITY")
    print("=" * 80)
    print("\n1. Show all tables")
    print("2. Show table info")
    print("3. Create all tables")
    print("4. Drop all tables")
    print("5. Reset database (drop + create)")
    print("6. Check database health")
    print("7. Show database size")
    print("8. Vacuum database")
    print("9. Exit")
    print("\n" + "=" * 80)


async def main():
    """Main function."""
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-9): ").strip()

        try:
            if choice == '1':
                await show_tables()
            elif choice == '2':
                table_name = input("Enter table name: ").strip()
                await show_table_info(table_name)
            elif choice == '3':
                await create_all_tables()
            elif choice == '4':
                await drop_all_tables()
            elif choice == '5':
                await reset_database()
            elif choice == '6':
                await check_database_health()
            elif choice == '7':
                await show_database_size()
            elif choice == '8':
                await vacuum_database()
            elif choice == '9':
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")

        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
