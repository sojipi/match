"""
Direct database query test for Dashboard API
Tests the SQL queries without going through the API
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import select, func, and_, or_
from app.core.database import async_session_maker
from app.models.match import Match, MatchStatus, MatchSession, MatchSessionStatus
from app.models.conversation import ConversationSession
from app.models.user import User


async def test_queries():
    """Test the dashboard queries directly"""
    
    print("=" * 60)
    print("Testing Dashboard Database Queries")
    print("=" * 60)
    
    async with async_session_maker() as db:
        try:
            # Get a test user
            print("\n1. Finding a test user...")
            user_query = select(User).limit(1)
            result = await db.execute(user_query)
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ No users found in database")
                print("Please create a user first")
                return False
            
            user_id = str(user.id)
            print(f"✅ Found user: {user.email} (ID: {user_id})")
            
            # Test 1: Count mutual matches
            print("\n2. Testing mutual matches query...")
            try:
                mutual_matches_query = select(func.count(Match.id)).where(
                    and_(
                        or_(Match.user1_id == user_id, Match.user2_id == user_id),
                        Match.status == MatchStatus.MUTUAL
                    )
                )
                result = await db.execute(mutual_matches_query)
                total_matches = result.scalar() or 0
                print(f"✅ Total mutual matches: {total_matches}")
            except Exception as e:
                print(f"❌ Mutual matches query failed: {e}")
                return False
            
            # Test 2: Count active conversations
            print("\n3. Testing active conversations query...")
            try:
                active_conversations_query = select(func.count(ConversationSession.id)).where(
                    and_(
                        or_(ConversationSession.user1_id == user_id, ConversationSession.user2_id == user_id),
                        ConversationSession.status == "active"
                    )
                )
                result = await db.execute(active_conversations_query)
                active_conversations = result.scalar() or 0
                print(f"✅ Active conversations: {active_conversations}")
            except Exception as e:
                print(f"❌ Active conversations query failed: {e}")
                return False
            
            # Test 3: Count compatibility reports
            print("\n4. Testing compatibility reports query...")
            try:
                compatibility_reports_query = select(func.count()).select_from(
                    select(Match.id).where(
                        and_(
                            or_(Match.user1_id == user_id, Match.user2_id == user_id),
                            Match.compatibility_score.isnot(None)
                        )
                    ).subquery()
                )
                result = await db.execute(compatibility_reports_query)
                compatibility_reports = result.scalar() or 0
                print(f"✅ Compatibility reports: {compatibility_reports}")
            except Exception as e:
                print(f"❌ Compatibility reports query failed: {e}")
                return False
            
            # Test 4: Count AI sessions
            print("\n5. Testing AI sessions query...")
            try:
                ai_sessions_query = select(func.count(MatchSession.id)).where(
                    and_(
                        or_(MatchSession.user1_id == user_id, MatchSession.user2_id == user_id),
                        MatchSession.status == MatchSessionStatus.COMPLETED
                    )
                )
                result = await db.execute(ai_sessions_query)
                ai_sessions = result.scalar() or 0
                print(f"✅ AI sessions: {ai_sessions}")
            except Exception as e:
                print(f"❌ AI sessions query failed: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            # Test 5: Get unread notifications count
            print("\n6. Testing unread notifications query...")
            try:
                from app.models.notification import Notification
                unread_notifications_query = select(func.count(Notification.id)).where(
                    and_(
                        Notification.user_id == user_id,
                        Notification.is_read == False
                    )
                )
                result = await db.execute(unread_notifications_query)
                unread_notifications = result.scalar() or 0
                print(f"✅ Unread notifications: {unread_notifications}")
            except Exception as e:
                print(f"❌ Unread notifications query failed: {e}")
                # This is optional, so don't fail the test
                print("   (This is optional, continuing...)")
            
            print("\n" + "=" * 60)
            print("✅ ALL QUERIES PASSED!")
            print("=" * 60)
            print("\nDashboard Stats Summary:")
            print(f"  - Total Matches: {total_matches}")
            print(f"  - Active Conversations: {active_conversations}")
            print(f"  - Compatibility Reports: {compatibility_reports}")
            print(f"  - AI Sessions: {ai_sessions}")
            print(f"  - Unread Notifications: {unread_notifications if 'unread_notifications' in locals() else 'N/A'}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run the tests"""
    print("\n🚀 Starting Dashboard Query Tests\n")
    
    try:
        result = await test_queries()
        
        if result:
            print("\n🎉 All tests passed! Dashboard queries are working correctly.")
            print("\nYou can now test the API endpoint at:")
            print("  GET http://localhost:8000/api/v1/users/dashboard")
        else:
            print("\n❌ Tests failed! Check the errors above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
