import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from sqlalchemy import text
from app.src.common.config.prosgresql_config import async_db_manager

async def drop_constraint():
    await async_db_manager.init()
    async with async_db_manager.async_engine.begin() as conn:
        try:
            # Drop the problematic global unique constraint
            await conn.execute(text("ALTER TABLE model_providers DROP CONSTRAINT IF EXISTS model_providers_name_key"))
            print("Successfully dropped constraint 'model_providers_name_key'")
            
            # Drop the new constraint if it exists (to ensure clean slate or if migration failed previously)
            await conn.execute(text("ALTER TABLE model_providers DROP CONSTRAINT IF EXISTS uq_model_providers_user_name"))
            print("Successfully dropped constraint 'uq_model_providers_user_name'")
            
            # Add the new composite unique constraint
            # Note: We do this via SQL here because Alembic/SQLModel auto-migration might not be set up to run immediately
            # or might have issues if data already violates the new constraint (though it shouldn't if we just dropped the stricter one)
            await conn.execute(text("ALTER TABLE model_providers ADD CONSTRAINT uq_model_providers_user_name UNIQUE (user_id, name)"))
            print("Successfully added constraint 'uq_model_providers_user_name'")
            
        except Exception as e:
            print(f"Error executing database operations: {e}")

    await async_db_manager.close()

if __name__ == "__main__":
    asyncio.run(drop_constraint())
