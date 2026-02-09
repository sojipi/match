-- Create scenario_templates table
CREATE TABLE IF NOT EXISTS scenario_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    difficulty_level INTEGER DEFAULT 2,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    context TEXT,
    setup_prompt TEXT NOT NULL,
    estimated_duration_minutes INTEGER DEFAULT 15,
    participant_roles JSONB DEFAULT '[]'::jsonb,
    success_criteria JSONB DEFAULT '[]'::jsonb,
    initial_prompt TEXT,
    guiding_questions JSONB DEFAULT '[]'::jsonb,
    escalation_prompts JSONB DEFAULT '[]'::jsonb,
    resolution_prompts JSONB DEFAULT '[]'::jsonb,
    personality_dimensions JSONB DEFAULT '[]'::jsonb,
    value_dimensions JSONB DEFAULT '[]'::jsonb,
    skill_dimensions JSONB DEFAULT '[]'::jsonb,
    cultural_adaptations JSONB DEFAULT '{}'::jsonb,
    age_appropriateness VARCHAR(50) DEFAULT 'all',
    relationship_stage VARCHAR(50) DEFAULT 'early',
    language_variants JSONB DEFAULT '{}'::jsonb,
    usage_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    user_rating FLOAT DEFAULT 0.0,
    completion_rate FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    is_approved BOOLEAN DEFAULT TRUE,
    requires_moderation BOOLEAN DEFAULT FALSE,
    content_warnings JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    keywords JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_scenario_templates_name ON scenario_templates(name);
CREATE INDEX IF NOT EXISTS idx_scenario_templates_category ON scenario_templates(category);

-- Create simulation_sessions table
CREATE TABLE IF NOT EXISTS simulation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user1_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user2_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    match_id UUID REFERENCES matches(id) ON DELETE CASCADE,
    scenario_template_id UUID NOT NULL REFERENCES scenario_templates(id),
    scenario_instance_data JSONB DEFAULT '{}'::jsonb,
    session_title VARCHAR(200),
    session_description TEXT,
    status VARCHAR(50) DEFAULT 'scheduled',
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    max_duration_minutes INTEGER DEFAULT 30,
    is_public BOOLEAN DEFAULT FALSE,
    allow_observers BOOLEAN DEFAULT FALSE,
    auto_guidance_enabled BOOLEAN DEFAULT TRUE,
    cultural_adaptation VARCHAR(50),
    language VARCHAR(10) DEFAULT 'en',
    current_phase VARCHAR(50),
    phase_start_time TIMESTAMP WITH TIME ZONE,
    turn_count INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    engagement_score FLOAT DEFAULT 0.0,
    scenario_completion_score FLOAT,
    collaboration_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_simulation_sessions_user1 ON simulation_sessions(user1_id);
CREATE INDEX IF NOT EXISTS idx_simulation_sessions_user2 ON simulation_sessions(user2_id);
CREATE INDEX IF NOT EXISTS idx_simulation_sessions_match ON simulation_sessions(match_id);
CREATE INDEX IF NOT EXISTS idx_simulation_sessions_scenario ON simulation_sessions(scenario_template_id);

-- Create simulation_messages table
CREATE TABLE IF NOT EXISTS simulation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES simulation_sessions(id) ON DELETE CASCADE,
    sender_id VARCHAR(100) NOT NULL,
    sender_type VARCHAR(50) NOT NULL,
    sender_name VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    scenario_phase VARCHAR(50),
    turn_number INTEGER DEFAULT 0,
    is_highlighted BOOLEAN DEFAULT FALSE,
    emotion_indicators JSONB DEFAULT '[]'::jsonb,
    compatibility_impact FLOAT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_simulation_messages_session ON simulation_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_simulation_messages_timestamp ON simulation_messages(timestamp);

-- Create scenario_results table
CREATE TABLE IF NOT EXISTS scenario_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_session_id UUID NOT NULL REFERENCES simulation_sessions(id) ON DELETE CASCADE,
    scenario_template_id UUID NOT NULL REFERENCES scenario_templates(id),
    overall_success_score FLOAT DEFAULT 0.0,
    scenario_completion_rate FLOAT DEFAULT 0.0,
    collaboration_score FLOAT DEFAULT 0.0,
    communication_score FLOAT DEFAULT 0.0,
    conflict_resolution_score FLOAT DEFAULT 0.0,
    value_alignment_score FLOAT DEFAULT 0.0,
    problem_solving_score FLOAT DEFAULT 0.0,
    empathy_score FLOAT DEFAULT 0.0,
    scenario_objectives_met JSONB DEFAULT '[]'::jsonb,
    key_decisions_made JSONB DEFAULT '[]'::jsonb,
    conflict_points JSONB DEFAULT '[]'::jsonb,
    resolution_strategies JSONB DEFAULT '[]'::jsonb,
    strengths_identified JSONB DEFAULT '[]'::jsonb,
    challenges_identified JSONB DEFAULT '[]'::jsonb,
    compatibility_insights JSONB DEFAULT '[]'::jsonb,
    behavioral_patterns JSONB DEFAULT '[]'::jsonb,
    relationship_recommendations JSONB DEFAULT '[]'::jsonb,
    future_scenario_suggestions JSONB DEFAULT '[]'::jsonb,
    skill_development_areas JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_scenario_results_session ON scenario_results(simulation_session_id);
CREATE INDEX IF NOT EXISTS idx_scenario_results_template ON scenario_results(scenario_template_id);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_scenario_templates_updated_at BEFORE UPDATE ON scenario_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_simulation_sessions_updated_at BEFORE UPDATE ON simulation_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
