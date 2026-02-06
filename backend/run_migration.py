import asyncio
from sqlalchemy import text
from app.core.database import engine

async def migrate():
    async with engine.begin() as conn:
        try:
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='gemini_api_key'"
            ))
            if result.fetchone():
                print('✅ Column gemini_api_key already exists')
            else:
                await conn.execute(text("ALTER TABLE users ADD COLUMN gemini_api_key VARCHAR(255)"))
                print('✅ Column gemini_api_key added successfully')
        except Exception as e:
            print(f'❌ Error: {e}')

asyncio.run(migrate())