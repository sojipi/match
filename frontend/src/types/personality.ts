/**
 * Personality assessment types
 */

export interface PersonalityQuestion {
    id: string;
    category: string;
    question: string;
    question_type: 'scale' | 'multiple_choice' | 'ranking';
    options?: string[];
    scale_min?: number;
    scale_max?: number;
    scale_labels?: Record<string, string>;
}

export interface PersonalityAnswer {
    question_id: string;
    answer: any; // Can be number, string, or array
    confidence?: number;
}

export interface PersonalityAssessmentRequest {
    answers: PersonalityAnswer[];
    assessment_version?: string;
}

export interface PersonalityProfile {
    id: string;
    user_id: string;
    openness?: number;
    conscientiousness?: number;
    extraversion?: number;
    agreeableness?: number;
    neuroticism?: number;
    values: Record<string, any>;
    communication_style?: string;
    conflict_resolution_style?: string;
    completeness_score: number;
    assessment_version?: string;
    created_at: string;
    updated_at: string;
}

export interface PersonalityInsight {
    trait: string;
    score: number;
    description: string;
    confidence: number;
}

export interface AssessmentProgress {
    current_step: number;
    total_steps: number;
    completion_percentage: number;
    estimated_time_remaining: number;
    insights: PersonalityInsight[];
}

export interface PersonalityVisualization {
    trait: string;
    score: number;
    label: string;
    description: string;
    color: string;
}