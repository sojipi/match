"""
Check and fix user status for match discovery.
"""
import asyncio
from sqlalchemy import select, update, text
from app.core.database import async_session_maker
from app.models.user import User

async def check_and_fix_users():
    async with async_session_maker() as db:
        print("=== Checking User Status ===\n")

        # Count total users
        result = await db.execute(select(User))
        all_users = result.scalars().all()
        print(f"Total users: {len(all_users)}")

        # Count active users
        active_count = sum(1 for u in all_users if u.is_active)
        print(f"Active users: {active_count}")

        # Count verified users
        verified_count = sum(1 for u in all_users if u.is_verified)
        print(f"Verified users: {verified_count}")

        # Count users eligible for matching
        eligible = [u for u in all_users if u.is_active and u.is_verified]
        print(f"Eligible for matching (active + verified): {len(eligible)}")

        # Count users with date_of_birth
        with_dob = sum(1 for u in all_users if u.date_of_birth)
        print(f"Users with date_of_birth: {with_dob}")

        print("\n=== User Details ===")
        for user in all_users[:10]:  # Show first 10
            print(f"\nEmail: {user.email}")
            print(f"  Name: {user.first_name} {user.last_name}")
            print(f"  Active: {user.is_active}")
            print(f"  Verified: {user.is_verified}")
            print(f"  Date of Birth: {user.date_of_birth}")
            print(f"  Gender: {user.gender}")

        # Ask to fix
        print("\n=== Fix Options ===")
        print("Would you like to:")
        print("1. Set all users to active=True and verified=True")
        print("2. Just show the SQL to run manually")
        print("3. Exit")

        # For now, just show the SQL
        print("\n=== SQL to Fix Users ===")
        print("Run this SQL to make all users eligible for matching:")
        print("\nUPDATE users SET is_active = true, is_verified = true;")
        print("\n=== Check Dating Preferences ===")

        # Check dating preferences
        result = await db.execute(text("SELECT COUNT(*) FROM dating_preferences"))
        prefs_count = result.scalar()
        print(f"Users with dating preferences: {prefs_count}")

        if prefs_count == 0:
            print("\nNo dating preferences found. Users might need to set preferences.")
            print("SQL to create default preferences for all users:")
            print("""
INSERT INTO dating_preferences (id, user_id, age_range_min, age_range_max, gender_preference)
SELECT gen_random_uuid(), id, 18, 50, ARRAY['male', 'female', 'other']::VARCHAR[]
FROM users
WHERE id NOT IN (SELECT user_id FROM dating_preferences);
""")

if __name__ == "__main__":
    asyncio.run(check_and_fix_users())
