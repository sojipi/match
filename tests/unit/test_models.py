"""
Unit tests for data models.

Tests the core data models including profiles, conversations, and scenarios.
"""

import pytest
from datetime import datetime
from ai_matchmaker.models import (
    PersonalityTraits,
    UserPreferences,
    BasicInfo,
    PersonalityProfile,
    UserProfile,
    Message,
    ConversationSession,
    Scenario,
    ScenarioResult,
    CompatibilityReport,
    Response,
    AgentType,
    SessionType,
    SessionStatus,
    ScenarioCategory,
    TrainingStatus,
    CommunicationStyle,
    ConflictResolutionStyle,
    validate_personality_profile,
    validate_user_profile,
)


class TestPersonalityTraits:
    """Test PersonalityTraits model."""
    
    def test_valid_personality_traits(self):
        """Test creating valid personality traits."""
        traits = PersonalityTraits(
            openness=0.8,
            conscientiousness=0.7,
            extraversion=0.6,
            agreeableness=0.9,
            neuroticism=0.3,
            values={'family': 0.9, 'career': 0.7},
            communication_style=CommunicationStyle.DIRECT,
            conflict_resolution_style=ConflictResolutionStyle.COLLABORATING
        )
        
        assert traits.openness == 0.8
        assert traits.values['family'] == 0.9
        assert traits.communication_style == CommunicationStyle.DIRECT
    
    def test_invalid_trait_values(self):
        """Test validation of trait values."""
        with pytest.raises(ValueError):
            PersonalityTraits(
                openness=1.5,  # Invalid: > 1.0
                conscientiousness=0.7,
                extraversion=0.6,
                agreeableness=0.9,
                neuroticism=0.3,
                communication_style=CommunicationStyle.DIRECT,
                conflict_resolution_style=ConflictResolutionStyle.COLLABORATING
            )
    
    def test_invalid_value_ratings(self):
        """Test validation of value ratings."""
        with pytest.raises(ValueError):
            PersonalityTraits(
                openness=0.8,
                conscientiousness=0.7,
                extraversion=0.6,
                agreeableness=0.9,
                neuroticism=0.3,
                values={'family': 1.5},  # Invalid: > 1.0
                communication_style=CommunicationStyle.DIRECT,
                conflict_resolution_style=ConflictResolutionStyle.COLLABORATING
            )


class TestUserPreferences:
    """Test UserPreferences model."""
    
    def test_valid_preferences(self):
        """Test creating valid user preferences."""
        prefs = UserPreferences(
            age_range=(25, 35),
            location_preferences=['New York', 'San Francisco'],
            relationship_goals=['marriage', 'children']
        )
        
        assert prefs.age_range == (25, 35)
        assert 'New York' in prefs.location_preferences
    
    def test_invalid_age_range(self):
        """Test validation of age range."""
        with pytest.raises(ValueError):
            UserPreferences(age_range=(35, 25))  # Max < Min
        
        with pytest.raises(ValueError):
            UserPreferences(age_range=(15, 25))  # Min < 18


class TestPersonalityProfile:
    """Test PersonalityProfile model."""
    
    def create_sample_profile(self):
        """Create a sample personality profile for testing."""
        traits = PersonalityTraits(
            openness=0.8,
            conscientiousness=0.7,
            extraversion=0.6,
            agreeableness=0.9,
            neuroticism=0.3,
            values={'family': 0.9, 'career': 0.7, 'adventure': 0.5},
            communication_style=CommunicationStyle.DIRECT,
            conflict_resolution_style=ConflictResolutionStyle.COLLABORATING
        )
        
        preferences = UserPreferences(
            age_range=(25, 35),
            location_preferences=['New York'],
            relationship_goals=['marriage']
        )
        
        return PersonalityProfile(
            user_id='test_user',
            personality_traits=traits,
            preferences=preferences
        )
    
    def test_profile_creation(self):
        """Test creating a personality profile."""
        profile = self.create_sample_profile()
        
        assert profile.user_id == 'test_user'
        assert profile.personality_traits.openness == 0.8
        assert profile.completeness_score >= 0.0
    
    def test_completeness_calculation(self):
        """Test profile completeness calculation."""
        profile = self.create_sample_profile()
        completeness = profile.calculate_completeness()
        
        assert 0.0 <= completeness <= 1.0
        # Should be high completeness since we have all required fields
        assert completeness > 0.8
    
    def test_get_relevant_traits(self):
        """Test retrieving relevant traits by context."""
        profile = self.create_sample_profile()
        traits = profile.get_relevant_traits("family planning")
        
        assert 'personality_traits' in traits
        assert 'communication_style' in traits
        # Should include family value since context mentions family
        assert 'relevant_values' in traits
        assert 'family' in traits['relevant_values']


class TestConversationSession:
    """Test ConversationSession model."""
    
    def test_session_creation(self):
        """Test creating a conversation session."""
        session = ConversationSession(
            session_id='test_session',
            participants=['user1', 'user2'],
            session_type=SessionType.MATCHMAKING
        )
        
        assert session.session_id == 'test_session'
        assert len(session.participants) == 2
        assert session.status == SessionStatus.ACTIVE
    
    def test_add_message(self):
        """Test adding messages to a session."""
        session = ConversationSession(
            session_id='test_session',
            participants=['user1', 'user2'],
            session_type=SessionType.MATCHMAKING
        )
        
        message = Message(
            message_id='msg1',
            sender_id='user1',
            sender_type=AgentType.USER_AVATAR,
            content='Hello!'
        )
        
        session.add_message(message)
        assert len(session.messages) == 1
        assert session.messages[0].content == 'Hello!'
    
    def test_session_termination(self):
        """Test session termination."""
        session = ConversationSession(
            session_id='test_session',
            participants=['user1', 'user2'],
            session_type=SessionType.MATCHMAKING
        )
        
        session.end_session()
        assert session.status == SessionStatus.COMPLETED
        assert session.end_time is not None
    
    def test_serialization(self):
        """Test session serialization and deserialization."""
        session = ConversationSession(
            session_id='test_session',
            participants=['user1', 'user2'],
            session_type=SessionType.MATCHMAKING
        )
        
        # Add a message
        message = Message(
            message_id='msg1',
            sender_id='user1',
            sender_type=AgentType.USER_AVATAR,
            content='Hello!'
        )
        session.add_message(message)
        
        # Test serialization
        session_dict = session.to_dict()
        assert session_dict['session_id'] == 'test_session'
        assert len(session_dict['messages']) == 1
        
        # Test deserialization
        restored_session = ConversationSession.from_dict(session_dict)
        assert restored_session.session_id == session.session_id
        assert len(restored_session.messages) == 1
        assert restored_session.messages[0].content == 'Hello!'


class TestScenario:
    """Test Scenario model."""
    
    def test_scenario_creation(self):
        """Test creating a scenario."""
        scenario = Scenario(
            scenario_id='scenario1',
            category=ScenarioCategory.FINANCIAL,
            title='Budget Planning',
            description='Plan a monthly budget together',
            difficulty_level=3,
            expected_duration=15
        )
        
        assert scenario.scenario_id == 'scenario1'
        assert scenario.category == ScenarioCategory.FINANCIAL
        assert scenario.difficulty_level == 3
    
    def test_cultural_adaptation(self):
        """Test scenario cultural adaptation."""
        scenario = Scenario(
            scenario_id='scenario1',
            category=ScenarioCategory.FAMILY,
            title='Family Planning',
            description='Discuss having children',
            difficulty_level=5,
            expected_duration=20,
            cultural_adaptations={
                'asian': {
                    'description': 'Discuss family planning with consideration for extended family',
                    'context': {'extended_family_involvement': True}
                }
            }
        )
        
        adapted = scenario.adapt_for_culture('asian')
        assert 'extended family' in adapted.description
        assert adapted.context['extended_family_involvement'] is True
        
        # Test with non-existent culture
        unchanged = scenario.adapt_for_culture('nonexistent')
        assert unchanged.description == scenario.description


class TestCompatibilityReport:
    """Test CompatibilityReport model."""
    
    def test_report_creation(self):
        """Test creating a compatibility report."""
        report = CompatibilityReport(
            report_id='report1',
            session_id='session1',
            user_ids=('user1', 'user2'),
            overall_score=0.8,
            confidence_level=0.9
        )
        
        assert report.report_id == 'report1'
        assert report.user_ids == ('user1', 'user2')
        assert report.overall_score == 0.8
    
    def test_add_scenario_result(self):
        """Test adding scenario results to report."""
        report = CompatibilityReport(
            report_id='report1',
            session_id='session1',
            user_ids=('user1', 'user2'),
            overall_score=0.0,
            confidence_level=0.0
        )
        
        result = ScenarioResult(
            scenario_id='scenario1',
            participants=['user1', 'user2'],
            collaboration_score=0.8,
            conflict_resolution_score=0.7,
            value_alignment_score=0.9,
            completion_time=15
        )
        
        report.add_scenario_result(result)
        
        assert len(report.scenario_results) == 1
        assert report.overall_score > 0.0  # Should be recalculated
        assert 'collaboration' in report.dimension_scores


class TestValidationFunctions:
    """Test validation functions."""
    
    def test_validate_personality_profile(self):
        """Test personality profile validation."""
        # Valid profile
        traits = PersonalityTraits(
            openness=0.8,
            conscientiousness=0.7,
            extraversion=0.6,
            agreeableness=0.9,
            neuroticism=0.3,
            values={'family': 0.9, 'career': 0.7, 'adventure': 0.5},
            communication_style=CommunicationStyle.DIRECT,
            conflict_resolution_style=ConflictResolutionStyle.COLLABORATING
        )
        
        preferences = UserPreferences(
            age_range=(25, 35),
            relationship_goals=['marriage']
        )
        
        profile = PersonalityProfile(
            user_id='test_user',
            personality_traits=traits,
            preferences=preferences
        )
        
        errors = validate_personality_profile(profile)
        assert len(errors) == 0
    
    def test_validate_user_profile(self):
        """Test user profile validation."""
        basic_info = BasicInfo(
            name='John Doe',
            age=30,
            location='New York'
        )
        
        profile = UserProfile(
            user_id='test_user',
            basic_info=basic_info
        )
        
        errors = validate_user_profile(profile)
        assert len(errors) == 0
        
        # Test invalid profile - Pydantic will catch these during creation
        # so we test the validation logic with edge cases that pass Pydantic
        edge_case_info = BasicInfo(
            name='   ',  # Whitespace only name (passes min_length but fails our validation)
            age=18,      # Minimum valid age
            location='New York'
        )
        
        edge_case_profile = UserProfile(
            user_id='test_user',
            basic_info=edge_case_info
        )
        
        errors = validate_user_profile(edge_case_profile)
        assert len(errors) > 0
        assert any('Name cannot be empty' in error for error in errors)