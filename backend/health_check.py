#!/usr/bin/env python
"""
Health check script for the AI Matchmaker backend.
Checks all critical services and dependencies.
"""
import asyncio
import sys
from datetime import datetime
import httpx
from sqlalchemy import text
from app.core.database import engine
from app.models.redis_models import redis_client


class HealthChecker:
    """Health check utility class."""

    def __init__(self):
        self.results = []
        self.all_passed = True

    def add_result(self, service: str, status: bool, message: str = ""):
        """Add a health check result."""
        self.results.append({
            "service": service,
            "status": status,
            "message": message
        })
        if not status:
            self.all_passed = False

    async def check_database(self):
        """Check PostgreSQL database connection and health."""
        print("\n[1/5] Checking PostgreSQL Database...")
        try:
            async with engine.begin() as conn:
                # Test connection
                result = await conn.execute(text("SELECT 1"))
                result.scalar()

                # Get version
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()

                # Check table count
                result = await conn.execute(text("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """))
                table_count = result.scalar()

                self.add_result(
                    "PostgreSQL",
                    True,
                    f"Connected | {table_count} tables | {version.split(',')[0]}"
                )
                print(f"  ✓ Database connection: OK")
                print(f"  ✓ Tables found: {table_count}")

        except Exception as e:
            self.add_result("PostgreSQL", False, str(e))
            print(f"  ✗ Database connection: FAILED")
            print(f"    Error: {e}")

    def check_redis(self):
        """Check Redis connection and health."""
        print("\n[2/5] Checking Redis...")
        try:
            # Test ping
            response = redis_client.ping()
            if not response:
                raise Exception("Ping failed")

            # Get info
            info = redis_client.info()
            version = info.get('redis_version', 'unknown')
            memory = info.get('used_memory_human', 'unknown')
            keys_count = sum(
                info.get(f'db{i}', {}).get('keys', 0)
                for i in range(16)
            )

            self.add_result(
                "Redis",
                True,
                f"Connected | {keys_count} keys | v{version} | {memory} used"
            )
            print(f"  ✓ Redis connection: OK")
            print(f"  ✓ Version: {version}")
            print(f"  ✓ Keys: {keys_count}")
            print(f"  ✓ Memory: {memory}")

        except Exception as e:
            self.add_result("Redis", False, str(e))
            print(f"  ✗ Redis connection: FAILED")
            print(f"    Error: {e}")

    async def check_api_server(self, base_url: str = "http://localhost:8000"):
        """Check if the API server is running."""
        print("\n[3/5] Checking API Server...")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check health endpoint
                response = await client.get(f"{base_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    self.add_result(
                        "API Server",
                        True,
                        f"Running | Status: {data.get('status', 'unknown')}"
                    )
                    print(f"  ✓ API server: Running")
                    print(f"  ✓ URL: {base_url}")
                else:
                    raise Exception(f"Status code: {response.status_code}")

        except httpx.ConnectError:
            self.add_result("API Server", False, "Not running or not accessible")
            print(f"  ✗ API server: NOT RUNNING")
            print(f"    Make sure to start the server with: uvicorn main:app --reload")
        except Exception as e:
            self.add_result("API Server", False, str(e))
            print(f"  ✗ API server: FAILED")
            print(f"    Error: {e}")

    async def check_critical_tables(self):
        """Check if all critical database tables exist."""
        print("\n[4/5] Checking Critical Tables...")

        critical_tables = [
            'users',
            'personality_profiles',
            'dating_preferences',
            'notifications',
            'matches',
            'ai_avatars',
            'match_sessions'
        ]

        try:
            async with engine.begin() as conn:
                result = await conn.execute(text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = ANY(:tables)
                """), {"tables": critical_tables})

                existing_tables = {row[0] for row in result}
                missing_tables = set(critical_tables) - existing_tables

                if missing_tables:
                    self.add_result(
                        "Critical Tables",
                        False,
                        f"Missing: {', '.join(missing_tables)}"
                    )
                    print(f"  ✗ Missing tables: {', '.join(missing_tables)}")
                    print(f"    Run: python manage_db.py (option 3) to create tables")
                else:
                    self.add_result(
                        "Critical Tables",
                        True,
                        f"All {len(critical_tables)} tables exist"
                    )
                    print(f"  ✓ All critical tables exist ({len(critical_tables)})")

        except Exception as e:
            self.add_result("Critical Tables", False, str(e))
            print(f"  ✗ Table check: FAILED")
            print(f"    Error: {e}")

    async def check_enum_types(self):
        """Check if all required enum types exist."""
        print("\n[5/5] Checking Enum Types...")

        required_enums = {
            'notificationtype': ['match', 'mutual_match', 'message', 'like',
                               'super_like', 'profile_view', 'compatibility_report', 'system'],
            'notificationchannel': ['in_app', 'email', 'push', 'sms'],
        }

        try:
            async with engine.begin() as conn:
                all_good = True
                for enum_name, expected_values in required_enums.items():
                    result = await conn.execute(text("""
                        SELECT e.enumlabel
                        FROM pg_type t
                        JOIN pg_enum e ON t.oid = e.enumtypid
                        WHERE t.typname = :enum_name
                        ORDER BY e.enumsortorder
                    """), {"enum_name": enum_name})

                    actual_values = [row[0] for row in result]

                    if not actual_values:
                        print(f"  ✗ Enum '{enum_name}': NOT FOUND")
                        all_good = False
                    else:
                        missing = set(expected_values) - set(actual_values)
                        if missing:
                            print(f"  ⚠ Enum '{enum_name}': Missing values: {missing}")
                            all_good = False
                        else:
                            print(f"  ✓ Enum '{enum_name}': OK ({len(actual_values)} values)")

                if all_good:
                    self.add_result("Enum Types", True, "All enum types valid")
                else:
                    self.add_result("Enum Types", False, "Some enum types have issues")

        except Exception as e:
            self.add_result("Enum Types", False, str(e))
            print(f"  ✗ Enum check: FAILED")
            print(f"    Error: {e}")

    def print_summary(self):
        """Print health check summary."""
        print("\n" + "=" * 80)
        print("HEALTH CHECK SUMMARY")
        print("=" * 80)
        print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        for result in self.results:
            status_icon = "✓" if result["status"] else "✗"
            status_text = "PASS" if result["status"] else "FAIL"
            print(f"{status_icon} {result['service']:<20} {status_text:<6} {result['message']}")

        print("\n" + "=" * 80)
        if self.all_passed:
            print("✓ ALL CHECKS PASSED - System is healthy")
            print("=" * 80)
            return 0
        else:
            print("✗ SOME CHECKS FAILED - Please review the errors above")
            print("=" * 80)
            return 1

    async def run_all_checks(self):
        """Run all health checks."""
        print("=" * 80)
        print("AI MATCHMAKER - HEALTH CHECK")
        print("=" * 80)
        print("\nRunning comprehensive health checks...")

        await self.check_database()
        self.check_redis()
        await self.check_api_server()
        await self.check_critical_tables()
        await self.check_enum_types()

        return self.print_summary()


async def main():
    """Main function."""
    checker = HealthChecker()
    exit_code = await checker.run_all_checks()
    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nHealth check cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
