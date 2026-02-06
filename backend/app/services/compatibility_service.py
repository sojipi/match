"""
Compatibility analysis and reporting service.
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import statistics
import json

from app.models.scenario import (
    SimulationSession, ScenarioResult, SimulationMessage,
    ScenarioTemplate, SimulationStatus
)
from app.models.user import User, PersonalityProfile
from app.models.match import Match
from app.core.database import get_db


class CompatibilityService:
    """Service for comprehensive compatibility analysis and reporting."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_compatibility_report(
        self,
        user1_id: str,
        user2_id: str,
        match_id: Optional[str] = None,
        include_trends: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive compatibility report for two users.
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            match_id: Optional match ID for context
            include_trends: Whether to include trend analysis
            
        Returns:
            Comprehensive compatibility report
        """
        # Get user profiles
        users = await self._get_user_profiles(user1_id, user2_id)
        if not users:
            raise ValueError("Users not found")
        
        user1, user2 = users
        
        # Get simulation history
        simulation_history = await self._get_simulation_history(user1_id, user2_id, match_id)
        
        # Calculate compatibility scores
        compatibility_scores = await self._calculate_compatibility_scores(
            user1, user2, simulation_history
        )
        
        # Generate insights and analysis
        insights = await self._generate_compatibility_insights(
            user1, user2, simulation_history, compatibility_scores
        )
        
        # Get trend analysis if requested
        trends = None
        if include_trends and len(simulation_history) > 1:
            trends = await self._analyze_compatibility_trends(simulation_history)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            user1, user2, compatibility_scores, insights, simulation_history
        )
        
        return {
            "report_id": f"compat_{user1_id}_{user2_id}_{int(datetime.utcnow().timestamp())}",
            "generated_at": datetime.utcnow().isoformat(),
            "users": {
                "user1": {
                    "id": str(user1.id),
                    "name": f"{user1.first_name} {user1.last_name[0]}.",
                    "personality_summary": self._summarize_personality(user1.personality_profile)
                },
                "user2": {
                    "id": str(user2.id),
                    "name": f"{user2.first_name} {user2.last_name[0]}.",
                    "personality_summary": self._summarize_personality(user2.personality_profile)
                }
            },
            "compatibility_scores": compatibility_scores,
            "insights": insights,
            "trends": trends,
            "recommendations": recommendations,
            "simulation_summary": {
                "total_sessions": len(simulation_history),
                "total_duration_minutes": sum(
                    (s.duration_seconds or 0) / 60 for s in simulation_history
                ),
                "scenarios_explored": list(set(
                    s.scenario_template.category.value for s in simulation_history
                )),
                "average_engagement": statistics.mean([
                    s.engagement_score for s in simulation_history if s.engagement_score
                ]) if simulation_history else 0.0
            }
        }
    
    async def get_compatibility_dashboard_data(
        self,
        user1_id: str,
        user2_id: str,
        match_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get compatibility dashboard data for interactive display.
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            match_id: Optional match ID
            
        Returns:
            Dashboard data with charts and metrics
        """
        # Get simulation history
        simulation_history = await self._get_simulation_history(user1_id, user2_id, match_id)
        
        if not simulation_history:
            return {
                "has_data": False,
                "message": "No simulation data available yet"
            }
        
        # Calculate dashboard metrics
        dashboard_data = {
            "has_data": True,
            "overview": await self._get_compatibility_overview(simulation_history),
            "dimension_scores": await self._get_dimension_scores(simulation_history),
            "progress_over_time": await self._get_progress_timeline(simulation_history),
            "scenario_performance": await self._get_scenario_performance(simulation_history),
            "communication_patterns": await self._analyze_communication_patterns(simulation_history),
            "key_insights": await self._extract_key_insights(simulation_history),
            "next_steps": await self._suggest_next_steps(simulation_history)
        }
        
        return dashboard_data
    
    async def track_compatibility_trends(
        self,
        user1_id: str,
        user2_id: str,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Track compatibility trends over time.
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            time_period_days: Time period to analyze
            
        Returns:
            Trend analysis data
        """
        cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
        
        # Get recent simulation history
        query = select(SimulationSession).options(
            selectinload(SimulationSession.scenario_template),
            selectinload(SimulationSession.result)
        ).where(
            and_(
                or_(
                    and_(
                        SimulationSession.user1_id == user1_id,
                        SimulationSession.user2_id == user2_id
                    ),
                    and_(
                        SimulationSession.user1_id == user2_id,
                        SimulationSession.user2_id == user1_id
                    )
                ),
                SimulationSession.created_at >= cutoff_date,
                SimulationSession.status == SimulationStatus.COMPLETED
            )
        ).order_by(SimulationSession.created_at)
        
        result = await self.db.execute(query)
        sessions = result.scalars().all()
        
        if len(sessions) < 2:
            return {
                "has_trends": False,
                "message": "Insufficient data for trend analysis"
            }
        
        return await self._analyze_compatibility_trends(sessions)
    
    async def _get_user_profiles(
        self, 
        user1_id: str, 
        user2_id: str
    ) -> Optional[Tuple[User, User]]:
        """Get user profiles with personality data."""
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
            return None
        
        return user1, user2
    
    async def _get_simulation_history(
        self,
        user1_id: str,
        user2_id: str,
        match_id: Optional[str] = None
    ) -> List[SimulationSession]:
        """Get simulation history between two users."""
        query = select(SimulationSession).options(
            selectinload(SimulationSession.scenario_template),
            selectinload(SimulationSession.result),
            selectinload(SimulationSession.messages)
        ).where(
            and_(
                or_(
                    and_(
                        SimulationSession.user1_id == user1_id,
                        SimulationSession.user2_id == user2_id
                    ),
                    and_(
                        SimulationSession.user1_id == user2_id,
                        SimulationSession.user2_id == user1_id
                    )
                ),
                SimulationSession.status == SimulationStatus.COMPLETED
            )
        )
        
        if match_id:
            query = query.where(SimulationSession.match_id == match_id)
        
        query = query.order_by(SimulationSession.created_at)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def _calculate_compatibility_scores(
        self,
        user1: User,
        user2: User,
        simulation_history: List[SimulationSession]
    ) -> Dict[str, float]:
        """Calculate comprehensive compatibility scores."""
        scores = {
            "overall_compatibility": 0.0,
            "personality_compatibility": 0.0,
            "communication_compatibility": 0.0,
            "value_alignment": 0.0,
            "conflict_resolution": 0.0,
            "collaboration_effectiveness": 0.0,
            "emotional_intelligence": 0.0,
            "future_potential": 0.0
        }
        
        if not simulation_history:
            # Calculate basic personality compatibility
            if user1.personality_profile and user2.personality_profile:
                scores["personality_compatibility"] = self._calculate_personality_compatibility(
                    user1.personality_profile, user2.personality_profile
                )
                scores["overall_compatibility"] = scores["personality_compatibility"] * 0.6
            return scores
        
        # Calculate scores based on simulation results
        results = [s.result for s in simulation_history if s.result]
        
        if results:
            scores["communication_compatibility"] = statistics.mean([
                r.communication_score for r in results if r.communication_score
            ])
            scores["value_alignment"] = statistics.mean([
                r.value_alignment_score for r in results if r.value_alignment_score
            ])
            scores["conflict_resolution"] = statistics.mean([
                r.conflict_resolution_score for r in results if r.conflict_resolution_score
            ])
            scores["collaboration_effectiveness"] = statistics.mean([
                r.collaboration_score for r in results if r.collaboration_score
            ])
            scores["emotional_intelligence"] = statistics.mean([
                r.empathy_score for r in results if r.empathy_score
            ])
        
        # Calculate personality compatibility
        if user1.personality_profile and user2.personality_profile:
            scores["personality_compatibility"] = self._calculate_personality_compatibility(
                user1.personality_profile, user2.personality_profile
            )
        
        # Calculate future potential based on trends
        if len(simulation_history) > 1:
            scores["future_potential"] = self._calculate_future_potential(simulation_history)
        
        # Calculate overall compatibility as weighted average
        weights = {
            "personality_compatibility": 0.20,
            "communication_compatibility": 0.25,
            "value_alignment": 0.20,
            "conflict_resolution": 0.15,
            "collaboration_effectiveness": 0.10,
            "emotional_intelligence": 0.10
        }
        
        scores["overall_compatibility"] = sum(
            scores[dimension] * weight 
            for dimension, weight in weights.items()
            if scores[dimension] > 0
        )
        
        return scores
    
    def _calculate_personality_compatibility(
        self,
        profile1: PersonalityProfile,
        profile2: PersonalityProfile
    ) -> float:
        """Calculate personality compatibility score."""
        if not profile1 or not profile2:
            return 0.0
        
        # Big Five compatibility calculation
        big_five_scores = []
        
        traits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        for trait in traits:
            val1 = getattr(profile1, trait, None)
            val2 = getattr(profile2, trait, None)
            
            if val1 is not None and val2 is not None:
                # Some traits benefit from similarity, others from complementarity
                if trait in ['agreeableness', 'conscientiousness']:
                    # Similarity is better
                    score = 1.0 - abs(val1 - val2)
                elif trait == 'neuroticism':
                    # Lower neuroticism is generally better, but some difference is okay
                    avg_neuroticism = (val1 + val2) / 2
                    score = 1.0 - avg_neuroticism * 0.7
                else:
                    # Moderate differences can be complementary
                    diff = abs(val1 - val2)
                    score = 1.0 - (diff * 0.6)  # Reduce penalty for differences
                
                big_five_scores.append(max(0.0, min(1.0, score)))
        
        return statistics.mean(big_five_scores) if big_five_scores else 0.5
    
    def _calculate_future_potential(self, simulation_history: List[SimulationSession]) -> float:
        """Calculate future relationship potential based on trends."""
        if len(simulation_history) < 2:
            return 0.5
        
        # Look at improvement trends
        recent_sessions = simulation_history[-3:]  # Last 3 sessions
        older_sessions = simulation_history[:-3] if len(simulation_history) > 3 else []
        
        if not older_sessions:
            return 0.7  # Default optimistic score for new relationships
        
        # Calculate average scores for recent vs older sessions
        recent_avg = statistics.mean([
            s.collaboration_score for s in recent_sessions 
            if s.collaboration_score
        ]) if recent_sessions else 0.5
        
        older_avg = statistics.mean([
            s.collaboration_score for s in older_sessions 
            if s.collaboration_score
        ]) if older_sessions else 0.5
        
        # Positive trend indicates good future potential
        trend = recent_avg - older_avg
        base_score = (recent_avg + older_avg) / 2
        
        # Boost score if improving, reduce if declining
        future_score = base_score + (trend * 0.5)
        
        return max(0.0, min(1.0, future_score))
    
    async def _generate_compatibility_insights(
        self,
        user1: User,
        user2: User,
        simulation_history: List[SimulationSession],
        compatibility_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate detailed compatibility insights."""
        insights = {
            "strengths": [],
            "challenges": [],
            "opportunities": [],
            "personality_dynamics": {},
            "communication_style": {},
            "conflict_patterns": {},
            "growth_areas": []
        }
        
        # Analyze strengths and challenges
        for dimension, score in compatibility_scores.items():
            if score >= 0.8:
                insights["strengths"].append({
                    "area": dimension.replace('_', ' ').title(),
                    "score": score,
                    "description": self._get_strength_description(dimension, score)
                })
            elif score <= 0.4:
                insights["challenges"].append({
                    "area": dimension.replace('_', ' ').title(),
                    "score": score,
                    "description": self._get_challenge_description(dimension, score)
                })
        
        # Analyze personality dynamics
        if user1.personality_profile and user2.personality_profile:
            insights["personality_dynamics"] = self._analyze_personality_dynamics(
                user1.personality_profile, user2.personality_profile
            )
        
        # Analyze communication patterns from simulations
        if simulation_history:
            insights["communication_style"] = await self._analyze_communication_style(
                simulation_history
            )
        
        # Identify growth opportunities
        insights["opportunities"] = self._identify_growth_opportunities(
            compatibility_scores, simulation_history
        )
        
        return insights
    
    def _get_strength_description(self, dimension: str, score: float) -> str:
        """Get description for compatibility strengths."""
        descriptions = {
            "personality_compatibility": "Your personalities complement each other well, creating a balanced dynamic.",
            "communication_compatibility": "You communicate effectively and understand each other's communication styles.",
            "value_alignment": "You share similar core values and life priorities.",
            "conflict_resolution": "You handle disagreements constructively and find mutually satisfactory solutions.",
            "collaboration_effectiveness": "You work well together and support each other's goals.",
            "emotional_intelligence": "You both demonstrate high emotional awareness and empathy."
        }
        return descriptions.get(dimension, f"Strong compatibility in {dimension.replace('_', ' ')}")
    
    def _get_challenge_description(self, dimension: str, score: float) -> str:
        """Get description for compatibility challenges."""
        descriptions = {
            "personality_compatibility": "Your personality differences may require extra understanding and compromise.",
            "communication_compatibility": "Different communication styles may lead to misunderstandings.",
            "value_alignment": "Some differences in core values may need discussion and mutual respect.",
            "conflict_resolution": "Disagreements may be challenging to resolve without developing better strategies.",
            "collaboration_effectiveness": "Working together toward shared goals may require more coordination.",
            "emotional_intelligence": "Building emotional understanding and empathy could strengthen your connection."
        }
        return descriptions.get(dimension, f"Area for growth in {dimension.replace('_', ' ')}")
    
    def _analyze_personality_dynamics(
        self,
        profile1: PersonalityProfile,
        profile2: PersonalityProfile
    ) -> Dict[str, Any]:
        """Analyze personality dynamics between two users."""
        dynamics = {
            "complementary_traits": [],
            "similar_traits": [],
            "potential_friction": []
        }
        
        traits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        for trait in traits:
            val1 = getattr(profile1, trait, None)
            val2 = getattr(profile2, trait, None)
            
            if val1 is not None and val2 is not None:
                diff = abs(val1 - val2)
                avg = (val1 + val2) / 2
                
                if diff < 0.2:  # Very similar
                    dynamics["similar_traits"].append({
                        "trait": trait.title(),
                        "description": f"Both score similarly on {trait} ({avg:.1f})"
                    })
                elif diff > 0.6:  # Very different
                    if trait in ['extraversion', 'openness']:
                        dynamics["complementary_traits"].append({
                            "trait": trait.title(),
                            "description": f"Complementary {trait} levels may create good balance"
                        })
                    else:
                        dynamics["potential_friction"].append({
                            "trait": trait.title(),
                            "description": f"Significant difference in {trait} may require understanding"
                        })
        
        return dynamics
    
    async def _analyze_communication_style(
        self,
        simulation_history: List[SimulationSession]
    ) -> Dict[str, Any]:
        """Analyze communication style from simulation messages."""
        all_messages = []
        for session in simulation_history:
            all_messages.extend(session.messages)
        
        if not all_messages:
            return {"message": "No communication data available"}
        
        # Analyze message patterns
        user_messages = {}
        for msg in all_messages:
            if msg.sender_type == "user_avatar":
                user_id = msg.sender_id
                if user_id not in user_messages:
                    user_messages[user_id] = []
                user_messages[user_id].append(msg)
        
        patterns = {
            "participation_balance": self._calculate_participation_balance(user_messages),
            "response_patterns": self._analyze_response_patterns(all_messages),
            "communication_quality": self._assess_communication_quality(all_messages)
        }
        
        return patterns
    
    def _calculate_participation_balance(self, user_messages: Dict[str, List]) -> Dict[str, Any]:
        """Calculate how balanced participation is between users."""
        if len(user_messages) != 2:
            return {"balance_score": 0.5, "description": "Unable to assess balance"}
        
        counts = [len(messages) for messages in user_messages.values()]
        total = sum(counts)
        
        if total == 0:
            return {"balance_score": 0.5, "description": "No messages to analyze"}
        
        balance = min(counts) / total
        balance_score = balance * 2  # Scale to 0-1 where 1 is perfect balance
        
        if balance_score >= 0.8:
            description = "Well-balanced participation from both users"
        elif balance_score >= 0.6:
            description = "Mostly balanced with slight differences in participation"
        else:
            description = "Unbalanced participation - one user dominates the conversation"
        
        return {
            "balance_score": balance_score,
            "description": description,
            "message_counts": dict(zip(user_messages.keys(), counts))
        }
    
    def _analyze_response_patterns(self, messages: List[SimulationMessage]) -> Dict[str, Any]:
        """Analyze response patterns and timing."""
        return {
            "average_response_length": statistics.mean([
                len(msg.content) for msg in messages if msg.sender_type == "user_avatar"
            ]) if messages else 0,
            "total_exchanges": len([
                msg for msg in messages if msg.sender_type == "user_avatar"
            ])
        }
    
    def _assess_communication_quality(self, messages: List[SimulationMessage]) -> Dict[str, Any]:
        """Assess overall communication quality."""
        highlighted_messages = [msg for msg in messages if msg.is_highlighted]
        
        return {
            "key_moments": len(highlighted_messages),
            "total_messages": len(messages),
            "quality_score": min(1.0, len(highlighted_messages) / max(1, len(messages)) * 5)
        }
    
    def _identify_growth_opportunities(
        self,
        compatibility_scores: Dict[str, float],
        simulation_history: List[SimulationSession]
    ) -> List[Dict[str, Any]]:
        """Identify specific growth opportunities."""
        opportunities = []
        
        # Find areas with moderate scores that could be improved
        for dimension, score in compatibility_scores.items():
            if 0.4 <= score <= 0.7:  # Moderate scores with improvement potential
                opportunities.append({
                    "area": dimension.replace('_', ' ').title(),
                    "current_score": score,
                    "potential": "High" if score > 0.6 else "Moderate",
                    "description": f"With focused effort, you could significantly improve your {dimension.replace('_', ' ')}"
                })
        
        return opportunities
    
    async def _analyze_compatibility_trends(
        self,
        simulation_history: List[SimulationSession]
    ) -> Dict[str, Any]:
        """Analyze compatibility trends over time."""
        if len(simulation_history) < 2:
            return {"has_trends": False}
        
        # Extract scores over time
        timeline_data = []
        for session in simulation_history:
            if session.result:
                timeline_data.append({
                    "date": session.created_at.isoformat(),
                    "overall_score": session.result.overall_success_score,
                    "collaboration_score": session.result.collaboration_score,
                    "communication_score": session.result.communication_score,
                    "scenario_category": session.scenario_template.category.value
                })
        
        if len(timeline_data) < 2:
            return {"has_trends": False}
        
        # Calculate trends
        overall_scores = [d["overall_score"] for d in timeline_data if d["overall_score"]]
        collaboration_scores = [d["collaboration_score"] for d in timeline_data if d["collaboration_score"]]
        
        trends = {
            "has_trends": True,
            "timeline_data": timeline_data,
            "overall_trend": self._calculate_trend(overall_scores),
            "collaboration_trend": self._calculate_trend(collaboration_scores),
            "improvement_rate": self._calculate_improvement_rate(overall_scores),
            "trend_summary": self._generate_trend_summary(timeline_data)
        }
        
        return trends
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend direction from scores."""
        if len(scores) < 2:
            return "stable"
        
        recent_avg = statistics.mean(scores[-2:])
        earlier_avg = statistics.mean(scores[:-2]) if len(scores) > 2 else scores[0]
        
        diff = recent_avg - earlier_avg
        
        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_improvement_rate(self, scores: List[float]) -> float:
        """Calculate rate of improvement over time."""
        if len(scores) < 2:
            return 0.0
        
        first_score = scores[0]
        last_score = scores[-1]
        
        return (last_score - first_score) / len(scores)
    
    def _generate_trend_summary(self, timeline_data: List[Dict]) -> str:
        """Generate human-readable trend summary."""
        if not timeline_data:
            return "No trend data available"
        
        latest = timeline_data[-1]
        earliest = timeline_data[0]
        
        overall_change = latest["overall_score"] - earliest["overall_score"]
        
        if overall_change > 0.1:
            return f"Compatibility has improved by {overall_change:.1%} over {len(timeline_data)} sessions"
        elif overall_change < -0.1:
            return f"Compatibility has declined by {abs(overall_change):.1%} over {len(timeline_data)} sessions"
        else:
            return f"Compatibility has remained stable over {len(timeline_data)} sessions"
    
    async def _generate_recommendations(
        self,
        user1: User,
        user2: User,
        compatibility_scores: Dict[str, float],
        insights: Dict[str, Any],
        simulation_history: List[SimulationSession]
    ) -> Dict[str, Any]:
        """Generate actionable recommendations."""
        recommendations = {
            "immediate_actions": [],
            "long_term_goals": [],
            "scenario_suggestions": [],
            "skill_development": [],
            "relationship_advice": []
        }
        
        # Generate recommendations based on scores
        for dimension, score in compatibility_scores.items():
            if score < 0.6:  # Areas needing improvement
                recs = self._get_improvement_recommendations(dimension, score)
                recommendations["immediate_actions"].extend(recs.get("immediate", []))
                recommendations["long_term_goals"].extend(recs.get("long_term", []))
        
        # Suggest scenarios based on areas needing work
        weak_areas = [
            dim for dim, score in compatibility_scores.items() 
            if score < 0.7
        ]
        recommendations["scenario_suggestions"] = await self._suggest_scenarios(
            weak_areas, simulation_history
        )
        
        # General relationship advice
        recommendations["relationship_advice"] = self._generate_relationship_advice(
            compatibility_scores, insights
        )
        
        return recommendations
    
    def _get_improvement_recommendations(
        self, 
        dimension: str, 
        score: float
    ) -> Dict[str, List[str]]:
        """Get specific recommendations for improving a compatibility dimension."""
        recommendations = {
            "communication_compatibility": {
                "immediate": [
                    "Practice active listening during conversations",
                    "Ask clarifying questions to ensure understanding",
                    "Share your communication preferences with each other"
                ],
                "long_term": [
                    "Develop a shared communication style",
                    "Learn each other's conflict resolution preferences",
                    "Practice expressing emotions constructively"
                ]
            },
            "value_alignment": {
                "immediate": [
                    "Discuss your core values and priorities",
                    "Find common ground in your belief systems",
                    "Respect differences while seeking understanding"
                ],
                "long_term": [
                    "Explore how your values can complement each other",
                    "Work together on causes you both care about",
                    "Create shared goals that reflect both your values"
                ]
            },
            "conflict_resolution": {
                "immediate": [
                    "Establish ground rules for disagreements",
                    "Practice taking breaks during heated discussions",
                    "Focus on the issue, not personal attacks"
                ],
                "long_term": [
                    "Develop a conflict resolution process that works for both",
                    "Learn to see conflicts as opportunities for growth",
                    "Build skills in compromise and negotiation"
                ]
            }
        }
        
        return recommendations.get(dimension, {
            "immediate": [f"Work on improving {dimension.replace('_', ' ')}"],
            "long_term": [f"Develop long-term strategies for {dimension.replace('_', ' ')}"]
        })
    
    async def _suggest_scenarios(
        self, 
        weak_areas: List[str], 
        simulation_history: List[SimulationSession]
    ) -> List[Dict[str, Any]]:
        """Suggest scenarios based on areas needing improvement."""
        suggestions = []
        
        if "communication_compatibility" in weak_areas:
            suggestions.append({
                "category": "communication",
                "title": "Communication Challenge",
                "reason": "To improve communication patterns and understanding"
            })
        
        if "conflict_resolution" in weak_areas:
            suggestions.append({
                "category": "conflict_resolution",
                "title": "Conflict Resolution Scenario",
                "reason": "To practice handling disagreements constructively"
            })
        
        if "value_alignment" in weak_areas:
            suggestions.append({
                "category": "values",
                "title": "Values Exploration",
                "reason": "To better understand each other's core values"
            })
        
        return suggestions
    
    def _generate_relationship_advice(
        self,
        compatibility_scores: Dict[str, float],
        insights: Dict[str, Any]
    ) -> List[str]:
        """Generate general relationship advice."""
        advice = []
        
        overall_score = compatibility_scores.get("overall_compatibility", 0.5)
        
        if overall_score >= 0.8:
            advice.append("You have strong compatibility! Focus on maintaining open communication and continuing to grow together.")
        elif overall_score >= 0.6:
            advice.append("You have good compatibility with room for growth. Work on the areas where you scored lower.")
        else:
            advice.append("Your compatibility has challenges, but these can be opportunities for growth if you're both committed.")
        
        # Add specific advice based on strengths and challenges
        if len(insights.get("strengths", [])) > len(insights.get("challenges", [])):
            advice.append("Build on your strengths while addressing the challenges together.")
        else:
            advice.append("Focus on turning your challenges into opportunities for deeper understanding.")
        
        advice.append("Remember that compatibility can improve over time with effort and understanding from both partners.")
        
        return advice
    
    def _summarize_personality(self, profile: Optional[PersonalityProfile]) -> Dict[str, Any]:
        """Summarize personality profile for report."""
        if not profile:
            return {"available": False}
        
        return {
            "available": True,
            "big_five": {
                "openness": getattr(profile, 'openness', None),
                "conscientiousness": getattr(profile, 'conscientiousness', None),
                "extraversion": getattr(profile, 'extraversion', None),
                "agreeableness": getattr(profile, 'agreeableness', None),
                "neuroticism": getattr(profile, 'neuroticism', None)
            },
            "dominant_traits": self._get_dominant_traits(profile),
            "communication_style": getattr(profile, 'communication_style', 'Unknown')
        }
    
    def _get_dominant_traits(self, profile: PersonalityProfile) -> List[str]:
        """Get dominant personality traits."""
        traits = {
            'openness': getattr(profile, 'openness', 0),
            'conscientiousness': getattr(profile, 'conscientiousness', 0),
            'extraversion': getattr(profile, 'extraversion', 0),
            'agreeableness': getattr(profile, 'agreeableness', 0),
            'neuroticism': getattr(profile, 'neuroticism', 0)
        }
        
        # Return traits that are above 0.7
        return [trait for trait, value in traits.items() if value > 0.7]
    
    # Dashboard helper methods
    async def _get_compatibility_overview(self, simulation_history: List[SimulationSession]) -> Dict[str, Any]:
        """Get compatibility overview for dashboard."""
        if not simulation_history:
            return {}
        
        latest_session = simulation_history[-1]
        if not latest_session.result:
            return {}
        
        return {
            "overall_score": latest_session.result.overall_success_score,
            "trend": self._calculate_trend([
                s.result.overall_success_score for s in simulation_history[-3:] 
                if s.result and s.result.overall_success_score
            ]),
            "sessions_completed": len(simulation_history),
            "last_session_date": latest_session.created_at.isoformat()
        }
    
    async def _get_dimension_scores(self, simulation_history: List[SimulationSession]) -> Dict[str, float]:
        """Get latest dimension scores for dashboard."""
        if not simulation_history or not simulation_history[-1].result:
            return {}
        
        result = simulation_history[-1].result
        return {
            "collaboration": result.collaboration_score or 0,
            "communication": result.communication_score or 0,
            "conflict_resolution": result.conflict_resolution_score or 0,
            "value_alignment": result.value_alignment_score or 0,
            "empathy": result.empathy_score or 0,
            "problem_solving": result.problem_solving_score or 0
        }
    
    async def _get_progress_timeline(self, simulation_history: List[SimulationSession]) -> List[Dict[str, Any]]:
        """Get progress timeline for dashboard charts."""
        timeline = []
        for session in simulation_history:
            if session.result:
                timeline.append({
                    "date": session.created_at.isoformat(),
                    "overall_score": session.result.overall_success_score,
                    "collaboration_score": session.result.collaboration_score,
                    "communication_score": session.result.communication_score,
                    "scenario": session.scenario_template.title
                })
        return timeline
    
    async def _get_scenario_performance(self, simulation_history: List[SimulationSession]) -> Dict[str, Any]:
        """Get scenario performance breakdown."""
        performance = {}
        for session in simulation_history:
            category = session.scenario_template.category.value
            if category not in performance:
                performance[category] = {
                    "sessions": 0,
                    "average_score": 0,
                    "scores": []
                }
            
            performance[category]["sessions"] += 1
            if session.result and session.result.overall_success_score:
                performance[category]["scores"].append(session.result.overall_success_score)
        
        # Calculate averages
        for category, data in performance.items():
            if data["scores"]:
                data["average_score"] = statistics.mean(data["scores"])
        
        return performance
    
    async def _extract_key_insights(self, simulation_history: List[SimulationSession]) -> List[str]:
        """Extract key insights from simulation history."""
        insights = []
        
        if not simulation_history:
            return insights
        
        # Analyze improvement trends
        if len(simulation_history) >= 2:
            first_score = simulation_history[0].result.overall_success_score if simulation_history[0].result else 0
            last_score = simulation_history[-1].result.overall_success_score if simulation_history[-1].result else 0
            
            if last_score > first_score + 0.1:
                insights.append("Your compatibility has improved significantly over time")
            elif last_score < first_score - 0.1:
                insights.append("Recent sessions show some challenges - consider focusing on communication")
        
        # Analyze scenario performance
        categories_tried = set(s.scenario_template.category.value for s in simulation_history)
        if len(categories_tried) >= 3:
            insights.append(f"You've explored {len(categories_tried)} different scenario types")
        
        # Analyze engagement
        avg_engagement = statistics.mean([
            s.engagement_score for s in simulation_history if s.engagement_score
        ])
        if avg_engagement > 0.8:
            insights.append("You both show high engagement in scenarios")
        
        return insights
    
    async def _suggest_next_steps(self, simulation_history: List[SimulationSession]) -> List[Dict[str, str]]:
        """Suggest next steps based on simulation history."""
        suggestions = []
        
        # Analyze what scenarios haven't been tried
        tried_categories = set(s.scenario_template.category.value for s in simulation_history)
        all_categories = [
            "financial", "family", "lifestyle", "career", "social", 
            "conflict_resolution", "values", "communication", "future_planning", "daily_life"
        ]
        
        untried_categories = set(all_categories) - tried_categories
        
        if untried_categories:
            suggestions.append({
                "type": "scenario",
                "title": f"Try {list(untried_categories)[0]} scenarios",
                "description": "Explore new areas of compatibility"
            })
        
        # Suggest based on performance
        if simulation_history:
            latest_result = simulation_history[-1].result
            if latest_result:
                if latest_result.conflict_resolution_score and latest_result.conflict_resolution_score < 0.6:
                    suggestions.append({
                        "type": "improvement",
                        "title": "Focus on conflict resolution",
                        "description": "Practice handling disagreements more effectively"
                    })
                
                if latest_result.communication_score and latest_result.communication_score < 0.6:
                    suggestions.append({
                        "type": "improvement",
                        "title": "Improve communication",
                        "description": "Work on understanding each other's communication styles"
                    })
        
        return suggestions