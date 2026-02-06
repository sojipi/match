/**
 * Types for live AI matching theater interface
 */

export interface MatchSession {
    session_id: string;
    match_id: string;
    user1_id: string;
    user2_id: string;
    session_type: 'conversation' | 'simulation' | 'speed_chat';
    status: 'waiting' | 'active' | 'completed' | 'terminated';
    start_time?: string;
    end_time?: string;
    live_compatibility_score: number;
    viewer_count: number;
    final_compatibility_score?: number;
}

export interface ConversationMessage {
    message_id: string;
    session_id: string;
    sender_type: 'user_avatar' | 'matchmaker_agent' | 'system';
    sender_name: string;
    content: string;
    message_type: 'text' | 'emotion' | 'action' | 'system_notification';
    emotion_indicators: string[];
    compatibility_impact?: number;
    is_highlighted: boolean;
    timestamp: string;
}

export interface CompatibilityUpdate {
    type: 'compatibility_update';
    session_id: string;
    overall_score: number;
    dimension_scores: {
        personality: number;
        communication: number;
        values: number;
        lifestyle: number;
    };
    trending_direction: 'improving' | 'declining' | 'stable';
    key_insights: string[];
    conversation_highlights: ConversationHighlight[];
    recent_highlight?: {
        message_id: string;
        reason: string;
        impact: number;
    };
    timestamp: string;
}

export interface ConversationHighlight {
    message_id: string;
    highlight: string;
    impact: number;
}

export interface UserAvatar {
    avatar_id: string;
    user_id: string;
    name: string;
    personality_traits: Record<string, any>;
    avatar_image?: string;
    status: 'active' | 'inactive' | 'training';
}

export interface WebSocketMessage {
    type: string;
    timestamp: string;
    [key: string]: any;
}

export interface SessionViewer {
    user_id: string;
    user_name: string;
    connected_at: string;
}

export interface UserFeedback {
    feedback_id: string;
    user_id: string;
    session_id: string;
    feedback_type: 'guidance' | 'reaction' | 'rating';
    content: string;
    target_avatar_id?: string;
    timestamp: string;
}

export interface UserReaction {
    reaction_id: string;
    user_id: string;
    user_name: string;
    message_id: string;
    reaction_type: 'like' | 'love' | 'concern' | 'laugh' | 'surprise';
    timestamp: string;
}

export interface TheaterControls {
    canProvideGuidance: boolean;
    canReact: boolean;
    canEndSession: boolean;
    isSessionOwner: boolean;
}

export interface CompatibilityMetrics {
    overall_score: number;
    dimension_scores: {
        personality: number;
        communication: number;
        values: number;
        lifestyle: number;
    };
    trend_data: Array<{
        timestamp: string;
        score: number;
    }>;
    insights: string[];
    strengths: string[];
    challenges: string[];
}

// WebSocket event types
export type WebSocketEventType =
    | 'connection_established'
    | 'user_joined'
    | 'user_left'
    | 'ai_message'
    | 'compatibility_update'
    | 'session_status_change'
    | 'user_reaction'
    | 'user_provided_feedback'
    | 'conversation_starting'
    | 'feedback_received'
    | 'guidance_sent'
    | 'gemini_quota_exceeded'
    | 'error'
    | 'ping'
    | 'pong';

export interface WebSocketEvent {
    type: WebSocketEventType;
    timestamp: string;
    [key: string]: any;
}

// Theater UI state
export interface TheaterState {
    isConnected: boolean;
    connectionError?: string;
    session?: MatchSession;
    messages: ConversationMessage[];
    compatibility: CompatibilityMetrics;
    viewers: SessionViewer[];
    userReactions: UserReaction[];
    isLoading: boolean;
    showCompatibilityPanel: boolean;
    showViewersPanel: boolean;
    showCompletionDialog: boolean;
    showQuotaExceededDialog: boolean;
    quotaErrorDetails?: any;
    selectedMessage?: string;
}

// Theater actions
export interface TheaterActions {
    sendFeedback: (feedback: Partial<UserFeedback>) => void;
    sendReaction: (messageId: string, reactionType: string) => void;
    sendGuidance: (avatarId: string, instruction: string) => void;
    toggleCompatibilityPanel: () => void;
    toggleViewersPanel: () => void;
    startConversation: () => void;
    endSession: () => void;
    requestCompatibilityUpdate: () => void;
}