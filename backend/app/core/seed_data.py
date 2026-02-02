"""
Seed data for development environment.
"""
import asyncio
from datetime import datetime, date, timedelta
from typing import List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user import User, PersonalityProfile, DatingPreferences, UserPhoto
from app.models.conversation import Scenario
from app.models.notification import Notification, NotificationType
from app.core.security import get_password_hash


async def create_sample_users(db: AsyncSession) -> List[User]:
    """Create sample users for development."""
    
    sample_users_data = [
        {
            "email": "alice@example.com",
            "username": "alice_wonder",
            "first_name": "Alice",
            "last_name": "Johnson",
            "date_of_birth": date(1995, 3, 15),
            "gender": "female",
            "location": "San Francisco, CA",
            "bio": "Love hiking, reading, and trying new restaurants. Looking for someone who shares my passion for adventure!",
        },
        {
            "email": "bob@example.com",
            "username": "bob_builder",
            "first_name": "Bob",
            "last_name": "Smith",
            "date_of_birth": date(1992, 7, 22),
            "gender": "male",
            "location": "New York, NY",
            "bio": "Software engineer by day, musician by night. Always up for a good conversation about tech or music.",
        },
        {
            "email": "charlie@example.com",
            "username": "charlie_artist",
            "first_name": "Charlie",
            "last_name": "Davis",
            "date_of_birth": date(1988, 11, 8),
            "gender": "non-binary",
            "location": "Austin, TX",
            "bio": "Digital artist and coffee enthusiast. Seeking meaningful connections with creative souls.",
        },
        {
            "email": "diana@example.com",
            "username": "diana_explorer",
            "first_name": "Diana",
            "last_name": "Wilson",
            "date_of_birth": date(1990, 5, 30),
            "gender": "female",
            "location": "Seattle, WA",
            "bio": "Travel blogger and yoga instructor. Love exploring new cultures and mindful living.",
        },
        {
            "email": "ethan@example.com",
            "username": "ethan_chef",
            "first_name": "Ethan",
            "last_name": "Brown",
            "date_of_birth": date(1993, 9, 12),
            "gender": "male",
            "location": "Chicago, IL",
            "bio": "Professional chef with a passion for sustainable cooking. Let's cook something amazing together!",
        }
    ]
    
    users = []
    for user_data in sample_users_data:
        user = User(
            id=uuid.uuid4(),
            password_hash=get_password_hash("password123"),  # Default password for all test users
            is_verified=True,
            is_active=True,
            **user_data
        )
        db.add(user)
        users.append(user)
    
    await db.commit()
    
    # Refresh to get the generated IDs
    for user in users:
        await db.refresh(user)
    
    return users


async def create_personality_profiles(db: AsyncSession, users: List[User]) -> None:
    """Create personality profiles for sample users."""
    
    personality_data = [
        {  # Alice - Extroverted, Open, Adventurous
            "openness": 0.85,
            "conscientiousness": 0.75,
            "extraversion": 0.80,
            "agreeableness": 0.70,
            "neuroticism": 0.30,
            "values": {
                "adventure": 0.9,
                "family": 0.8,
                "creativity": 0.7,
                "stability": 0.6
            },
            "communication_style": "enthusiastic",
            "conflict_resolution_style": "collaborative",
            "completeness_score": 0.95
        },
        {  # Bob - Analytical, Introverted, Reliable
            "openness": 0.70,
            "conscientiousness": 0.90,
            "extraversion": 0.40,
            "agreeableness": 0.75,
            "neuroticism": 0.25,
            "values": {
                "knowledge": 0.9,
                "creativity": 0.8,
                "stability": 0.85,
                "independence": 0.7
            },
            "communication_style": "analytical",
            "conflict_resolution_style": "problem_solving",
            "completeness_score": 0.90
        },
        {  # Charlie - Creative, Open, Empathetic
            "openness": 0.95,
            "conscientiousness": 0.60,
            "extraversion": 0.65,
            "agreeableness": 0.85,
            "neuroticism": 0.40,
            "values": {
                "creativity": 0.95,
                "authenticity": 0.9,
                "compassion": 0.85,
                "freedom": 0.8
            },
            "communication_style": "expressive",
            "conflict_resolution_style": "empathetic",
            "completeness_score": 0.88
        },
        {  # Diana - Balanced, Mindful, Growth-oriented
            "openness": 0.80,
            "conscientiousness": 0.85,
            "extraversion": 0.60,
            "agreeableness": 0.80,
            "neuroticism": 0.20,
            "values": {
                "growth": 0.9,
                "mindfulness": 0.95,
                "adventure": 0.8,
                "balance": 0.85
            },
            "communication_style": "mindful",
            "conflict_resolution_style": "meditative",
            "completeness_score": 0.92
        },
        {  # Ethan - Passionate, Creative, Social
            "openness": 0.75,
            "conscientiousness": 0.80,
            "extraversion": 0.75,
            "agreeableness": 0.70,
            "neuroticism": 0.35,
            "values": {
                "creativity": 0.85,
                "passion": 0.9,
                "community": 0.8,
                "sustainability": 0.85
            },
            "communication_style": "passionate",
            "conflict_resolution_style": "direct",
            "completeness_score": 0.87
        }
    ]
    
    for user, profile_data in zip(users, personality_data):
        profile = PersonalityProfile(
            id=uuid.uuid4(),
            user_id=user.id,
            assessment_version="1.0",
            **profile_data
        )
        db.add(profile)
    
    await db.commit()


async def create_dating_preferences(db: AsyncSession, users: List[User]) -> None:
    """Create dating preferences for sample users."""
    
    preferences_data = [
        {  # Alice
            "age_range_min": 25,
            "age_range_max": 35,
            "max_distance": 50,
            "gender_preference": ["male", "non-binary"],
            "relationship_goals": ["long_term", "marriage"],
            "lifestyle_preferences": {
                "activity_level": "high",
                "social_preference": "extroverted",
                "travel_frequency": "frequent"
            },
            "deal_breakers": ["smoking", "no_pets"],
            "importance_weights": {
                "personality": 0.4,
                "lifestyle": 0.3,
                "values": 0.2,
                "physical": 0.1
            }
        },
        {  # Bob
            "age_range_min": 24,
            "age_range_max": 32,
            "max_distance": 30,
            "gender_preference": ["female"],
            "relationship_goals": ["long_term", "companionship"],
            "lifestyle_preferences": {
                "activity_level": "moderate",
                "social_preference": "introverted",
                "work_life_balance": "important"
            },
            "deal_breakers": ["party_lifestyle", "no_career_goals"],
            "importance_weights": {
                "personality": 0.5,
                "values": 0.3,
                "lifestyle": 0.15,
                "physical": 0.05
            }
        },
        {  # Charlie
            "age_range_min": 26,
            "age_range_max": 40,
            "max_distance": 75,
            "gender_preference": ["female", "male", "non-binary"],
            "relationship_goals": ["companionship", "creative_partnership"],
            "lifestyle_preferences": {
                "creativity": "essential",
                "openness": "very_important",
                "authenticity": "required"
            },
            "deal_breakers": ["closed_minded", "materialistic"],
            "importance_weights": {
                "values": 0.4,
                "personality": 0.35,
                "creativity": 0.2,
                "physical": 0.05
            }
        },
        {  # Diana
            "age_range_min": 28,
            "age_range_max": 38,
            "max_distance": 40,
            "gender_preference": ["male"],
            "relationship_goals": ["long_term", "spiritual_growth"],
            "lifestyle_preferences": {
                "mindfulness": "important",
                "health_conscious": "very_important",
                "travel": "loves"
            },
            "deal_breakers": ["negative_attitude", "unhealthy_habits"],
            "importance_weights": {
                "values": 0.35,
                "personality": 0.3,
                "lifestyle": 0.25,
                "physical": 0.1
            }
        },
        {  # Ethan
            "age_range_min": 25,
            "age_range_max": 35,
            "max_distance": 60,
            "gender_preference": ["female"],
            "relationship_goals": ["long_term", "family"],
            "lifestyle_preferences": {
                "food_lover": "essential",
                "social": "important",
                "sustainability": "values"
            },
            "deal_breakers": ["picky_eater", "wasteful"],
            "importance_weights": {
                "lifestyle": 0.35,
                "personality": 0.3,
                "values": 0.25,
                "physical": 0.1
            }
        }
    ]
    
    for user, pref_data in zip(users, preferences_data):
        preferences = DatingPreferences(
            id=uuid.uuid4(),
            user_id=user.id,
            **pref_data
        )
        db.add(preferences)
    
    await db.commit()


async def create_sample_scenarios(db: AsyncSession) -> None:
    """Create sample relationship scenarios."""
    
    scenarios_data = [
        {
            "title": "Planning a Weekend Getaway",
            "description": "You and your partner need to plan a weekend trip together. You have different preferences for activities and budget.",
            "category": "travel_planning",
            "difficulty_level": 2,
            "expected_duration": 15,
            "cultural_context": "western",
            "context_data": {
                "budget_range": "$200-800",
                "time_available": "2 days",
                "season": "spring",
                "transportation": "car"
            },
            "success_criteria": [
                "Reach agreement on destination",
                "Agree on budget allocation",
                "Plan activities both enjoy",
                "Handle disagreements respectfully"
            ],
            "evaluation_metrics": {
                "collaboration": 0.3,
                "compromise": 0.25,
                "communication": 0.25,
                "creativity": 0.2
            }
        },
        {
            "title": "Discussing Future Career Changes",
            "description": "One partner is considering a major career change that might affect the relationship dynamics and finances.",
            "category": "career_planning",
            "difficulty_level": 4,
            "expected_duration": 20,
            "cultural_context": "western",
            "context_data": {
                "career_change": "corporate_to_freelance",
                "financial_impact": "significant",
                "timeline": "6_months",
                "support_needed": "emotional_financial"
            },
            "success_criteria": [
                "Express concerns openly",
                "Show mutual support",
                "Discuss practical implications",
                "Create action plan together"
            ],
            "evaluation_metrics": {
                "support": 0.35,
                "communication": 0.3,
                "problem_solving": 0.2,
                "empathy": 0.15
            }
        },
        {
            "title": "Meeting Each Other's Families",
            "description": "Planning the first meeting with each other's families during a holiday gathering.",
            "category": "family_integration",
            "difficulty_level": 3,
            "expected_duration": 18,
            "cultural_context": "multicultural",
            "context_data": {
                "occasion": "holiday_dinner",
                "family_size": "large",
                "cultural_differences": "moderate",
                "expectations": "formal_introduction"
            },
            "success_criteria": [
                "Prepare each other for family dynamics",
                "Show respect for family traditions",
                "Handle awkward moments gracefully",
                "Support each other throughout"
            ],
            "evaluation_metrics": {
                "adaptability": 0.3,
                "respect": 0.25,
                "support": 0.25,
                "social_skills": 0.2
            }
        },
        {
            "title": "Handling Financial Disagreement",
            "description": "You disagree about a significant purchase decision and need to find a solution that works for both.",
            "category": "financial_planning",
            "difficulty_level": 3,
            "expected_duration": 12,
            "cultural_context": "western",
            "context_data": {
                "purchase_type": "home_improvement",
                "amount": "$5000",
                "disagreement": "necessity_vs_luxury",
                "budget_impact": "moderate"
            },
            "success_criteria": [
                "Listen to each other's perspectives",
                "Discuss financial priorities",
                "Find compromise solution",
                "Maintain respect during disagreement"
            ],
            "evaluation_metrics": {
                "compromise": 0.35,
                "communication": 0.3,
                "respect": 0.2,
                "problem_solving": 0.15
            }
        },
        {
            "title": "Supporting Through Difficult Times",
            "description": "One partner is going through a challenging period at work and needs emotional support.",
            "category": "emotional_support",
            "difficulty_level": 2,
            "expected_duration": 10,
            "cultural_context": "universal",
            "context_data": {
                "challenge_type": "work_stress",
                "duration": "ongoing",
                "support_needed": "emotional",
                "impact_on_relationship": "moderate"
            },
            "success_criteria": [
                "Provide emotional support",
                "Listen without trying to fix",
                "Offer practical help when appropriate",
                "Maintain relationship balance"
            ],
            "evaluation_metrics": {
                "empathy": 0.4,
                "listening": 0.3,
                "support": 0.2,
                "balance": 0.1
            }
        }
    ]
    
    for scenario_data in scenarios_data:
        scenario = Scenario(
            id=uuid.uuid4(),
            is_active=True,
            usage_count=0,
            **scenario_data
        )
        db.add(scenario)
    
    await db.commit()


async def create_sample_notifications(db: AsyncSession, users: List[User]) -> None:
    """Create sample notifications for users."""
    
    # Create some sample notifications for the first user
    user = users[0]
    
    notifications_data = [
        {
            "type": NotificationType.SYSTEM_ANNOUNCEMENT,
            "title": "Welcome to AI Matchmaker!",
            "message": "Complete your personality assessment to start finding compatible matches.",
            "priority": 2,
            "action_url": "/onboarding/personality"
        },
        {
            "type": NotificationType.NEW_MATCH,
            "title": "New Potential Match!",
            "message": "You have a new potential match with high compatibility. Check it out!",
            "priority": 2,
            "related_user_id": users[1].id,
            "action_url": f"/matches/{users[1].id}"
        }
    ]
    
    for notif_data in notifications_data:
        notification = Notification(
            id=uuid.uuid4(),
            user_id=user.id,
            **notif_data
        )
        db.add(notification)
    
    await db.commit()


async def seed_development_data() -> None:
    """Seed the database with development data."""
    
    async with AsyncSessionLocal() as db:
        try:
            print("Creating sample users...")
            users = await create_sample_users(db)
            
            print("Creating personality profiles...")
            await create_personality_profiles(db, users)
            
            print("Creating dating preferences...")
            await create_dating_preferences(db, users)
            
            print("Creating sample scenarios...")
            await create_sample_scenarios(db)
            
            print("Creating sample notifications...")
            await create_sample_notifications(db, users)
            
            print("✅ Development data seeded successfully!")
            
        except Exception as e:
            print(f"❌ Error seeding data: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_development_data())