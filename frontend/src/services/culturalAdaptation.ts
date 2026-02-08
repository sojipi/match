import { supportedLanguages, SupportedLanguage } from '../i18n/config';

/**
 * Cultural context types for content adaptation
 */
export type CulturalContext = 'western' | 'eastern' | 'middle-eastern' | 'latin-american';

/**
 * Personality assessment question adaptations by culture
 */
export interface CulturalQuestionAdaptation {
    originalQuestion: string;
    adaptedQuestion: string;
    culturalNotes?: string;
}

/**
 * Scenario adaptations by culture
 */
export interface CulturalScenarioAdaptation {
    scenarioId: string;
    culturalContext: CulturalContext;
    adaptedContent: {
        title: string;
        description: string;
        context: Record<string, any>;
    };
}

/**
 * Get cultural context for a language
 */
export const getCulturalContext = (language: SupportedLanguage): CulturalContext => {
    return supportedLanguages[language]?.culturalContext || 'western';
};

/**
 * Adapt personality assessment questions for cultural context
 */
export const adaptPersonalityQuestion = (
    questionId: string,
    originalText: string,
    culturalContext: CulturalContext
): string => {
    // Cultural adaptations for personality questions
    const adaptations: Record<string, Record<CulturalContext, string>> = {
        'extraversion_1': {
            western: 'I enjoy being the center of attention at social gatherings',
            eastern: 'I feel comfortable contributing to group discussions',
            'middle-eastern': 'I enjoy participating actively in family and social gatherings',
            'latin-american': 'I feel energized when surrounded by friends and family',
        },
        'independence_1': {
            western: 'I prefer making decisions independently',
            eastern: 'I value both personal judgment and group harmony in decisions',
            'middle-eastern': 'I consider family input when making important decisions',
            'latin-american': 'I balance personal goals with family expectations',
        },
        // Add more adaptations as needed
    };

    return adaptations[questionId]?.[culturalContext] || originalText;
};

/**
 * Adapt relationship scenarios for cultural context
 */
export const adaptScenario = (
    scenarioId: string,
    culturalContext: CulturalContext
): CulturalScenarioAdaptation | null => {
    const scenarioAdaptations: Record<string, Record<CulturalContext, any>> = {
        'financial_decision': {
            western: {
                title: 'Major Purchase Decision',
                description: 'You and your partner are considering buying a new car. How do you approach this decision?',
                context: {
                    decisionMakers: ['both partners'],
                    familyInvolvement: 'minimal',
                    financialApproach: 'individual budgets',
                },
            },
            eastern: {
                title: 'Family Financial Planning',
                description: 'You and your partner are considering a major purchase. How do you involve family in this decision?',
                context: {
                    decisionMakers: ['both partners', 'family elders'],
                    familyInvolvement: 'significant',
                    financialApproach: 'family consideration',
                },
            },
            'middle-eastern': {
                title: 'Household Investment Decision',
                description: 'You and your partner are planning a significant household investment. How do you approach this with family?',
                context: {
                    decisionMakers: ['both partners', 'extended family'],
                    familyInvolvement: 'high',
                    financialApproach: 'family-oriented',
                },
            },
            'latin-american': {
                title: 'Family Financial Commitment',
                description: 'You and your partner are considering a major expense. How do you balance personal and family needs?',
                context: {
                    decisionMakers: ['both partners', 'close family'],
                    familyInvolvement: 'moderate to high',
                    financialApproach: 'family-inclusive',
                },
            },
        },
        'family_conflict': {
            western: {
                title: 'Disagreement with In-Laws',
                description: 'You have a disagreement with your partner\'s parents about parenting styles. How do you handle it?',
                context: {
                    boundaryExpectation: 'clear boundaries',
                    conflictResolution: 'direct communication',
                    familyRole: 'advisory',
                },
            },
            eastern: {
                title: 'Family Harmony and Respect',
                description: 'There are different views between you and elder family members about family matters. How do you navigate this?',
                context: {
                    boundaryExpectation: 'flexible boundaries',
                    conflictResolution: 'indirect, respectful',
                    familyRole: 'significant authority',
                },
            },
            'middle-eastern': {
                title: 'Family Respect and Unity',
                description: 'You need to address different perspectives with elder family members. How do you maintain respect and unity?',
                context: {
                    boundaryExpectation: 'family-integrated',
                    conflictResolution: 'respectful mediation',
                    familyRole: 'central authority',
                },
            },
            'latin-american': {
                title: 'Family Connection and Understanding',
                description: 'You have different views from family members on an important matter. How do you maintain family harmony?',
                context: {
                    boundaryExpectation: 'close family ties',
                    conflictResolution: 'warm, diplomatic',
                    familyRole: 'influential',
                },
            },
        },
    };

    const adaptation = scenarioAdaptations[scenarioId]?.[culturalContext];
    if (!adaptation) return null;

    return {
        scenarioId,
        culturalContext,
        adaptedContent: adaptation,
    };
};

/**
 * Get culturally appropriate communication style descriptions
 */
export const getCommunicationStyleDescription = (
    style: string,
    culturalContext: CulturalContext
): string => {
    const descriptions: Record<string, Record<CulturalContext, string>> = {
        direct: {
            western: 'Direct and straightforward communication',
            eastern: 'Clear communication while maintaining harmony',
            'middle-eastern': 'Respectful and clear expression',
            'latin-american': 'Warm and expressive communication',
        },
        indirect: {
            western: 'Subtle and diplomatic communication',
            eastern: 'Harmonious and context-aware communication',
            'middle-eastern': 'Respectful and nuanced expression',
            'latin-american': 'Tactful and relationship-focused communication',
        },
    };

    return descriptions[style]?.[culturalContext] || style;
};

/**
 * Get culturally appropriate value descriptions
 */
export const getValueDescription = (
    value: string,
    culturalContext: CulturalContext
): string => {
    const descriptions: Record<string, Record<CulturalContext, string>> = {
        independence: {
            western: 'Personal autonomy and self-reliance',
            eastern: 'Balance between personal goals and group harmony',
            'middle-eastern': 'Personal growth within family structure',
            'latin-american': 'Individual expression within family bonds',
        },
        family: {
            western: 'Close family relationships and support',
            eastern: 'Family as central life priority and identity',
            'middle-eastern': 'Family honor and collective well-being',
            'latin-american': 'Strong family bonds and mutual support',
        },
        tradition: {
            western: 'Respect for heritage and customs',
            eastern: 'Deep reverence for ancestral wisdom',
            'middle-eastern': 'Preservation of cultural and religious traditions',
            'latin-american': 'Celebration of cultural heritage and customs',
        },
    };

    return descriptions[value]?.[culturalContext] || value;
};

/**
 * Validate cultural appropriateness of content
 */
export const validateCulturalAppropriateness = (
    content: string,
    culturalContext: CulturalContext
): { appropriate: boolean; suggestions?: string[] } => {
    // Cultural sensitivity checks
    const sensitivities: Record<CulturalContext, string[]> = {
        western: ['respect personal boundaries', 'acknowledge diversity'],
        eastern: ['respect hierarchy', 'maintain harmony', 'honor family'],
        'middle-eastern': ['respect religious values', 'honor family', 'maintain modesty'],
        'latin-american': ['value family bonds', 'respect traditions', 'warmth in communication'],
    };

    // Simple validation - in production, this would be more sophisticated
    const appropriate = true; // Placeholder
    const suggestions = sensitivities[culturalContext];

    return { appropriate, suggestions };
};

/**
 * Get date format for cultural context
 */
export const getDateFormat = (culturalContext: CulturalContext): string => {
    const formats: Record<CulturalContext, string> = {
        western: 'MM/DD/YYYY',
        eastern: 'YYYY/MM/DD',
        'middle-eastern': 'DD/MM/YYYY',
        'latin-american': 'DD/MM/YYYY',
    };

    return formats[culturalContext] || 'MM/DD/YYYY';
};

/**
 * Get time format for cultural context
 */
export const getTimeFormat = (culturalContext: CulturalContext): '12h' | '24h' => {
    const formats: Record<CulturalContext, '12h' | '24h'> = {
        western: '12h',
        eastern: '24h',
        'middle-eastern': '12h',
        'latin-american': '12h',
    };

    return formats[culturalContext] || '12h';
};
