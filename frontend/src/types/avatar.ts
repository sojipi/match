/**
 * AI Avatar types
 */

export interface AIAvatar {
    id: string;
    user_id: string;
    name: string;
    description?: string;
    avatar_version: string;
    personality_traits: Record<string, any>;
    communication_patterns: Record<string, any>;
    response_style: Record<string, any>;
    conversation_skills: Record<string, any>;
    emotional_range: Record<string, any>;
    completeness_score: number;
    authenticity_score: number;
    consistency_score: number;
    status: string;
    improvement_areas: string[];
    suggested_actions: string[];
    training_iterations: number;
    last_training_date?: string;
    created_at: string;
    updated_at: string;
}

export interface AvatarCustomization {
    id: string;
    avatar_id: string;
    customization_type: string;
    field_name: string;
    original_value: any;
    custom_value: any;
    reason?: string;
    confidence: number;
    impact_score: number;
    is_active: boolean;
    created_at: string;
}

export interface AvatarCustomizationRequest {
    customization_type: string;
    field_name: string;
    custom_value: any;
    reason?: string;
}

export interface AvatarCompletenessAnalysis {
    overall_score: number;
    authenticity_score: number;
    consistency_score: number;
    areas: Record<string, {
        score: number;
        missing: string[];
        suggestions: string[];
    }>;
    improvement_areas: string[];
    suggested_actions: string[];
    training_status: {
        iterations: number;
        last_training?: string;
        status: string;
    };
}

export interface AvatarTrainingSession {
    id: string;
    avatar_id: string;
    training_type: string;
    trigger_reason: string;
    success: boolean;
    error_message?: string;
    started_at: string;
    completed_at?: string;
    duration_seconds?: number;
}

export interface AvatarVisualization {
    trait: string;
    score: number;
    label: string;
    description: string;
    color: string;
    category: 'personality' | 'communication' | 'emotional' | 'skills';
}

export interface AvatarImprovementSuggestion {
    area: string;
    priority: 'high' | 'medium' | 'low';
    action: string;
    description: string;
    estimated_impact: number;
}