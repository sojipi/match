"""
AI Avatar service for creating and managing user avatars.
"""
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
import json
import uuid

from app.models.user import User, PersonalityProfile
from app.models.avatar import AIAvatar, AvatarCustomization, AvatarTrainingSession, AvatarStatus
from app.core.config import settings


class AvatarService:
    """Service for AI avatar creation and management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_avatar_from_personality(
        self, 
        user_id: str, 
        personality_profile_id: str
    ) -> AIAvatar:
        """Create an AI avatar from a user's personality profile."""
        
        # Get user and personality profile
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        profile_result = await self.db.execute(
            select(PersonalityProfile).where(PersonalityProfile.id == personality_profile_id)
        )
        personality_profile = profile_result.scalar_one_or_none()
        if not personality_profile:
            raise ValueError("Personality profile not found")
        
        # Check if avatar already exists
        existing_result = await self.db.execute(
            select(AIAvatar).where(AIAvatar.user_id == user_id)
        )
        existing_avatar = existing_result.scalar_one_or_none()
        if existing_avatar:
            # Update existing avatar instead of creating new one
            return await self.update_avatar_from_personality(existing_avatar.id, personality_profile_id)
        
        # Generate avatar configuration from personality data
        avatar_config = await self._generate_avatar_config(personality_profile)
        
        # Create avatar
        avatar = AIAvatar(
            id=uuid.uuid4(),
            user_id=user_id,
            personality_profile_id=personality_profile_id,
            name=f"{user.first_name}'s Avatar",
            description=f"AI representation of {user.first_name}",
            personality_traits=avatar_config["personality_traits"],
            communication_patterns=avatar_config["communication_patterns"],
            response_style=avatar_config["response_style"],
            memory_context=avatar_config["memory_context"],
            conversation_skills=avatar_config["conversation_skills"],
            emotional_range=avatar_config["emotional_range"],
            cultural_context=avatar_config["cultural_context"],
            completeness_score=avatar_config["completeness_score"],
            authenticity_score=0.8,  # Initial score
            consistency_score=0.8,   # Initial score
            status=AvatarStatus.CREATING.value,
            improvement_areas=avatar_config["improvement_areas"],
            suggested_actions=avatar_config["suggested_actions"]
        )
        
        self.db.add(avatar)
        await self.db.commit()
        await self.db.refresh(avatar)
        
        # Start initial training
        await self._start_avatar_training(avatar.id, "initial", "Avatar creation")
        
        # Refresh avatar after training to get updated status and training info
        await self.db.refresh(avatar)
        
        return avatar
    
    async def update_avatar_from_personality(
        self, 
        avatar_id: str, 
        personality_profile_id: str
    ) -> AIAvatar:
        """Update an existing avatar when personality data changes."""
        
        # Get avatar and personality profile
        avatar_result = await self.db.execute(select(AIAvatar).where(AIAvatar.id == avatar_id))
        avatar = avatar_result.scalar_one_or_none()
        if not avatar:
            raise ValueError("Avatar not found")
        
        profile_result = await self.db.execute(
            select(PersonalityProfile).where(PersonalityProfile.id == personality_profile_id)
        )
        personality_profile = profile_result.scalar_one_or_none()
        if not personality_profile:
            raise ValueError("Personality profile not found")
        
        # Generate updated avatar configuration
        avatar_config = await self._generate_avatar_config(personality_profile)
        
        # Update avatar
        avatar.personality_profile_id = personality_profile_id
        avatar.personality_traits = avatar_config["personality_traits"]
        avatar.communication_patterns = avatar_config["communication_patterns"]
        avatar.response_style = avatar_config["response_style"]
        avatar.memory_context = avatar_config["memory_context"]
        avatar.conversation_skills = avatar_config["conversation_skills"]
        avatar.emotional_range = avatar_config["emotional_range"]
        avatar.cultural_context = avatar_config["cultural_context"]
        avatar.completeness_score = avatar_config["completeness_score"]
        avatar.improvement_areas = avatar_config["improvement_areas"]
        avatar.suggested_actions = avatar_config["suggested_actions"]
        avatar.status = AvatarStatus.TRAINING.value
        avatar.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(avatar)
        
        # Start retraining
        await self._start_avatar_training(avatar.id, "personality_update", "Personality profile updated")
        
        # Refresh avatar after training to get updated status and training info
        await self.db.refresh(avatar)
        
        return avatar
    
    async def get_avatar_by_user_id(self, user_id: str) -> Optional[AIAvatar]:
        """Get a user's AI avatar."""
        result = await self.db.execute(
            select(AIAvatar).where(AIAvatar.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def customize_avatar(
        self, 
        avatar_id: str, 
        customization_type: str,
        field_name: str,
        custom_value: Any,
        reason: Optional[str] = None
    ) -> AvatarCustomization:
        """Apply user customization to avatar."""
        
        # Get avatar
        avatar_result = await self.db.execute(select(AIAvatar).where(AIAvatar.id == avatar_id))
        avatar = avatar_result.scalar_one_or_none()
        if not avatar:
            raise ValueError("Avatar not found")
        
        # Get original value
        original_value = None
        if customization_type == "personality_adjustment":
            original_value = avatar.personality_traits.get(field_name)
        elif customization_type == "communication_style":
            original_value = avatar.communication_patterns.get(field_name)
        elif customization_type == "response_style":
            original_value = avatar.response_style.get(field_name)
        
        # Create customization
        customization = AvatarCustomization(
            id=uuid.uuid4(),
            avatar_id=avatar_id,
            customization_type=customization_type,
            field_name=field_name,
            original_value=original_value,
            custom_value=custom_value,
            reason=reason,
            confidence=1.0,
            impact_score=self._calculate_customization_impact(customization_type, field_name)
        )
        
        self.db.add(customization)
        
        # Apply customization to avatar
        await self._apply_customization_to_avatar(avatar, customization)
        
        await self.db.commit()
        await self.db.refresh(customization)
        
        return customization
    
    async def get_avatar_completeness_analysis(self, avatar_id: str) -> Dict[str, Any]:
        """Get detailed completeness analysis and improvement suggestions."""
        
        avatar_result = await self.db.execute(select(AIAvatar).where(AIAvatar.id == avatar_id))
        avatar = avatar_result.scalar_one_or_none()
        if not avatar:
            raise ValueError("Avatar not found")
        
        # Analyze completeness
        analysis = {
            "overall_score": avatar.completeness_score,
            "authenticity_score": avatar.authenticity_score,
            "consistency_score": avatar.consistency_score,
            "areas": {
                "personality_traits": self._analyze_personality_completeness(avatar.personality_traits),
                "communication_patterns": self._analyze_communication_completeness(avatar.communication_patterns),
                "emotional_range": self._analyze_emotional_completeness(avatar.emotional_range),
                "conversation_skills": self._analyze_conversation_completeness(avatar.conversation_skills)
            },
            "improvement_areas": avatar.improvement_areas,
            "suggested_actions": avatar.suggested_actions,
            "training_status": {
                "iterations": avatar.training_iterations,
                "last_training": avatar.last_training_date.isoformat() if avatar.last_training_date else None,
                "status": avatar.status
            }
        }
        
        return analysis
    
    async def _generate_avatar_config(self, personality_profile: PersonalityProfile) -> Dict[str, Any]:
        """Generate avatar configuration from personality profile."""
        
        # Calculate completeness score
        completeness_score = self._calculate_avatar_completeness(personality_profile)
        
        # Generate personality traits for AI
        personality_traits = {
            "big_five": {
                "openness": personality_profile.openness or 0.5,
                "conscientiousness": personality_profile.conscientiousness or 0.5,
                "extraversion": personality_profile.extraversion or 0.5,
                "agreeableness": personality_profile.agreeableness or 0.5,
                "neuroticism": personality_profile.neuroticism or 0.5
            },
            "values": personality_profile.values or {},
            "core_beliefs": self._extract_core_beliefs(personality_profile),
            "motivations": self._extract_motivations(personality_profile)
        }
        
        # Generate communication patterns
        communication_patterns = {
            "style": personality_profile.communication_style or "balanced",
            "directness": self._calculate_directness(personality_profile),
            "emotional_expression": self._calculate_emotional_expression(personality_profile),
            "conflict_approach": personality_profile.conflict_resolution_style or "collaborative",
            "listening_style": self._determine_listening_style(personality_profile),
            "humor_usage": self._determine_humor_usage(personality_profile)
        }
        
        # Generate response style
        response_style = {
            "response_length": self._determine_response_length(personality_profile),
            "formality_level": self._determine_formality(personality_profile),
            "question_asking": self._determine_question_frequency(personality_profile),
            "empathy_level": personality_profile.agreeableness or 0.5,
            "assertiveness": self._calculate_assertiveness(personality_profile)
        }
        
        # Generate memory context
        memory_context = {
            "focus_areas": self._determine_memory_focus(personality_profile),
            "detail_level": self._determine_memory_detail(personality_profile),
            "emotional_memory": self._determine_emotional_memory(personality_profile)
        }
        
        # Generate conversation skills
        conversation_skills = {
            "topic_initiation": self._calculate_topic_initiation(personality_profile),
            "topic_maintenance": self._calculate_topic_maintenance(personality_profile),
            "emotional_support": self._calculate_emotional_support(personality_profile),
            "conflict_resolution": self._calculate_conflict_resolution(personality_profile),
            "humor_appreciation": self._calculate_humor_appreciation(personality_profile)
        }
        
        # Generate emotional range
        emotional_range = {
            "expressiveness": personality_profile.extraversion or 0.5,
            "emotional_stability": 1.0 - (personality_profile.neuroticism or 0.5),
            "empathy": personality_profile.agreeableness or 0.5,
            "emotional_intelligence": self._calculate_emotional_intelligence(personality_profile)
        }
        
        # Generate cultural context (placeholder for future internationalization)
        cultural_context = {
            "language": "en",
            "cultural_background": "western",
            "communication_norms": "direct",
            "relationship_expectations": "egalitarian"
        }
        
        # Identify improvement areas
        improvement_areas = []
        suggested_actions = []
        
        if completeness_score < 0.7:
            improvement_areas.append("personality_completeness")
            suggested_actions.append("Complete more personality assessment questions")
        
        if not personality_profile.values:
            improvement_areas.append("values_definition")
            suggested_actions.append("Define your core values and priorities")
        
        if not personality_profile.communication_style:
            improvement_areas.append("communication_style")
            suggested_actions.append("Specify your preferred communication style")
        
        return {
            "personality_traits": personality_traits,
            "communication_patterns": communication_patterns,
            "response_style": response_style,
            "memory_context": memory_context,
            "conversation_skills": conversation_skills,
            "emotional_range": emotional_range,
            "cultural_context": cultural_context,
            "completeness_score": completeness_score,
            "improvement_areas": improvement_areas,
            "suggested_actions": suggested_actions
        }
    
    def _calculate_avatar_completeness(self, personality_profile: PersonalityProfile) -> float:
        """Calculate how complete the avatar configuration is."""
        score = 0.0
        total_weight = 0.0
        
        # Big Five traits (40% weight)
        big_five_traits = [
            personality_profile.openness,
            personality_profile.conscientiousness,
            personality_profile.extraversion,
            personality_profile.agreeableness,
            personality_profile.neuroticism
        ]
        completed_traits = sum(1 for trait in big_five_traits if trait is not None)
        score += (completed_traits / 5) * 0.4
        total_weight += 0.4
        
        # Values (25% weight)
        if personality_profile.values:
            score += 0.25
        total_weight += 0.25
        
        # Communication style (20% weight)
        if personality_profile.communication_style:
            score += 0.2
        total_weight += 0.2
        
        # Conflict resolution style (15% weight)
        if personality_profile.conflict_resolution_style:
            score += 0.15
        total_weight += 0.15
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _extract_core_beliefs(self, personality_profile: PersonalityProfile) -> List[str]:
        """Extract core beliefs from personality data."""
        beliefs = []
        
        if personality_profile.openness and personality_profile.openness > 0.7:
            beliefs.append("Growth and learning are essential")
            beliefs.append("Diversity of thought is valuable")
        
        if personality_profile.conscientiousness and personality_profile.conscientiousness > 0.7:
            beliefs.append("Hard work leads to success")
            beliefs.append("Reliability is important in relationships")
        
        if personality_profile.agreeableness and personality_profile.agreeableness > 0.7:
            beliefs.append("Cooperation is better than competition")
            beliefs.append("Everyone deserves respect and kindness")
        
        return beliefs
    
    def _extract_motivations(self, personality_profile: PersonalityProfile) -> List[str]:
        """Extract motivations from personality data."""
        motivations = []
        
        if personality_profile.values:
            for value, importance in personality_profile.values.items():
                if isinstance(importance, (int, float)) and importance > 0.7:
                    motivations.append(f"Achieving {value.lower()}")
        
        return motivations
    
    def _calculate_directness(self, personality_profile: PersonalityProfile) -> float:
        """Calculate communication directness."""
        base_directness = 0.5
        
        if personality_profile.extraversion:
            base_directness += (personality_profile.extraversion - 0.5) * 0.3
        
        if personality_profile.agreeableness:
            base_directness -= (personality_profile.agreeableness - 0.5) * 0.2
        
        return max(0.0, min(1.0, base_directness))
    
    def _calculate_emotional_expression(self, personality_profile: PersonalityProfile) -> float:
        """Calculate emotional expression level."""
        base_expression = 0.5
        
        if personality_profile.extraversion:
            base_expression += (personality_profile.extraversion - 0.5) * 0.4
        
        if personality_profile.neuroticism:
            base_expression += (personality_profile.neuroticism - 0.5) * 0.2
        
        return max(0.0, min(1.0, base_expression))
    
    def _determine_listening_style(self, personality_profile: PersonalityProfile) -> str:
        """Determine listening style based on personality."""
        if personality_profile.agreeableness and personality_profile.agreeableness > 0.7:
            return "empathetic"
        elif personality_profile.conscientiousness and personality_profile.conscientiousness > 0.7:
            return "analytical"
        elif personality_profile.extraversion and personality_profile.extraversion > 0.7:
            return "interactive"
        else:
            return "balanced"
    
    def _determine_humor_usage(self, personality_profile: PersonalityProfile) -> str:
        """Determine humor usage pattern."""
        if personality_profile.extraversion and personality_profile.extraversion > 0.7:
            if personality_profile.agreeableness and personality_profile.agreeableness > 0.6:
                return "frequent_positive"
            else:
                return "frequent_mixed"
        elif personality_profile.openness and personality_profile.openness > 0.7:
            return "witty_occasional"
        else:
            return "minimal"
    
    def _determine_response_length(self, personality_profile: PersonalityProfile) -> str:
        """Determine typical response length."""
        if personality_profile.extraversion and personality_profile.extraversion > 0.7:
            return "detailed"
        elif personality_profile.conscientiousness and personality_profile.conscientiousness > 0.7:
            return "thorough"
        else:
            return "concise"
    
    def _determine_formality(self, personality_profile: PersonalityProfile) -> str:
        """Determine formality level."""
        if personality_profile.conscientiousness and personality_profile.conscientiousness > 0.7:
            return "formal"
        elif personality_profile.extraversion and personality_profile.extraversion > 0.7:
            return "casual"
        else:
            return "moderate"
    
    def _determine_question_frequency(self, personality_profile: PersonalityProfile) -> str:
        """Determine how often avatar asks questions."""
        if personality_profile.openness and personality_profile.openness > 0.7:
            return "frequent"
        elif personality_profile.extraversion and personality_profile.extraversion > 0.7:
            return "moderate"
        else:
            return "occasional"
    
    def _calculate_assertiveness(self, personality_profile: PersonalityProfile) -> float:
        """Calculate assertiveness level."""
        base_assertiveness = 0.5
        
        if personality_profile.extraversion:
            base_assertiveness += (personality_profile.extraversion - 0.5) * 0.3
        
        if personality_profile.agreeableness:
            base_assertiveness -= (personality_profile.agreeableness - 0.5) * 0.2
        
        if personality_profile.conscientiousness:
            base_assertiveness += (personality_profile.conscientiousness - 0.5) * 0.1
        
        return max(0.0, min(1.0, base_assertiveness))
    
    def _determine_memory_focus(self, personality_profile: PersonalityProfile) -> List[str]:
        """Determine what the avatar focuses on remembering."""
        focus_areas = ["basic_facts", "preferences"]
        
        if personality_profile.agreeableness and personality_profile.agreeableness > 0.6:
            focus_areas.append("emotions")
            focus_areas.append("relationships")
        
        if personality_profile.conscientiousness and personality_profile.conscientiousness > 0.6:
            focus_areas.append("goals")
            focus_areas.append("commitments")
        
        if personality_profile.openness and personality_profile.openness > 0.6:
            focus_areas.append("ideas")
            focus_areas.append("experiences")
        
        return focus_areas
    
    def _determine_memory_detail(self, personality_profile: PersonalityProfile) -> str:
        """Determine level of detail in memory."""
        if personality_profile.conscientiousness and personality_profile.conscientiousness > 0.7:
            return "high"
        elif personality_profile.openness and personality_profile.openness > 0.7:
            return "moderate"
        else:
            return "basic"
    
    def _determine_emotional_memory(self, personality_profile: PersonalityProfile) -> float:
        """Determine emotional memory strength."""
        base_emotional_memory = 0.5
        
        if personality_profile.agreeableness:
            base_emotional_memory += (personality_profile.agreeableness - 0.5) * 0.3
        
        if personality_profile.neuroticism:
            base_emotional_memory += (personality_profile.neuroticism - 0.5) * 0.2
        
        return max(0.0, min(1.0, base_emotional_memory))
    
    def _calculate_topic_initiation(self, personality_profile: PersonalityProfile) -> float:
        """Calculate topic initiation ability."""
        base_initiation = 0.5
        
        if personality_profile.extraversion:
            base_initiation += (personality_profile.extraversion - 0.5) * 0.4
        
        if personality_profile.openness:
            base_initiation += (personality_profile.openness - 0.5) * 0.2
        
        return max(0.0, min(1.0, base_initiation))
    
    def _calculate_topic_maintenance(self, personality_profile: PersonalityProfile) -> float:
        """Calculate topic maintenance ability."""
        base_maintenance = 0.5
        
        if personality_profile.conscientiousness:
            base_maintenance += (personality_profile.conscientiousness - 0.5) * 0.3
        
        if personality_profile.agreeableness:
            base_maintenance += (personality_profile.agreeableness - 0.5) * 0.2
        
        return max(0.0, min(1.0, base_maintenance))
    
    def _calculate_emotional_support(self, personality_profile: PersonalityProfile) -> float:
        """Calculate emotional support ability."""
        base_support = 0.5
        
        if personality_profile.agreeableness:
            base_support += (personality_profile.agreeableness - 0.5) * 0.4
        
        if personality_profile.neuroticism:
            # Lower neuroticism = better emotional stability for supporting others
            base_support += (0.5 - personality_profile.neuroticism) * 0.2
        
        return max(0.0, min(1.0, base_support))
    
    def _calculate_conflict_resolution(self, personality_profile: PersonalityProfile) -> float:
        """Calculate conflict resolution ability."""
        base_resolution = 0.5
        
        if personality_profile.agreeableness:
            base_resolution += (personality_profile.agreeableness - 0.5) * 0.3
        
        if personality_profile.conscientiousness:
            base_resolution += (personality_profile.conscientiousness - 0.5) * 0.2
        
        if personality_profile.neuroticism:
            base_resolution -= (personality_profile.neuroticism - 0.5) * 0.1
        
        return max(0.0, min(1.0, base_resolution))
    
    def _calculate_humor_appreciation(self, personality_profile: PersonalityProfile) -> float:
        """Calculate humor appreciation and usage."""
        base_humor = 0.5
        
        if personality_profile.extraversion:
            base_humor += (personality_profile.extraversion - 0.5) * 0.3
        
        if personality_profile.openness:
            base_humor += (personality_profile.openness - 0.5) * 0.2
        
        return max(0.0, min(1.0, base_humor))
    
    def _calculate_emotional_intelligence(self, personality_profile: PersonalityProfile) -> float:
        """Calculate emotional intelligence score."""
        base_ei = 0.5
        
        if personality_profile.agreeableness:
            base_ei += (personality_profile.agreeableness - 0.5) * 0.3
        
        if personality_profile.extraversion:
            base_ei += (personality_profile.extraversion - 0.5) * 0.2
        
        if personality_profile.neuroticism:
            base_ei -= (personality_profile.neuroticism - 0.5) * 0.1
        
        return max(0.0, min(1.0, base_ei))
    
    async def _start_avatar_training(
        self, 
        avatar_id: str, 
        training_type: str, 
        trigger_reason: str
    ) -> AvatarTrainingSession:
        """Start avatar training session."""
        
        training_session = AvatarTrainingSession(
            id=uuid.uuid4(),
            avatar_id=avatar_id,
            training_type=training_type,
            trigger_reason=trigger_reason,
            input_data={},  # Would contain actual training data
            training_parameters={"version": "1.0"},
            started_at=datetime.utcnow()
        )
        
        self.db.add(training_session)
        
        # Update avatar status
        await self.db.execute(
            update(AIAvatar)
            .where(AIAvatar.id == avatar_id)
            .values(status=AvatarStatus.TRAINING.value)
        )
        
        await self.db.commit()
        
        # In a real implementation, this would trigger actual AI training
        # For now, we'll simulate successful training
        await self._complete_avatar_training(training_session.id, True)
        
        return training_session
    
    async def _complete_avatar_training(
        self, 
        training_session_id: str, 
        success: bool,
        error_message: Optional[str] = None
    ):
        """Complete avatar training session."""
        
        # Update training session
        await self.db.execute(
            update(AvatarTrainingSession)
            .where(AvatarTrainingSession.id == training_session_id)
            .values(
                success=success,
                error_message=error_message,
                completed_at=datetime.utcnow(),
                duration_seconds=30  # Simulated duration
            )
        )
        
        # Get training session to find avatar
        session_result = await self.db.execute(
            select(AvatarTrainingSession).where(AvatarTrainingSession.id == training_session_id)
        )
        session = session_result.scalar_one()
        
        # Get current avatar to increment training iterations
        avatar_result = await self.db.execute(
            select(AIAvatar).where(AIAvatar.id == session.avatar_id)
        )
        avatar = avatar_result.scalar_one()
        
        # Update avatar status and training count
        new_status = AvatarStatus.ACTIVE.value if success else AvatarStatus.ERROR.value
        await self.db.execute(
            update(AIAvatar)
            .where(AIAvatar.id == session.avatar_id)
            .values(
                status=new_status,
                training_iterations=avatar.training_iterations + 1,
                last_training_date=datetime.utcnow()
            )
        )
        
        await self.db.commit()
    
    def _calculate_customization_impact(self, customization_type: str, field_name: str) -> float:
        """Calculate the impact score of a customization."""
        impact_weights = {
            "personality_adjustment": {
                "openness": 0.8,
                "conscientiousness": 0.7,
                "extraversion": 0.9,
                "agreeableness": 0.8,
                "neuroticism": 0.6
            },
            "communication_style": {
                "directness": 0.7,
                "formality": 0.5,
                "humor_usage": 0.6
            },
            "response_style": {
                "response_length": 0.4,
                "assertiveness": 0.6
            }
        }
        
        return impact_weights.get(customization_type, {}).get(field_name, 0.5)
    
    async def _apply_customization_to_avatar(
        self, 
        avatar: AIAvatar, 
        customization: AvatarCustomization
    ):
        """Apply a customization to the avatar configuration."""
        
        if customization.customization_type == "personality_adjustment":
            if not avatar.personality_traits:
                avatar.personality_traits = {}
            avatar.personality_traits[customization.field_name] = customization.custom_value
        
        elif customization.customization_type == "communication_style":
            if not avatar.communication_patterns:
                avatar.communication_patterns = {}
            avatar.communication_patterns[customization.field_name] = customization.custom_value
        
        elif customization.customization_type == "response_style":
            if not avatar.response_style:
                avatar.response_style = {}
            avatar.response_style[customization.field_name] = customization.custom_value
        
        # Mark avatar for retraining if impact is significant
        if customization.impact_score > 0.6:
            avatar.status = AvatarStatus.TRAINING.value
    
    def _analyze_personality_completeness(self, personality_traits: Dict) -> Dict[str, Any]:
        """Analyze personality traits completeness."""
        if not personality_traits:
            return {"score": 0.0, "missing": ["All personality traits"], "suggestions": ["Complete personality assessment"]}
        
        big_five = personality_traits.get("big_five", {})
        missing = []
        
        for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
            if trait not in big_five or big_five[trait] is None:
                missing.append(trait)
        
        score = (5 - len(missing)) / 5
        suggestions = []
        
        if missing:
            suggestions.append(f"Complete assessment for: {', '.join(missing)}")
        
        if not personality_traits.get("values"):
            suggestions.append("Define your core values")
        
        return {"score": score, "missing": missing, "suggestions": suggestions}
    
    def _analyze_communication_completeness(self, communication_patterns: Dict) -> Dict[str, Any]:
        """Analyze communication patterns completeness."""
        if not communication_patterns:
            return {"score": 0.0, "missing": ["All communication patterns"], "suggestions": ["Define communication preferences"]}
        
        required_fields = ["style", "directness", "conflict_approach"]
        missing = [field for field in required_fields if field not in communication_patterns]
        
        score = (len(required_fields) - len(missing)) / len(required_fields)
        suggestions = []
        
        if missing:
            suggestions.append(f"Define: {', '.join(missing)}")
        
        return {"score": score, "missing": missing, "suggestions": suggestions}
    
    def _analyze_emotional_completeness(self, emotional_range: Dict) -> Dict[str, Any]:
        """Analyze emotional range completeness."""
        if not emotional_range:
            return {"score": 0.0, "missing": ["All emotional data"], "suggestions": ["Complete emotional assessment"]}
        
        required_fields = ["expressiveness", "emotional_stability", "empathy"]
        missing = [field for field in required_fields if field not in emotional_range]
        
        score = (len(required_fields) - len(missing)) / len(required_fields)
        suggestions = []
        
        if missing:
            suggestions.append(f"Assess: {', '.join(missing)}")
        
        return {"score": score, "missing": missing, "suggestions": suggestions}
    
    def _analyze_conversation_completeness(self, conversation_skills: Dict) -> Dict[str, Any]:
        """Analyze conversation skills completeness."""
        if not conversation_skills:
            return {"score": 0.0, "missing": ["All conversation skills"], "suggestions": ["Define conversation preferences"]}
        
        required_fields = ["topic_initiation", "emotional_support", "conflict_resolution"]
        missing = [field for field in required_fields if field not in conversation_skills]
        
        score = (len(required_fields) - len(missing)) / len(required_fields)
        suggestions = []
        
        if missing:
            suggestions.append(f"Develop: {', '.join(missing)}")
        
        return {"score": score, "missing": missing, "suggestions": suggestions}