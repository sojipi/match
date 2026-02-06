-- Fix conversation_messages table schema
-- Add missing sender_id column if it doesn't exist

DO $$
BEGIN
    -- Check if sender_id column exists
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'conversation_messages'
        AND column_name = 'sender_id'
    ) THEN
        -- Add sender_id column
        ALTER TABLE conversation_messages
        ADD COLUMN sender_id VARCHAR(100) NOT NULL DEFAULT '';

        RAISE NOTICE 'Added sender_id column to conversation_messages';
    ELSE
        RAISE NOTICE 'sender_id column already exists';
    END IF;
END $$;

-- Show current table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'conversation_messages'
ORDER BY ordinal_position;
