"""
Diagnostic script to check why match discovery returns no results.
"""
import asyncio
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import date
from app.core.database import AsyncSessionLocal
from app.models.user import User, DatingPreferences
from app.models.match import Match


async def diagnose_match_discovery():
    """Diagnose why match discovery returns no results."""
    print("=" * 80)
    print("MATCH DISCOVERY DIAGNOSTIC")
    print("=" * 80)

    async with AsyncSessionLocal() as db:
        # 1. Check total users
        result = await db.execute(select(func.count(User.id)))
        total_users = result.scalar()
        print(f"\n1. Total users in database: {total_users}")

        if total_users == 0:
            print("   ❌ No users found! Please create some users first.")
            return

        # 2. Check active users
        result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = result.scalar()
        print(f"2. Active users: {active_users}")

        # 3. Check verified users
        result = await db.execute(
            select(func.count(User.id)).where(
                and_(User.is_active == True, User.is_verified == True)
            )
        )
        verified_users = result.scalar()
        print(f"3. Active & verified users: {verified_users}")

        if verified_users < 2:
            print("   WARNING: Need at least 2 active & verified users for matching!")
            print("   Tip: Update users to set is_active=true and is_verified=true")

        # 4. Check users with complete profiles
        result = await db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.is_active == True,
                    User.is_verified == True,
                    User.date_of_birth.isnot(None),
                    User.gender.isnot(None)
                )
            )
        )
        complete_profiles = result.scalar()
        print(f"4. Users with complete profiles: {complete_profiles}")

        # 5. Get a sample user and check their preferences
        result = await db.execute(
            select(User).options(
                selectinload(User.dating_preferences)
            ).where(User.is_active == True).limit(1)
        )
        sample_user = result.scalar_one_or_none()

        if sample_user:
            print(f"\n5. Sample user: {sample_user.email}")
            print(f"   - ID: {sample_user.id}")
            print(f"   - Active: {sample_user.is_active}")
            print(f"   - Verified: {sample_user.is_verified}")
            print(f"   - Gender: {sample_user.gender}")
            print(f"   - Date of birth: {sample_user.date_of_birth}")

            if sample_user.dating_preferences:
                prefs = sample_user.dating_preferences
                print(f"\n   Dating Preferences:")
                print(f"   - Age range: {prefs.age_range_min}-{prefs.age_range_max}")
                print(f"   - Gender preference: {prefs.gender_preference}")
                print(f"   - Max distance: {prefs.max_distance}")

                # Check how many users match these preferences
                query = select(func.count(User.id)).where(
                    and_(
                        User.id != sample_user.id,
                        User.is_active == True,
                        User.is_verified == True
                    )
                )

                # Apply age filter
                if prefs.age_range_min and prefs.age_range_max:
                    today = date.today()
                    min_birth_date = date(today.year - prefs.age_range_max, today.month, today.day)
                    max_birth_date = date(today.year - prefs.age_range_min, today.month, today.day)
                    query = query.where(
                        and_(
                            User.date_of_birth >= min_birth_date,
                            User.date_of_birth <= max_birth_date
                        )
                    )

                # Apply gender filter
                if prefs.gender_preference:
                    query = query.where(User.gender.in_(prefs.gender_preference))

                result = await db.execute(query)
                matching_users = result.scalar()
                print(f"\n   Users matching preferences: {matching_users}")

                if matching_users == 0:
                    print("   PROBLEM: No users match the preferences!")
                    print("   Suggestions:")
                    print("   - Expand age range")
                    print("   - Add more gender preferences")
                    print("   - Create more test users")
            else:
                print("   WARNING: No dating preferences set for this user")

        # 6. Check existing matches
        result = await db.execute(select(func.count(Match.id)))
        total_matches = result.scalar()
        print(f"\n6. Total matches in database: {total_matches}")

        # 7. List all users with their status
        print(f"\n7. All users in database:")
        print("-" * 80)
        result = await db.execute(
            select(User).options(selectinload(User.dating_preferences))
        )
        users = result.scalars().all()

        for i, user in enumerate(users, 1):
            age = None
            if user.date_of_birth:
                today = date.today()
                age = today.year - user.date_of_birth.year

            status_icons = []
            if user.is_active:
                status_icons.append("OK Active")
            else:
                status_icons.append("X Inactive")

            if user.is_verified:
                status_icons.append("OK Verified")
            else:
                status_icons.append("X Unverified")

            print(f"\n{i}. {user.email}")
            print(f"   ID: {user.id}")
            print(f"   Status: {' | '.join(status_icons)}")
            print(f"   Gender: {user.gender or 'Not set'}")
            print(f"   Age: {age or 'Not set'}")
            print(f"   Has preferences: {'Yes' if user.dating_preferences else 'No'}")

        # 8. Provide recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)

        if total_users < 2:
            print("\nPROBLEM: Create at least 2 users for matching to work")
        elif verified_users < 2:
            print("\nPROBLEM: Update users to be active and verified:")
            print("   Run this SQL:")
            print("   UPDATE users SET is_active = true, is_verified = true;")
        elif complete_profiles < 2:
            print("\nPROBLEM: Ensure users have complete profiles:")
            print("   - Set date_of_birth")
            print("   - Set gender")
            print("   - Create dating_preferences")
        else:
            print("\nOK: Database looks good!")
            print("  If still no matches, check:")
            print("  1. Dating preferences are not too restrictive")
            print("  2. Users haven't already matched/passed each other")
            print("  3. API authentication is working correctly")


if __name__ == "__main__":
    asyncio.run(diagnose_match_discovery())
