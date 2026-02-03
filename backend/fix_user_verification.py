"""
Quick fix script to enable matching by verifying all users.
"""
import asyncio
from sqlalchemy import text, update
from app.core.database import AsyncSessionLocal
from app.models.user import User


async def fix_user_verification():
    """Update all users to be verified so matching can work."""
    print("=" * 80)
    print("FIXING USER VERIFICATION STATUS")
    print("=" * 80)

    async with AsyncSessionLocal() as db:
        # Update all users to be verified
        result = await db.execute(
            update(User).values(is_verified=True)
        )

        await db.commit()

        print(f"\nOK: Updated {result.rowcount} users to verified status")
        print("\nNow all users can be discovered in match discovery!")
        print("\nYou can now test the API:")
        print("  GET /api/v1/matches/discover?limit=20&offset=0")


if __name__ == "__main__":
    asyncio.run(fix_user_verification())
