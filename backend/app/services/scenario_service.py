"""
Scenario management and simulation service.
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import random
import json

from app.models.scenario import (
    ScenarioTemplate, SimulationSession, SimulationMessage, ScenarioResult,
    ScenarioLibrary, ScenarioCategory, ScenarioDifficulty, SimulationStatus
)
from app.models.user import User, PersonalityProfile
from app.models.match import Match
from app.core.database import get_db


class ScenarioService:
    """Service for scenario management and simulation orchestration."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_scenario_library(
        self,
        category: Optional[str] = None,
        difficulty: Optional[int] = None,
        cultural_context: Optional[str] = None,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Get available scenarios from the library.
        
        Args:
            category: Filter by scenario category
            difficulty: Filter by difficulty level (1-5)
            cultural_context: Cultural adaptation context
            language: Language preference
            
        Returns:
            List of scenario templates
        """
        query = select(ScenarioTemplate).where(
            and_(
                ScenarioTemplate.is_active == True,
                ScenarioTemplate.is_approved == True
            )
        )
        
        # Apply filters
        if category:
            try:
                category_enum = ScenarioCategory(category)
                query = query.where(ScenarioTemplate.category == category_enum)
            except ValueError:
                pass  # Invalid category, ignore filter
        
        if difficulty:
            try:
                difficulty_enum = ScenarioDifficulty(difficulty)
                query = query.where(ScenarioTemplate.difficulty_level == difficulty_enum)
            except ValueError:
                pass  # Invalid difficulty, ignore filter
        
        # Order by usage and rating
        query = query.order_by(
            ScenarioTemplate.user_rating.desc(),
            ScenarioTemplate.usage_count.desc()
        )
        
        result = await self.db.execute(query)
        scenarios = result.scalars().all()
        
        # Format response
        scenario_list = []
        for scenario in scenarios:
            # Get cultural adaptation if available
            adapted_content = self._get_cultural_adaptation(
                scenario, cultural_context, language
            )
            
            scenario_data = {
                "id": str(scenario.id),
                "name": scenario.name,
                "title": adapted_content.get("title", scenario.title),
                "description": adapted_content.get("description", scenario.description),
                "category": scenario.category.value,
                "difficulty_level": scenario.difficulty_level.value,
                "estimated_duration_minutes": scenario.estimated_duration_minutes,
                "personality_dimensions": scenario.personality_dimensions,
                "value_dimensions": scenario.value_dimensions,
                "tags": scenario.tags,
                "user_rating": scenario.user_rating,
                "usage_count": scenario.usage_count,
                "success_rate": scenario.success_rate,
                "content_warnings": scenario.content_warnings
            }
            scenario_list.append(scenario_data)
        
        return scenario_list
    
    async def get_recommended_scenarios(
        self,
        user1_id: str,
        user2_id: str,
        match_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recommended scenarios based on user personalities and match history.
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            match_id: Optional match ID for context
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended scenarios
        """
        # Get user personality profiles
        user1_query = select(User).options(
            selectinload(User.personality_profile)
        ).where(User.id == user1_id)
        
        user2_query = select(User).options(
            selectinload(User.personality_profile)
        ).where(User.id == user2_id)
        
        user1_result = await self.db.execute(user1_query)
        user2_result = await self.db.execute(user2_query)
        
        user1 = user1_result.scalar_one_or_none()
        user2 = user2_result.scalar_one_or_none()
        
        if not user1 or not user2:
            # Fall back to general recommendations
            return await self.get_scenario_library(limit=limit)
        
        # Get previous simulation history
        previous_scenarios = []
        if match_id:
            previous_query = select(SimulationSession.scenario_template_id).where(
                SimulationSession.match_id == match_id
            )
            previous_result = await self.db.execute(previous_query)
            previous_scenarios = [str(row[0]) for row in previous_result.fetchall()]
        
        # Analyze personalities for recommendations
        recommendations = await self._analyze_personality_for_scenarios(
            user1, user2, previous_scenarios, limit
        )
        
        return recommendations
    
    async def create_simulation_session(
        self,
        user1_id: str,
        user2_id: str,
        scenario_id: str,
        match_id: Optional[str] = None,
        cultural_context: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Create a new simulation session.
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            scenario_id: Scenario template ID
            match_id: Optional match ID
            cultural_context: Cultural adaptation context
            language: Language preference
            
        Returns:
            Created simulation session data
        """
        # Get scenario template
        scenario_query = select(ScenarioTemplate).where(
            ScenarioTemplate.id == scenario_id
        )
        scenario_result = await self.db.execute(scenario_query)
        scenario = scenario_result.scalar_one_or_none()
        
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        # Get cultural adaptation
        adapted_content = self._get_cultural_adaptation(
            scenario, cultural_context, language
        )
        
        # Create simulation session
        session = SimulationSession(
            user1_id=user1_id,
            user2_id=user2_id,
            match_id=match_id,
            scenario_template_id=scenario_id,
            scenario_instance_data=adapted_content,
            session_title=adapted_content.get("title", scenario.title),
            session_description=adapted_content.get("description", scenario.description),
            cultural_adaptation=cultural_context,
            language=language,
            max_duration_minutes=scenario.estimated_duration_minutes,
            current_phase="setup"
        )
        
        self.db.add(session)
        await self.db.flush()  # Get the ID
        
        # Update scenario usage count
        scenario.usage_count += 1
        
        await self.db.commit()
        
        return {
            "session_id": str(session.id),
            "scenario": {
                "id": str(scenario.id),
                "name": scenario.name,
                "title": session.session_title,
                "description": session.session_description,
                "category": scenario.category.value,
                "difficulty_level": scenario.difficulty_level.value,
                "estimated_duration_minutes": scenario.estimated_duration_minutes
            },
            "status": session.status.value,
            "created_at": session.created_at.isoformat()
        }
    
    async def start_simulation(self, session_id: str) -> Dict[str, Any]:
        """
        Start a simulation session.
        
        Args:
            session_id: Simulation session ID
            
        Returns:
            Updated session data with initial scenario presentation
        """
        # Get session with scenario
        session_query = select(SimulationSession).options(
            selectinload(SimulationSession.scenario_template)
        ).where(SimulationSession.id == session_id)
        
        session_result = await self.db.execute(session_query)
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise ValueError(f"Simulation session {session_id} not found")
        
        if session.status != SimulationStatus.SCHEDULED:
            raise ValueError(f"Session {session_id} cannot be started (status: {session.status.value})")
        
        # Update session status
        session.status = SimulationStatus.ACTIVE
        session.started_at = datetime.utcnow()
        session.current_phase = "scenario_presentation"
        session.phase_start_time = datetime.utcnow()
        
        # Create initial scenario presentation message
        scenario_data = session.scenario_instance_data or {}
        initial_prompt = scenario_data.get("setup_prompt", session.scenario_template.setup_prompt)
        
        initial_message = SimulationMessage(
            session_id=session.id,
            sender_id="scenario_agent",
            sender_type="scenario_agent",
            sender_name="Scenario Guide",
            content=initial_prompt,
            message_type="system",
            scenario_phase="scenario_presentation",
            turn_number=0
        )
        
        self.db.add(initial_message)
        await self.db.commit()
        
        return {
            "session_id": str(session.id),
            "status": session.status.value,
            "current_phase": session.current_phase,
            "initial_message": {
                "content": initial_prompt,
                "sender_name": "Scenario Guide",
                "message_type": "system"
            },
            "started_at": session.started_at.isoformat()
        }
    
    async def get_simulation_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get simulation session details.
        
        Args:
            session_id: Simulation session ID
            
        Returns:
            Session data or None if not found
        """
        session_query = select(SimulationSession).options(
            selectinload(SimulationSession.scenario_template),
            selectinload(SimulationSession.user1),
            selectinload(SimulationSession.user2),
            selectinload(SimulationSession.messages)
        ).where(SimulationSession.id == session_id)
        
        session_result = await self.db.execute(session_query)
        session = session_result.scalar_one_or_none()
        
        if not session:
            return None
        
        return {
            "session_id": str(session.id),
            "match_id": str(session.match_id) if session.match_id else None,
            "scenario": {
                "id": str(session.scenario_template.id),
                "name": session.scenario_template.name,
                "title": session.session_title,
                "description": session.session_description,
                "category": session.scenario_template.category.value,
                "difficulty_level": session.scenario_template.difficulty_level.value
            },
            "participants": [
                {
                    "user_id": str(session.user1.id),
                    "name": f"{session.user1.first_name} {session.user1.last_name[0]}."
                },
                {
                    "user_id": str(session.user2.id),
                    "name": f"{session.user2.first_name} {session.user2.last_name[0]}."
                }
            ],
            "status": session.status.value,
            "current_phase": session.current_phase,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "duration_seconds": session.duration_seconds,
            "message_count": session.message_count,
            "engagement_score": session.engagement_score,
            "scenario_completion_score": session.scenario_completion_score,
            "collaboration_score": session.collaboration_score,
            "messages": [
                {
                    "message_id": str(msg.id),
                    "sender_name": msg.sender_name,
                    "sender_type": msg.sender_type,
                    "content": msg.content,
                    "message_type": msg.message_type,
                    "scenario_phase": msg.scenario_phase,
                    "timestamp": msg.timestamp.isoformat(),
                    "is_highlighted": msg.is_highlighted
                }
                for msg in session.messages
            ]
        }
    
    async def add_simulation_message(
        self,
        session_id: str,
        sender_id: str,
        sender_type: str,
        sender_name: str,
        content: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Add a message to a simulation session.
        
        Args:
            session_id: Simulation session ID
            sender_id: ID of the sender
            sender_type: Type of sender (user_avatar, scenario_agent, system)
            sender_name: Display name of sender
            content: Message content
            message_type: Type of message
            
        Returns:
            Created message data
        """
        # Get session
        session_query = select(SimulationSession).where(
            SimulationSession.id == session_id
        )
        session_result = await self.db.execute(session_query)
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise ValueError(f"Simulation session {session_id} not found")
        
        # Create message
        message = SimulationMessage(
            session_id=session.id,
            sender_id=sender_id,
            sender_type=sender_type,
            sender_name=sender_name,
            content=content,
            message_type=message_type,
            scenario_phase=session.current_phase,
            turn_number=session.turn_count + 1
        )
        
        self.db.add(message)
        
        # Update session counters
        session.message_count += 1
        session.turn_count += 1
        session.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        return {
            "message_id": str(message.id),
            "sender_name": message.sender_name,
            "sender_type": message.sender_type,
            "content": message.content,
            "message_type": message.message_type,
            "scenario_phase": message.scenario_phase,
            "turn_number": message.turn_number,
            "timestamp": message.timestamp.isoformat()
        }
    
    async def complete_simulation(self, session_id: str) -> Dict[str, Any]:
        """
        Complete a simulation session and generate results.
        
        Args:
            session_id: Simulation session ID
            
        Returns:
            Completion data with results
        """
        # Get session with messages
        session_query = select(SimulationSession).options(
            selectinload(SimulationSession.scenario_template),
            selectinload(SimulationSession.messages)
        ).where(SimulationSession.id == session_id)
        
        session_result = await self.db.execute(session_query)
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise ValueError(f"Simulation session {session_id} not found")
        
        # Update session status
        session.status = SimulationStatus.COMPLETED
        session.ended_at = datetime.utcnow()
        session.duration_seconds = int((session.ended_at - session.started_at).total_seconds()) if session.started_at else 0
        session.current_phase = "completed"
        
        # Generate scenario results
        results = await self._generate_scenario_results(session)
        
        # Create scenario result record
        scenario_result = ScenarioResult(
            simulation_session_id=session.id,
            scenario_template_id=session.scenario_template_id,
            overall_success_score=results["overall_success_score"],
            scenario_completion_rate=results["scenario_completion_rate"],
            collaboration_score=results["collaboration_score"],
            communication_score=results["communication_score"],
            conflict_resolution_score=results["conflict_resolution_score"],
            value_alignment_score=results["value_alignment_score"],
            problem_solving_score=results["problem_solving_score"],
            empathy_score=results["empathy_score"],
            scenario_objectives_met=results["scenario_objectives_met"],
            key_decisions_made=results["key_decisions_made"],
            conflict_points=results["conflict_points"],
            resolution_strategies=results["resolution_strategies"],
            strengths_identified=results["strengths_identified"],
            challenges_identified=results["challenges_identified"],
            compatibility_insights=results["compatibility_insights"],
            behavioral_patterns=results["behavioral_patterns"],
            relationship_recommendations=results["relationship_recommendations"],
            future_scenario_suggestions=results["future_scenario_suggestions"],
            skill_development_areas=results["skill_development_areas"]
        )
        
        self.db.add(scenario_result)
        
        # Update scenario template success rate
        await self._update_scenario_success_rate(session.scenario_template_id)
        
        await self.db.commit()
        
        return {
            "session_id": str(session.id),
            "status": session.status.value,
            "duration_seconds": session.duration_seconds,
            "results": results,
            "completed_at": session.ended_at.isoformat()
        }
    
    def _get_cultural_adaptation(
        self,
        scenario: ScenarioTemplate,
        cultural_context: Optional[str],
        language: str
    ) -> Dict[str, Any]:
        """Get culturally adapted scenario content."""
        adapted_content = {}
        
        # Start with base content
        adapted_content["title"] = scenario.title
        adapted_content["description"] = scenario.description
        adapted_content["setup_prompt"] = scenario.setup_prompt
        adapted_content["initial_prompt"] = scenario.initial_prompt
        adapted_content["guiding_questions"] = scenario.guiding_questions
        
        # Apply cultural adaptations if available
        if cultural_context and scenario.cultural_adaptations:
            cultural_data = scenario.cultural_adaptations.get(cultural_context, {})
            adapted_content.update(cultural_data)
        
        # Apply language variants if available
        if language != "en" and scenario.language_variants:
            language_data = scenario.language_variants.get(language, {})
            adapted_content.update(language_data)
        
        return adapted_content
    
    async def _analyze_personality_for_scenarios(
        self,
        user1: User,
        user2: User,
        previous_scenarios: List[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Analyze user personalities to recommend appropriate scenarios."""
        # Get all available scenarios
        scenarios_query = select(ScenarioTemplate).where(
            and_(
                ScenarioTemplate.is_active == True,
                ScenarioTemplate.is_approved == True,
                ~ScenarioTemplate.id.in_(previous_scenarios) if previous_scenarios else True
            )
        )
        
        scenarios_result = await self.db.execute(scenarios_query)
        scenarios = scenarios_result.scalars().all()
        
        # Score scenarios based on personality compatibility
        scored_scenarios = []
        
        for scenario in scenarios:
            score = self._calculate_scenario_personality_match(
                user1.personality_profile,
                user2.personality_profile,
                scenario
            )
            
            scored_scenarios.append((scenario, score))
        
        # Sort by score and return top recommendations
        scored_scenarios.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for scenario, score in scored_scenarios[:limit]:
            recommendations.append({
                "id": str(scenario.id),
                "name": scenario.name,
                "title": scenario.title,
                "description": scenario.description,
                "category": scenario.category.value,
                "difficulty_level": scenario.difficulty_level.value,
                "estimated_duration_minutes": scenario.estimated_duration_minutes,
                "personality_match_score": score,
                "tags": scenario.tags,
                "user_rating": scenario.user_rating
            })
        
        return recommendations
    
    def _calculate_scenario_personality_match(
        self,
        profile1: Optional[PersonalityProfile],
        profile2: Optional[PersonalityProfile],
        scenario: ScenarioTemplate
    ) -> float:
        """Calculate how well a scenario matches user personalities."""
        if not profile1 or not profile2:
            return 0.5  # Default neutral score
        
        score = 0.0
        factors = 0
        
        # Check personality dimensions the scenario tests
        if scenario.personality_dimensions:
            for dimension in scenario.personality_dimensions:
                if dimension in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
                    trait1 = getattr(profile1, dimension, None)
                    trait2 = getattr(profile2, dimension, None)
                    
                    if trait1 is not None and trait2 is not None:
                        # Some scenarios benefit from similar traits, others from complementary
                        if dimension in ["agreeableness", "conscientiousness"]:
                            # Similar is better for these
                            score += 1 - abs(trait1 - trait2)
                        else:
                            # Some difference can be interesting
                            diff = abs(trait1 - trait2)
                            score += 1 - (diff * 0.7)  # Reduce penalty for differences
                        factors += 1
        
        # Base score on scenario difficulty vs user experience
        # This is simplified - in production, track user experience levels
        difficulty_score = 0.7  # Assume moderate difficulty is good for most users
        score += difficulty_score
        factors += 1
        
        # Add some randomness to avoid always recommending the same scenarios
        score += random.uniform(0, 0.2)
        
        return score / factors if factors > 0 else 0.5
    
    async def _generate_scenario_results(self, session: SimulationSession) -> Dict[str, Any]:
        """Generate comprehensive results from a completed simulation."""
        # This is a simplified version - in production, use AI analysis
        # of the conversation messages to generate detailed insights
        
        message_count = len(session.messages)
        duration_minutes = session.duration_seconds / 60 if session.duration_seconds else 0
        
        # Calculate basic scores based on participation and engagement
        completion_rate = min(1.0, duration_minutes / session.scenario_template.estimated_duration_minutes)
        participation_balance = self._calculate_participation_balance(session.messages)
        
        return {
            "overall_success_score": 0.75,  # Placeholder
            "scenario_completion_rate": completion_rate,
            "collaboration_score": participation_balance,
            "communication_score": 0.8,  # Placeholder
            "conflict_resolution_score": 0.7,  # Placeholder
            "value_alignment_score": 0.75,  # Placeholder
            "problem_solving_score": 0.8,  # Placeholder
            "empathy_score": 0.85,  # Placeholder
            "scenario_objectives_met": ["objective_1", "objective_2"],
            "key_decisions_made": ["decision_1", "decision_2"],
            "conflict_points": ["conflict_1"],
            "resolution_strategies": ["strategy_1"],
            "strengths_identified": ["good_communication", "mutual_respect"],
            "challenges_identified": ["different_priorities"],
            "compatibility_insights": ["shared_values", "complementary_skills"],
            "behavioral_patterns": ["collaborative_approach"],
            "relationship_recommendations": ["continue_exploring_shared_interests"],
            "future_scenario_suggestions": ["financial_planning", "family_discussion"],
            "skill_development_areas": ["active_listening"]
        }
    
    def _calculate_participation_balance(self, messages: List[SimulationMessage]) -> float:
        """Calculate how balanced the participation was between users."""
        if not messages:
            return 0.0
        
        user_messages = {}
        for message in messages:
            if message.sender_type == "user_avatar":
                user_messages[message.sender_id] = user_messages.get(message.sender_id, 0) + 1
        
        if len(user_messages) < 2:
            return 0.5  # Only one participant
        
        counts = list(user_messages.values())
        total = sum(counts)
        if total == 0:
            return 0.0
        
        # Calculate balance (closer to 0.5/0.5 split is better)
        balance = min(counts) / total
        return balance * 2  # Scale to 0-1 where 1 is perfect balance
    
    async def _update_scenario_success_rate(self, scenario_id: str):
        """Update scenario success rate based on completion data."""
        # This would calculate success rate based on user feedback and completion rates
        # For now, just increment usage count
        scenario_query = select(ScenarioTemplate).where(
            ScenarioTemplate.id == scenario_id
        )
        scenario_result = await self.db.execute(scenario_query)
        scenario = scenario_result.scalar_one_or_none()
        
        if scenario:
            # Placeholder success rate calculation
            scenario.success_rate = min(1.0, scenario.success_rate + 0.01)