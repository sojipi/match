-- Add missing columns to scenario_templates table

-- Add setup_prompt column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'scenario_templates' 
        AND column_name = 'setup_prompt'
    ) THEN
        ALTER TABLE scenario_templates 
        ADD COLUMN setup_prompt TEXT;
        
        -- Set default value for existing rows
        UPDATE scenario_templates 
        SET setup_prompt = description 
        WHERE setup_prompt IS NULL;
        
        -- Make it NOT NULL after setting defaults
        ALTER TABLE scenario_templates 
        ALTER COLUMN setup_prompt SET NOT NULL;
    END IF;
END $$;

-- Verify the column exists
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'scenario_templates'
AND column_name = 'setup_prompt';
