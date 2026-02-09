"""
Seed script to populate scenario templates in the database.
Run from project root with venv activated: python backend/scripts/seed_scenarios.py
Or use: scripts/seed-scenarios.bat
"""
import asyncio
import sys
import os

# Ensure we're running from the correct directory
if not os.path.exists('backend'):
    print("Error: Please run this script from the project root directory")
    print("Usage: python backend/scripts/seed_scenarios.py")
    sys.exit(1)

# Add backend to path
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Import after path is set
from app.core.config import settings
from app.models.scenario import ScenarioTemplate, ScenarioCategory, ScenarioDifficulty


async def seed_scenarios():
    """Seed the database with sample scenario templates."""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    scenarios = [
        {
            "name": "weekend_plans",
            "category": ScenarioCategory.LIFESTYLE,
            "difficulty_level": ScenarioDifficulty.EASY,
            "title": "Weekend Plans Discussion",
            "description": "Discuss and plan how to spend an upcoming weekend together",
            "context": "You both have a free weekend coming up and want to plan something enjoyable together.",
            "setup_prompt": "You have a free weekend ahead. Discuss what you'd like to do together.",
            "estimated_duration_minutes": 10,
            "participant_roles": ["partner_1", "partner_2"],
            "success_criteria": ["reach_agreement", "both_satisfied", "clear_plan"],
            "initial_prompt": "Let's talk about our weekend plans. What would you like to do?",
            "guiding_questions": [
                "What activities do you enjoy on weekends?",
                "Do you prefer staying in or going out?",
                "How do you like to balance relaxation and activities?"
            ],
            "personality_dimensions": ["extraversion", "openness"],
            "value_dimensions": ["leisure", "social_connection"],
            "skill_dimensions": ["communication", "compromise"],
            "tags": ["lifestyle", "planning", "leisure"],
            "keywords": ["weekend", "plans", "activities", "leisure"],
            "is_active": True,
            "is_approved": True
        },
        {
            "name": "budget_discussion",
            "category": ScenarioCategory.FINANCIAL,
            "difficulty_level": ScenarioDifficulty.MODERATE,
            "title": "Monthly Budget Planning",
            "description": "Create a shared monthly budget and discuss financial priorities",
            "context": "You're considering sharing expenses and need to discuss your financial approach.",
            "setup_prompt": "Let's discuss how to manage our finances together and create a budget.",
            "estimated_duration_minutes": 15,
            "participant_roles": ["partner_1", "partner_2"],
            "success_criteria": ["budget_created", "priorities_aligned", "both_comfortable"],
            "initial_prompt": "We should talk about our financial goals and how to budget together.",
            "guiding_questions": [
                "What are your spending priorities?",
                "How do you feel about saving vs. spending?",
                "What financial goals are important to you?"
            ],
            "personality_dimensions": ["conscientiousness", "neuroticism"],
            "value_dimensions": ["security", "freedom", "responsibility"],
            "skill_dimensions": ["planning", "compromise", "transparency"],
            "tags": ["financial", "budget", "planning", "money"],
            "keywords": ["budget", "money", "finances", "spending"],
            "is_active": True,
            "is_approved": True
        },
        {
            "name": "family_visit",
            "category": ScenarioCategory.FAMILY,
            "difficulty_level": ScenarioDifficulty.CHALLENGING,
            "title": "Family Visit Planning",
            "description": "Discuss an upcoming visit from family members and how to handle it",
            "context": "One partner's family wants to visit for a week. Discuss expectations and boundaries.",
            "setup_prompt": "My family wants to visit for a week. Let's talk about how to make this work.",
            "estimated_duration_minutes": 15,
            "participant_roles": ["partner_1", "partner_2"],
            "success_criteria": ["clear_boundaries", "both_comfortable", "plan_agreed"],
            "initial_prompt": "I need to talk about my family's upcoming visit.",
            "guiding_questions": [
                "How do you feel about hosting family?",
                "What boundaries are important to you?",
                "How can we make this comfortable for both of us?"
            ],
            "personality_dimensions": ["agreeableness", "extraversion"],
            "value_dimensions": ["family", "independence", "hospitality"],
            "skill_dimensions": ["boundary_setting", "empathy", "compromise"],
            "tags": ["family", "boundaries", "hosting", "relationships"],
            "keywords": ["family", "visit", "boundaries", "hosting"],
            "is_active": True,
            "is_approved": True
        },
        {
            "name": "career_opportunity",
            "category": ScenarioCategory.CAREER,
            "difficulty_level": ScenarioDifficulty.DIFFICULT,
            "title": "Career Opportunity Decision",
            "description": "One partner has a job offer in another city. Discuss the implications.",
            "context": "A great job opportunity has come up, but it would require relocating to another city.",
            "setup_prompt": "I received a job offer in another city. We need to talk about what this means for us.",
            "estimated_duration_minutes": 20,
            "participant_roles": ["partner_1", "partner_2"],
            "success_criteria": ["all_concerns_heard", "options_explored", "path_forward"],
            "initial_prompt": "I have something important to discuss about my career.",
            "guiding_questions": [
                "What are your career goals?",
                "How do you feel about relocating?",
                "What would this mean for our relationship?"
            ],
            "personality_dimensions": ["openness", "conscientiousness"],
            "value_dimensions": ["career", "stability", "partnership"],
            "skill_dimensions": ["problem_solving", "empathy", "long_term_planning"],
            "tags": ["career", "relocation", "decision", "future"],
            "keywords": ["career", "job", "relocation", "decision"],
            "is_active": True,
            "is_approved": True
        },
        {
            "name": "household_chores",
            "category": ScenarioCategory.DAILY_LIFE,
            "difficulty_level": ScenarioDifficulty.EASY,
            "title": "Household Chores Division",
            "description": "Discuss how to fairly divide household responsibilities",
            "context": "You're moving in together and need to figure out who does what around the house.",
            "setup_prompt": "Let's talk about how to divide household chores fairly.",
            "estimated_duration_minutes": 10,
            "participant_roles": ["partner_1", "partner_2"],
            "success_criteria": ["fair_division", "both_satisfied", "clear_responsibilities"],
            "initial_prompt": "We should figure out how to handle household chores.",
            "guiding_questions": [
                "Which chores do you prefer or dislike?",
                "What does 'fair' mean to you?",
                "How can we make this work for both of us?"
            ],
            "personality_dimensions": ["conscientiousness", "agreeableness"],
            "value_dimensions": ["fairness", "cleanliness", "cooperation"],
            "skill_dimensions": ["negotiation", "compromise", "organization"],
            "tags": ["daily_life", "chores", "household", "fairness"],
            "keywords": ["chores", "household", "cleaning", "responsibilities"],
            "is_active": True,
            "is_approved": True
        },
        {
            "name": "social_event_conflict",
            "category": ScenarioCategory.CONFLICT_RESOLUTION,
            "difficulty_level": ScenarioDifficulty.MODERATE,
            "title": "Conflicting Social Events",
            "description": "You have two important social events on the same day. Decide what to do.",
            "context": "Your friend's wedding and your partner's family reunion are on the same day.",
            "setup_prompt": "We have a scheduling conflict with two important events. Let's figure this out.",
            "estimated_duration_minutes": 12,
            "participant_roles": ["partner_1", "partner_2"],
            "success_criteria": ["solution_found", "both_heard", "relationship_maintained"],
            "initial_prompt": "I need to talk about a scheduling conflict we have.",
            "guiding_questions": [
                "Why is each event important to you?",
                "What options do we have?",
                "How can we honor both commitments?"
            ],
            "personality_dimensions": ["agreeableness", "extraversion"],
            "value_dimensions": ["loyalty", "family", "friendship"],
            "skill_dimensions": ["conflict_resolution", "empathy", "creativity"],
            "tags": ["conflict", "social", "decision", "compromise"],
            "keywords": ["conflict", "events", "scheduling", "compromise"],
            "is_active": True,
            "is_approved": True
        },
        {
            "name": "communication_styles",
            "category": ScenarioCategory.COMMUNICATION,
            "difficulty_level": ScenarioDifficulty.MODERATE,
            "title": "Communication Preferences Discussion",
            "description": "Discuss how you each prefer to communicate and resolve misunderstandings",
            "context": "You've noticed you communicate differently and want to understand each other better.",
            "setup_prompt": "Let's talk about how we communicate and how we can understand each other better.",
            "estimated_duration_minutes": 15,
            "participant_roles": ["partner_1", "partner_2"],
            "success_criteria": ["understanding_reached", "strategies_identified", "both_validated"],
            "initial_prompt": "I think we should talk about our communication styles.",
            "guiding_questions": [
                "How do you prefer to discuss difficult topics?",
                "What makes you feel heard and understood?",
                "How can we communicate more effectively?"
            ],
            "personality_dimensions": ["extraversion", "agreeableness", "neuroticism"],
            "value_dimensions": ["honesty", "respect", "understanding"],
            "skill_dimensions": ["active_listening", "self_awareness", "empathy"],
            "tags": ["communication", "understanding", "relationship", "growth"],
            "keywords": ["communication", "listening", "understanding", "talking"],
            "is_active": True,
            "is_approved": True
        },
        {
            "name": "future_goals",
            "category": ScenarioCategory.FUTURE_PLANNING,
            "difficulty_level": ScenarioDifficulty.CHALLENGING,
            "title": "Five-Year Goals Discussion",
            "description": "Share and discuss your individual and shared goals for the next five years",
            "context": "You want to ensure you're on the same page about your future together.",
            "setup_prompt": "Let's talk about where we see ourselves in five years.",
            "estimated_duration_minutes": 20,
            "participant_roles": ["partner_1", "partner_2"],
            "success_criteria": ["goals_shared", "alignment_assessed", "plan_created"],
            "initial_prompt": "I think it's important we talk about our future goals.",
            "guiding_questions": [
                "What are your personal goals for the next five years?",
                "What do you envision for us as a couple?",
                "How can we support each other's goals?"
            ],
            "personality_dimensions": ["openness", "conscientiousness"],
            "value_dimensions": ["growth", "partnership", "ambition"],
            "skill_dimensions": ["long_term_planning", "compromise", "support"],
            "tags": ["future", "goals", "planning", "vision"],
            "keywords": ["future", "goals", "planning", "vision", "dreams"],
            "is_active": True,
            "is_approved": True
        }
    ]
    
    async with async_session() as session:
        try:
            # Check if scenarios already exist
            result = await session.execute(select(ScenarioTemplate))
            existing = result.scalars().all()
            
            if existing:
                print(f"Found {len(existing)} existing scenarios. Skipping seed.")
                return
            
            # Add scenarios
            for scenario_data in scenarios:
                scenario = ScenarioTemplate(**scenario_data)
                session.add(scenario)
            
            await session.commit()
            print(f"Successfully seeded {len(scenarios)} scenario templates!")
            
        except Exception as e:
            print(f"Error seeding scenarios: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("Seeding scenario templates...")
    asyncio.run(seed_scenarios())
    print("Done!")
