"""
Cultural Adaptation Service

Provides cultural adaptation for personality assessments, scenarios,
and AI interactions based on user's cultural background.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class CulturalContext(str, Enum):
    """Cultural context types"""
    WESTERN = "western"
    EASTERN = "eastern"
    MIDDLE_EASTERN = "middle-eastern"
    LATIN_AMERICAN = "latin-american"


@dataclass
class CulturalAdaptation:
    """Cultural adaptation data"""
    original_content: str
    adapted_content: str
    cultural_context: CulturalContext
    adaptation_notes: Optional[str] = None


class CulturalAdaptationService:
    """Service for adapting content to cultural contexts"""
    
    # Language to cultural context mapping
    LANGUAGE_CULTURE_MAP = {
        "en": CulturalContext.WESTERN,
        "es": CulturalContext.LATIN_AMERICAN,
        "fr": CulturalContext.WESTERN,
        "de": CulturalContext.WESTERN,
        "zh": CulturalContext.EASTERN,
        "ja": CulturalContext.EASTERN,
        "ar": CulturalContext.MIDDLE_EASTERN,
        "ko": CulturalContext.EASTERN,
        "pt": CulturalContext.LATIN_AMERICAN,
    }
    
    def __init__(self):
        """Initialize cultural adaptation service"""
        self.personality_adaptations = self._load_personality_adaptations()
        self.scenario_adaptations = self._load_scenario_adaptations()
    
    def get_cultural_context(self, language: str) -> CulturalContext:
        """Get cultural context for a language"""
        return self.LANGUAGE_CULTURE_MAP.get(language, CulturalContext.WESTERN)
    
    def adapt_personality_question(
        self,
        question_id: str,
        original_text: str,
        cultural_context: CulturalContext
    ) -> str:
        """
        Adapt personality assessment question for cultural context
        
        Args:
            question_id: Unique identifier for the question
            original_text: Original question text
            cultural_context: Target cultural context
            
        Returns:
            Culturally adapted question text
        """
        adaptations = self.personality_adaptations.get(question_id, {})
        return adaptations.get(cultural_context, original_text)
    
    def adapt_scenario(
        self,
        scenario_id: str,
        cultural_context: CulturalContext
    ) -> Optional[Dict[str, Any]]:
        """
        Adapt relationship scenario for cultural context
        
        Args:
            scenario_id: Unique identifier for the scenario
            cultural_context: Target cultural context
            
        Returns:
            Adapted scenario data or None if not found
        """
        scenarios = self.scenario_adaptations.get(scenario_id, {})
        return scenarios.get(cultural_context)
    
    def adapt_ai_prompt(
        self,
        base_prompt: str,
        cultural_context: CulturalContext,
        personality_traits: Dict[str, float]
    ) -> str:
        """
        Adapt AI agent prompt for cultural context
        
        Args:
            base_prompt: Base prompt template
            cultural_context: Target cultural context
            personality_traits: User's personality traits
            
        Returns:
            Culturally adapted prompt
        """
        cultural_guidelines = self._get_cultural_guidelines(cultural_context)
        
        adapted_prompt = f"""{base_prompt}

Cultural Context: {cultural_context.value}
Cultural Guidelines:
{cultural_guidelines}

When responding, ensure your communication style aligns with these cultural expectations
while maintaining authenticity to the personality traits provided.
"""
        return adapted_prompt
    
    def validate_cultural_appropriateness(
        self,
        content: str,
        cultural_context: CulturalContext
    ) -> Dict[str, Any]:
        """
        Validate if content is culturally appropriate
        
        Args:
            content: Content to validate
            cultural_context: Cultural context to validate against
            
        Returns:
            Validation result with suggestions
        """
        sensitivities = self._get_cultural_sensitivities(cultural_context)
        
        # Simple validation - in production, use NLP models
        issues = []
        suggestions = []
        
        # Check for common cultural sensitivity issues
        if cultural_context == CulturalContext.EASTERN:
            if "independent" in content.lower() and "family" not in content.lower():
                suggestions.append("Consider mentioning family harmony alongside independence")
        
        if cultural_context == CulturalContext.MIDDLE_EASTERN:
            if "tradition" not in content.lower() and "modern" in content.lower():
                suggestions.append("Balance modern concepts with respect for tradition")
        
        return {
            "appropriate": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "cultural_sensitivities": sensitivities
        }
    
    def get_communication_style_description(
        self,
        style: str,
        cultural_context: CulturalContext
    ) -> str:
        """Get culturally appropriate communication style description"""
        descriptions = {
            "direct": {
                CulturalContext.WESTERN: "Direct and straightforward communication",
                CulturalContext.EASTERN: "Clear communication while maintaining harmony",
                CulturalContext.MIDDLE_EASTERN: "Respectful and clear expression",
                CulturalContext.LATIN_AMERICAN: "Warm and expressive communication",
            },
            "indirect": {
                CulturalContext.WESTERN: "Subtle and diplomatic communication",
                CulturalContext.EASTERN: "Harmonious and context-aware communication",
                CulturalContext.MIDDLE_EASTERN: "Respectful and nuanced expression",
                CulturalContext.LATIN_AMERICAN: "Tactful and relationship-focused communication",
            },
        }
        
        return descriptions.get(style, {}).get(cultural_context, style)
    
    def _load_personality_adaptations(self) -> Dict[str, Dict[CulturalContext, str]]:
        """Load personality question adaptations"""
        return {
            "extraversion_1": {
                CulturalContext.WESTERN: "I enjoy being the center of attention at social gatherings",
                CulturalContext.EASTERN: "I feel comfortable contributing to group discussions",
                CulturalContext.MIDDLE_EASTERN: "I enjoy participating actively in family and social gatherings",
                CulturalContext.LATIN_AMERICAN: "I feel energized when surrounded by friends and family",
            },
            "independence_1": {
                CulturalContext.WESTERN: "I prefer making decisions independently",
                CulturalContext.EASTERN: "I value both personal judgment and group harmony in decisions",
                CulturalContext.MIDDLE_EASTERN: "I consider family input when making important decisions",
                CulturalContext.LATIN_AMERICAN: "I balance personal goals with family expectations",
            },
            "family_values_1": {
                CulturalContext.WESTERN: "I maintain close relationships with my family",
                CulturalContext.EASTERN: "Family is the foundation of my identity and decisions",
                CulturalContext.MIDDLE_EASTERN: "Family honor and unity are my highest priorities",
                CulturalContext.LATIN_AMERICAN: "Family bonds are central to my happiness and life",
            },
        }
    
    def _load_scenario_adaptations(self) -> Dict[str, Dict[CulturalContext, Dict[str, Any]]]:
        """Load scenario adaptations"""
        return {
            "financial_decision": {
                CulturalContext.WESTERN: {
                    "title": "Major Purchase Decision",
                    "description": "You and your partner are considering buying a new car. How do you approach this decision?",
                    "context": {
                        "decision_makers": ["both partners"],
                        "family_involvement": "minimal",
                        "financial_approach": "individual budgets",
                    },
                },
                CulturalContext.EASTERN: {
                    "title": "Family Financial Planning",
                    "description": "You and your partner are considering a major purchase. How do you involve family in this decision?",
                    "context": {
                        "decision_makers": ["both partners", "family elders"],
                        "family_involvement": "significant",
                        "financial_approach": "family consideration",
                    },
                },
                CulturalContext.MIDDLE_EASTERN: {
                    "title": "Household Investment Decision",
                    "description": "You and your partner are planning a significant household investment. How do you approach this with family?",
                    "context": {
                        "decision_makers": ["both partners", "extended family"],
                        "family_involvement": "high",
                        "financial_approach": "family-oriented",
                    },
                },
                CulturalContext.LATIN_AMERICAN: {
                    "title": "Family Financial Commitment",
                    "description": "You and your partner are considering a major expense. How do you balance personal and family needs?",
                    "context": {
                        "decision_makers": ["both partners", "close family"],
                        "family_involvement": "moderate to high",
                        "financial_approach": "family-inclusive",
                    },
                },
            },
        }
    
    def _get_cultural_guidelines(self, cultural_context: CulturalContext) -> str:
        """Get cultural communication guidelines"""
        guidelines = {
            CulturalContext.WESTERN: """
- Value individual autonomy and personal boundaries
- Direct communication is generally preferred
- Personal achievement and self-expression are important
- Balance independence with relationship needs
""",
            CulturalContext.EASTERN: """
- Prioritize group harmony and collective well-being
- Indirect communication to maintain face and respect
- Family and community are central to identity
- Balance personal desires with group expectations
""",
            CulturalContext.MIDDLE_EASTERN: """
- Show deep respect for family and tradition
- Honor and reputation are highly valued
- Communication should be respectful and modest
- Family involvement in major decisions is expected
""",
            CulturalContext.LATIN_AMERICAN: """
- Emphasize warmth and personal connections
- Family bonds are extremely important
- Expressive and emotional communication is valued
- Balance personal goals with family obligations
""",
        }
        
        return guidelines.get(cultural_context, guidelines[CulturalContext.WESTERN])
    
    def _get_cultural_sensitivities(self, cultural_context: CulturalContext) -> List[str]:
        """Get cultural sensitivities to be aware of"""
        sensitivities = {
            CulturalContext.WESTERN: [
                "Respect personal boundaries",
                "Acknowledge diversity",
                "Value individual choice",
            ],
            CulturalContext.EASTERN: [
                "Respect hierarchy and elders",
                "Maintain harmony",
                "Honor family obligations",
                "Preserve face and dignity",
            ],
            CulturalContext.MIDDLE_EASTERN: [
                "Respect religious values",
                "Honor family and tradition",
                "Maintain modesty",
                "Preserve family honor",
            ],
            CulturalContext.LATIN_AMERICAN: [
                "Value family bonds",
                "Respect traditions",
                "Warmth in communication",
                "Personal relationships matter",
            ],
        }
        
        return sensitivities.get(cultural_context, [])


# Global service instance
cultural_adaptation_service = CulturalAdaptationService()
