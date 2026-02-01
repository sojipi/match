-- Initialize AI Matchmaker database
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE ai_matchmaker'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ai_matchmaker');

-- Connect to the database
\c ai_matchmaker;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
DO $$ BEGIN
    CREATE TYPE match_status AS ENUM ('pending', 'mutual', 'expired', 'blocked');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE interest_level AS ENUM ('like', 'pass', 'super_like');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE session_type AS ENUM ('conversation', 'simulation', 'speed_chat');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE session_status AS ENUM ('waiting', 'active', 'completed', 'terminated');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE agent_type AS ENUM ('user_avatar', 'matchmaker_agent', 'system');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE message_type AS ENUM ('text', 'emotion', 'action', 'system_notification');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance (will be created by SQLAlchemy, but good to have)
-- These will be created automatically by the application