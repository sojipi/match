-- Quick fix for conversation_messages table
-- Run this SQL in your PostgreSQL database

-- Add sender_id column if it doesn't exist
ALTER TABLE conversation_messages
ADD COLUMN IF NOT EXISTS sender_id VARCHAR(100) NOT NULL DEFAULT '';

-- Verify the column was added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'conversation_messages'
ORDER BY ordinal_position;
