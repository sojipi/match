"""
Unit tests for personality assessment system.
Tests questionnaire logic, data validation, and avatar creation/customization.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, Any, List
import uuid

from app.api.v1.endpoints.personality import (
    PersonalityQuestion, PersonalityAnswer, PersonalityAssessmentRequest,
    PersonalityProfileResponse, PersonalityInsight, AssessmentProgress,
    PERSONALITY_QUESTIONS, _calculate_personality_scores, _calculate_completeness_score
)
from app.services.avatar_service import AvatarService
from app.models.user import User, PersonalityProfile
from app.models.avatar import AIAvatar, AvatarCustomization, AvatarStatus


class TestPersonalityQuestionnaire:
    """Test personality questionnaire logic and data validation."""
    
    def test_personality_questions_structure(self):
        """Test that personality questions have correct structure."""
        # Verify we have questions
        assert len(PERSONALITY_QUESTIONS) > 0
        
        # Test each question has required fields
        for question in PERSONALITY_QUESTIONS:
            assert hasattr(question, 'id')
            assert hasattr(question, 'category')
            assert hasattr(question, 'question')
            assert hasattr(question, 'question_type')
            assert question.id is not None
            assert question.category is not None
            assert question.question is not None
            assert question.question_type in ['scale', 'multiple_choice', 'ranking']
    
    def test_scale_questions_validation(self):
        """Test scale questions have proper scale configuration."""
        scale_questions = [q for q in PERSONALITY_QUESTIONS if q.question_type == 'scale']
        
        for question in scale_questions:
            assert question.scale_min is not None
            assert question.scale_max is not None
            assert question.scale_min < question.scale_max
            assert question.scale_labels is not None
            assert isinstance(question.scale_labels, dict)
    
    def test_multiple_choice_questions_validation(self):
        """Test multiple choice questions have options."""
        mc_questions = [q for q in PERSONALITY_QUESTIONS if q.question_type == 'multiple_choice']
        
        for question in mc_questions:
            assert question.options is not None
            assert isinstance(question.options, list)
            assert len(question.options) > 1
    
    def test_ranking_questions_validation(self):
        """Test ranking questions have options to rank."""
        ranking_questions = [q for q in PERSONALITY_QUESTIONS if q.question_type == 'ranking']
        
        for question in ranking_questions:
            assert question.options is not None
            assert isinstance(question.options, list)
            assert len(question.options) >= 2
    
    def test_big_five_coverage(self):
        """Test that questions cover all Big Five personality traits."""
        categories = {q.category for q in PERSONALITY_QUESTIONS}
        
        # Should have questions for each Big Five trait
        big_five_traits = {'openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'}
        for trait in big_five_traits:
            assert trait in categories, f"Missing questions for {trait}"
    
    def test_personality_answer_validation(self):
        """Test personality answer model validation."""
        # Valid scale answer
        scale_answer = PersonalityAnswer(
            question_id="open_1",
            answer=5,
            confidence=0.8
        )
        assert scale_answer.question_id == "open_1"
        assert scale_answer.answer == 5
        assert scale_answer.confidence == 0.8
        
        # Valid multiple choice answer
        mc_answer = PersonalityAnswer(
            question_id="values_2",
            answer="Trust and honesty"
        )
        assert mc_answer.question_id == "values_2"
        assert mc_answer.answer == "Trust and honesty"
        
        # Valid ranking answer
        ranking_answer = PersonalityAnswer(
            question_id="values_1",
            answer=["Family", "Career Success", "Personal Growth"]
        )
        assert ranking_answer.question_id == "values_1"
        assert isinstance(ranking_answer.answer, list)


class TestPersonalityScoring:
    """Test personality scoring algorithms."""
    
    def test_calculate_personality_scores_big_five(self):
        """Test Big Five personality trait calculation."""
        # Create test answers for openness
        answers = [
            PersonalityAnswer(question_id="open_1", answer=7),  # High openness
            PersonalityAnswer(question_id="open_2", answer=2),  # Low preference for routine (reverse scored)
        ]
        
        scores = _calculate_personality_scores(answers)
        
        # Should calculate openness score
        assert "openness" in scores
        assert scores["openness"] is not None
        assert 0.0 <= scores["openness"] <= 1.0
        
        # High openness answer (7/7) + low routine preference (reverse scored 2/7 -> 5/7)
        # Expected: (1.0 + 5/7) / 2 ≈ 0.857
        expected_openness = (1.0 + (1.0 - 2/7)) / 2
        assert abs(scores["openness"] - expected_openness) < 0.01
    
    def test_calculate_personality_scores_conscientiousness(self):
        """Test conscientiousness scoring."""
        answers = [
            PersonalityAnswer(question_id="cons_1", answer=6),  # High conscientiousness
            PersonalityAnswer(question_id="cons_2", answer=3),  # Low procrastination (reverse scored)
        ]
        
        scores = _calculate_personality_scores(answers)
        
        assert "conscientiousness" in scores
        assert scores["conscientiousness"] is not None
        assert 0.0 <= scores["conscientiousness"] <= 1.0
        
        # Expected: (6/7 + (1 - 3/7)) / 2
        expected_cons = (6/7 + (1.0 - 3/7)) / 2
        assert abs(scores["conscientiousness"] - expected_cons) < 0.01
    
    def test_calculate_personality_scores_values(self):
        """Test values scoring from ranking questions."""
        answers = [
            PersonalityAnswer(
                question_id="values_1", 
                answer=["Family", "Personal Growth", "Career Success", "Adventure", "Security", "Creativity"]
            )
        ]
        
        scores = _calculate_personality_scores(answers)
        
        assert "values" in scores
        assert isinstance(scores["values"], dict)
        
        # Family should have highest score (ranked first)
        assert "Family" in scores["values"]
        assert scores["values"]["Family"] == 1.0  # First place = 1.0
        
        # Personal Growth should be second
        assert "Personal Growth" in scores["values"]
        assert scores["values"]["Personal Growth"] == 1.0 - (1/6)  # Second place
        
        # Creativity should have lowest score (ranked last)
        assert "Creativity" in scores["values"]
        assert scores["values"]["Creativity"] == 1.0 - (5/6)  # Last place
    
    def test_calculate_personality_scores_communication_style(self):
        """Test communication style extraction."""
        answers = [
            PersonalityAnswer(question_id="comm_2", answer="Direct and straightforward")
        ]
        
        scores = _calculate_personality_scores(answers)
        
        assert "communication_style" in scores
        assert scores["communication_style"] == "Direct and straightforward"
    
    def test_calculate_personality_scores_conflict_resolution(self):
        """Test conflict resolution style extraction."""
        answers = [
            PersonalityAnswer(question_id="comm_1", answer="Seek compromise")
        ]
        
        scores = _calculate_personality_scores(answers)
        
        assert "conflict_resolution_style" in scores
        assert scores["conflict_resolution_style"] == "Seek compromise"
    
    def test_calculate_completeness_score(self):
        """Test profile completeness calculation."""
        # Complete profile
        complete_scores = {
            "openness": 0.8,
            "conscientiousness": 0.7,
            "extraversion": 0.6,
            "agreeableness": 0.9,
            "neuroticism": 0.4,
            "values": {"Family": 1.0, "Career": 0.8},
            "communication_style": "Direct and straightforward",
            "conflict_resolution_style": "Seek compromise"
        }
        
        completeness = _calculate_completeness_score(complete_scores)
        assert completeness > 1.0  # Should exceed 1.0 with bonus points
        
        # Incomplete profile (missing traits)
        incomplete_scores = {
            "openness": 0.8,
            "conscientiousness": None,
            "extraversion": None,
            "agreeableness": 0.9,
            "neuroticism": None
        }
        
        completeness = _calculate_completeness_score(incomplete_scores)
        assert 0.0 <= completeness <= 1.0
        assert completeness < 0.5  # Should be low due to missing traits
    
    def test_calculate_personality_scores_partial_answers(self):
        """Test scoring with partial answers."""
        # Only answer some questions
        answers = [
            PersonalityAnswer(question_id="open_1", answer=5),
            PersonalityAnswer(question_id="extra_1", answer=6),
        ]
        
        scores = _calculate_personality_scores(answers)
        
        # Should have scores for answered traits
        assert scores["openness"] is not None
        assert scores["extraversion"] is not None
        
        # Should have default/None for unanswered traits
        assert scores["conscientiousness"] == 0.0  # Default when no answers
        assert scores["agreeableness"] == 0.0
        assert scores["neuroticism"] == 0.0


class TestAvatarCreation:
    """Test avatar creation and customization features."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def avatar_service(self, mock_db):
        """Create avatar service with mocked database."""
        return AvatarService(mock_db)
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        return User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password_hash="hashed_password"
        )
    
    @pytest.fixture
    def sample_personality_profile(self, sample_user):
        """Create sample personality profile."""
        return PersonalityProfile(
            id=uuid.uuid4(),
            user_id=sample_user.id,
            openness=0.8,
            conscientiousness=0.7,
            extraversion=0.6,
            agreeableness=0.9,
            neuroticism=0.3,
            values={"Family": 1.0, "Career": 0.8, "Adventure": 0.6},
            communication_style="Direct and straightforward",
            conflict_resolution_style="Seek compromise",
            completeness_score=0.95
        )
    
    async def test_create_avatar_from_personality(self, avatar_service, mock_db, sample_user, sample_personality_profile):
        """Test avatar creation from personality profile."""
        # Mock database queries
        mock_db.execute.return_value.scalar_one_or_none.side_effect = [
            sample_user,  # User query
            sample_personality_profile,  # Personality profile query
            None  # No existing avatar
        ]
        
        # Mock database operations
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Create avatar
        avatar = await avatar_service.create_avatar_from_personality(
            str(sample_user.id),
            str(sample_personality_profile.id)
        )
        
        # Verify avatar creation
        assert avatar is not None
        assert avatar.user_id == str(sample_user.id)
        assert avatar.personality_profile_id == str(sample_personality_profile.id)
        assert avatar.name == f"{sample_user.first_name}'s Avatar"
        assert avatar.status == AvatarStatus.CREATING.value
        
        # Verify personality traits mapping
        assert avatar.personality_traits is not None
        assert "big_five" in avatar.personality_traits
        assert avatar.personality_traits["big_five"]["openness"] == 0.8
        assert avatar.personality_traits["big_five"]["conscientiousness"] == 0.7
        
        # Verify communication patterns
        assert avatar.communication_patterns is not None
        assert "style" in avatar.communication_patterns
        assert avatar.communication_patterns["style"] == "Direct and straightforward"
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()
    
    async def test_update_existing_avatar(self, avatar_service, mock_db, sample_user, sample_personality_profile):
        """Test updating existing avatar when creating from personality."""
        existing_avatar = AIAvatar(
            id=uuid.uuid4(),
            user_id=str(sample_user.id),
            personality_profile_id=str(sample_personality_profile.id),
            name="Existing Avatar",
            status=AvatarStatus.ACTIVE.value
        )
        
        # Mock database queries - return existing avatar
        mock_db.execute.return_value.scalar_one_or_none.side_effect = [
            sample_user,  # User query
            sample_personality_profile,  # Personality profile query
            existing_avatar  # Existing avatar found
        ]
        
        with patch.object(avatar_service, 'update_avatar_from_personality') as mock_update:
            mock_update.return_value = existing_avatar
            
            result = await avatar_service.create_avatar_from_personality(
                str(sample_user.id),
                str(sample_personality_profile.id)
            )
            
            # Should call update instead of create
            mock_update.assert_called_once_with(existing_avatar.id, str(sample_personality_profile.id))
            assert result == existing_avatar
    
    def test_avatar_completeness_calculation(self, avatar_service, sample_personality_profile):
        """Test avatar completeness score calculation."""
        completeness = avatar_service._calculate_avatar_completeness(sample_personality_profile)
        
        # Should be high completeness for complete profile
        assert 0.8 <= completeness <= 1.0
        
        # Test incomplete profile
        incomplete_profile = PersonalityProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            openness=0.8,
            conscientiousness=None,  # Missing
            extraversion=None,       # Missing
            agreeableness=None,      # Missing
            neuroticism=None,        # Missing
            values=None,             # Missing
            communication_style=None, # Missing
            conflict_resolution_style=None  # Missing
        )
        
        incomplete_completeness = avatar_service._calculate_avatar_completeness(incomplete_profile)
        assert incomplete_completeness < 0.5  # Should be low
    
    def test_core_beliefs_extraction(self, avatar_service, sample_personality_profile):
        """Test extraction of core beliefs from personality data."""
        beliefs = avatar_service._extract_core_beliefs(sample_personality_profile)
        
        assert isinstance(beliefs, list)
        
        # High openness should generate growth-related beliefs
        assert any("growth" in belief.lower() or "learning" in belief.lower() for belief in beliefs)
        
        # High conscientiousness should generate work-related beliefs
        assert any("work" in belief.lower() or "reliability" in belief.lower() for belief in beliefs)
        
        # High agreeableness should generate cooperation-related beliefs
        assert any("cooperation" in belief.lower() or "respect" in belief.lower() for belief in beliefs)
    
    def test_motivations_extraction(self, avatar_service, sample_personality_profile):
        """Test extraction of motivations from personality values."""
        motivations = avatar_service._extract_motivations(sample_personality_profile)
        
        assert isinstance(motivations, list)
        
        # Should extract motivations from high-importance values
        motivation_text = " ".join(motivations).lower()
        assert "family" in motivation_text  # High importance value
        assert "career" in motivation_text  # High importance value
    
    def test_communication_directness_calculation(self, avatar_service, sample_personality_profile):
        """Test communication directness calculation."""
        directness = avatar_service._calculate_directness(sample_personality_profile)
        
        assert 0.0 <= directness <= 1.0
        
        # High extraversion should increase directness
        # High agreeableness should decrease directness
        # With extraversion=0.6 and agreeableness=0.9, expect moderate directness
        assert 0.3 <= directness <= 0.7
    
    def test_emotional_expression_calculation(self, avatar_service, sample_personality_profile):
        """Test emotional expression level calculation."""
        expression = avatar_service._calculate_emotional_expression(sample_personality_profile)
        
        assert 0.0 <= expression <= 1.0
        
        # Should be influenced by extraversion and neuroticism
        # With extraversion=0.6 and neuroticism=0.3, expect moderate expression
        assert 0.4 <= expression <= 0.8
    
    def test_listening_style_determination(self, avatar_service, sample_personality_profile):
        """Test listening style determination."""
        style = avatar_service._determine_listening_style(sample_personality_profile)
        
        assert style in ["empathetic", "analytical", "interactive", "balanced"]
        
        # High agreeableness (0.9) should result in empathetic style
        assert style == "empathetic"
    
    def test_humor_usage_determination(self, avatar_service, sample_personality_profile):
        """Test humor usage pattern determination."""
        humor = avatar_service._determine_humor_usage(sample_personality_profile)
        
        assert humor in ["frequent_positive", "frequent_mixed", "witty_occasional", "minimal"]
        
        # With moderate extraversion (0.6) and high agreeableness (0.9)
        # Should not be frequent but could be occasional
        assert humor in ["witty_occasional", "minimal"]
    
    async def test_avatar_customization(self, avatar_service, mock_db):
        """Test avatar customization functionality."""
        avatar_id = str(uuid.uuid4())
        
        # Mock avatar retrieval
        mock_avatar = AIAvatar(
            id=avatar_id,
            user_id=str(uuid.uuid4()),
            personality_traits={"big_five": {"openness": 0.8}},
            communication_patterns={"directness": 0.6},
            response_style={"assertiveness": 0.7}
        )
        
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_avatar
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Test personality adjustment
        customization = await avatar_service.customize_avatar(
            avatar_id,
            "personality_adjustment",
            "openness",
            0.9,
            "User wants to be more open to experiences"
        )
        
        assert customization is not None
        assert customization.avatar_id == avatar_id
        assert customization.customization_type == "personality_adjustment"
        assert customization.field_name == "openness"
        assert customization.custom_value == 0.9
        assert customization.original_value == 0.8
        assert customization.reason == "User wants to be more open to experiences"
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()
    
    def test_customization_impact_calculation(self, avatar_service):
        """Test customization impact score calculation."""
        # Test personality adjustment impact
        impact = avatar_service._calculate_customization_impact("personality_adjustment", "extraversion")
        assert 0.0 <= impact <= 1.0
        assert impact == 0.9  # High impact for extraversion
        
        # Test communication style impact
        impact = avatar_service._calculate_customization_impact("communication_style", "directness")
        assert impact == 0.7  # Medium-high impact for directness
        
        # Test response style impact
        impact = avatar_service._calculate_customization_impact("response_style", "response_length")
        assert impact == 0.4  # Lower impact for response length
        
        # Test unknown field
        impact = avatar_service._calculate_customization_impact("unknown_type", "unknown_field")
        assert impact == 0.5  # Default impact
    
    async def test_get_avatar_completeness_analysis(self, avatar_service, mock_db):
        """Test avatar completeness analysis."""
        avatar_id = str(uuid.uuid4())
        
        # Mock complete avatar
        mock_avatar = AIAvatar(
            id=avatar_id,
            user_id=str(uuid.uuid4()),
            completeness_score=0.85,
            authenticity_score=0.9,
            consistency_score=0.8,
            personality_traits={"big_five": {"openness": 0.8, "conscientiousness": 0.7}},
            communication_patterns={"style": "direct", "directness": 0.7},
            emotional_range={"expressiveness": 0.6, "empathy": 0.8},
            conversation_skills={"topic_initiation": 0.7, "emotional_support": 0.9},
            improvement_areas=["values_definition"],
            suggested_actions=["Define your core values"],
            training_iterations=3,
            last_training_date=datetime.utcnow(),
            status=AvatarStatus.ACTIVE.value
        )
        
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_avatar
        
        analysis = await avatar_service.get_avatar_completeness_analysis(avatar_id)
        
        assert analysis is not None
        assert analysis["overall_score"] == 0.85
        assert analysis["authenticity_score"] == 0.9
        assert analysis["consistency_score"] == 0.8
        
        # Check area analysis
        assert "areas" in analysis
        assert "personality_traits" in analysis["areas"]
        assert "communication_patterns" in analysis["areas"]
        assert "emotional_range" in analysis["areas"]
        assert "conversation_skills" in analysis["areas"]
        
        # Check improvement suggestions
        assert analysis["improvement_areas"] == ["values_definition"]
        assert analysis["suggested_actions"] == ["Define your core values"]
        
        # Check training status
        assert "training_status" in analysis
        assert analysis["training_status"]["iterations"] == 3
        assert analysis["training_status"]["status"] == AvatarStatus.ACTIVE.value


class TestPersonalityDataValidation:
    """Test personality data validation and error handling."""
    
    def test_personality_profile_response_validation(self):
        """Test personality profile response model validation."""
        profile_data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "openness": 0.8,
            "conscientiousness": 0.7,
            "extraversion": 0.6,
            "agreeableness": 0.9,
            "neuroticism": 0.3,
            "values": {"Family": 1.0, "Career": 0.8},
            "communication_style": "Direct and straightforward",
            "conflict_resolution_style": "Seek compromise",
            "completeness_score": 0.95,
            "assessment_version": "1.0",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        profile = PersonalityProfileResponse(**profile_data)
        
        assert profile.openness == 0.8
        assert profile.conscientiousness == 0.7
        assert profile.values == {"Family": 1.0, "Career": 0.8}
        assert profile.completeness_score == 0.95
    
    def test_assessment_progress_validation(self):
        """Test assessment progress model validation."""
        insights = [
            PersonalityInsight(
                trait="Openness",
                score=0.8,
                description="Your openness to new experiences",
                confidence=0.9
            )
        ]
        
        progress = AssessmentProgress(
            current_step=3,
            total_steps=5,
            completion_percentage=60.0,
            estimated_time_remaining=10,
            insights=insights
        )
        
        assert progress.current_step == 3
        assert progress.total_steps == 5
        assert progress.completion_percentage == 60.0
        assert len(progress.insights) == 1
        assert progress.insights[0].trait == "Openness"
    
    def test_personality_insight_validation(self):
        """Test personality insight model validation."""
        insight = PersonalityInsight(
            trait="Extraversion",
            score=0.7,
            description="Your social energy level",
            confidence=0.85
        )
        
        assert insight.trait == "Extraversion"
        assert insight.score == 0.7
        assert insight.description == "Your social energy level"
        assert insight.confidence == 0.85
    
    def test_assessment_request_validation(self):
        """Test personality assessment request validation."""
        answers = [
            PersonalityAnswer(question_id="open_1", answer=7, confidence=0.9),
            PersonalityAnswer(question_id="cons_1", answer=5, confidence=0.8)
        ]
        
        request = PersonalityAssessmentRequest(
            answers=answers,
            assessment_version="1.0"
        )
        
        assert len(request.answers) == 2
        assert request.assessment_version == "1.0"
        assert request.answers[0].question_id == "open_1"
        assert request.answers[0].answer == 7