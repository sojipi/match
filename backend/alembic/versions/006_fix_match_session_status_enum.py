"""Fix match_session status enum type

Revision ID: 006_fix_match_session_status_enum
Revises: 005_add_match_session_model
Create Date: 2026-02-08 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005_add_match_session_model'
branch_labels = None
depends_on = None


def upgrade():
    # First, check if the column is using the wrong enum type and fix it
    # We need to:
    # 1. Alter the column to use string temporarily
    # 2. Drop the incorrect enum type if it exists
    # 3. Ensure the correct enum type exists
    # 4. Alter the column back to use the correct enum type

    # Step 1: Convert status column to varchar temporarily
    op.execute("ALTER TABLE match_sessions ALTER COLUMN status TYPE varchar(50)")

    # Step 2: Drop sessionstatus enum if it exists (only if not used by other tables)
    # We'll check if it's safe to drop by seeing if conversation_sessions uses it
    op.execute("""
        DO $$
        BEGIN
            -- Only drop sessionstatus if it exists and is not used by conversation_sessions
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sessionstatus') THEN
                -- Check if conversation_sessions.status is using sessionstatus enum
                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'conversation_sessions'
                    AND column_name = 'status'
                    AND udt_name = 'sessionstatus'
                ) THEN
                    -- Safe to drop
                    DROP TYPE sessionstatus;
                END IF;
            END IF;
        END $$;
    """)

    # Step 3: Ensure matchsessionstatus enum exists with correct values
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'matchsessionstatus') THEN
                CREATE TYPE matchsessionstatus AS ENUM ('SCHEDULED', 'ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED');
            END IF;
        END $$;
    """)

    # Step 4: Convert status column to use matchsessionstatus enum
    op.execute("ALTER TABLE match_sessions ALTER COLUMN status TYPE matchsessionstatus USING status::matchsessionstatus")

    # Set default value
    op.execute("ALTER TABLE match_sessions ALTER COLUMN status SET DEFAULT 'SCHEDULED'::matchsessionstatus")


def downgrade():
    # Convert back to varchar
    op.execute("ALTER TABLE match_sessions ALTER COLUMN status TYPE varchar(50)")
