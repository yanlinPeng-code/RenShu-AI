import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from sqlalchemy import text
from app.src.common.config.prosgresql_config import async_db_manager

async def cleanup_duplicates():
    print("Starting duplicate provider cleanup...")
    await async_db_manager.init()
    
    async with async_db_manager.async_engine.begin() as conn:
        try:
            # 1. Identify duplicates for 'xai' (case-insensitive)
            # Find all providers where lower(name) = 'xai'
            res = await conn.execute(text("SELECT id, name FROM system_model_providers WHERE lower(name) = 'xai'"))
            providers = res.fetchall()
            
            if len(providers) <= 1:
                print("No duplicates found or only one instance exists.")
                return

            print(f"Found {len(providers)} instances of 'xAI': {providers}")
            
            # Strategy: Keep the first one, delete others.
            # Ideally, we should check which one has models attached, but for simplicity in this fix script:
            # We will migrate all models from the "to-be-deleted" providers to the "kept" provider.
            
            keep_id = providers[0][0]
            keep_name = providers[0][1]
            print(f"Keeping provider: {keep_name} ({keep_id})")
            
            for i in range(1, len(providers)):
                del_id = providers[i][0]
                del_name = providers[i][1]
                print(f"Processing duplicate to remove: {del_name} ({del_id})")
                
                # 1. Migrate Models
                # Update system_model_definitions set provider_id = keep_id where provider_id = del_id
                # Handle conflict: if keep_id already has a model with same name, we can't just update.
                # For this specific case (xAI), models are likely identical.
                
                # Check for model conflicts
                models_to_move = await conn.execute(text("SELECT id, model_name FROM system_model_definitions WHERE provider_id = :del_id"), {"del_id": del_id})
                for model in models_to_move.fetchall():
                    m_id = model[0]
                    m_name = model[1]
                    
                    # Check if keep_id has this model
                    exists = await conn.execute(text("SELECT id FROM system_model_definitions WHERE provider_id = :keep_id AND model_name = :m_name"), {"keep_id": keep_id, "m_name": m_name})
                    if exists.scalar():
                        # Conflict: keep_id already has this model.
                        # Delete the duplicate model from the provider we are about to delete
                        print(f"  - Model '{m_name}' exists in target. Deleting duplicate model.")
                        await conn.execute(text("DELETE FROM system_model_definitions WHERE id = :id"), {"id": m_id})
                    else:
                        # No conflict: Move it
                        print(f"  - Moving model '{m_name}' to target provider.")
                        await conn.execute(text("UPDATE system_model_definitions SET provider_id = :keep_id WHERE id = :id"), {"keep_id": keep_id, "id": m_id})

                # 2. Migrate User Configs
                # Similar logic for user_provider_configs
                configs_to_move = await conn.execute(text("SELECT id, user_id FROM user_provider_configs WHERE provider_id = :del_id"), {"del_id": del_id})
                for cfg in configs_to_move.fetchall():
                    c_id = cfg[0]
                    u_id = cfg[1]
                    
                    exists = await conn.execute(text("SELECT id FROM user_provider_configs WHERE provider_id = :keep_id AND user_id = :u_id"), {"keep_id": keep_id, "u_id": u_id})
                    if exists.scalar():
                        print(f"  - User config for user {u_id} exists in target. Deleting duplicate config.")
                        await conn.execute(text("DELETE FROM user_provider_configs WHERE id = :id"), {"id": c_id})
                    else:
                        print(f"  - Moving user config for user {u_id} to target provider.")
                        await conn.execute(text("UPDATE user_provider_configs SET provider_id = :keep_id WHERE id = :id"), {"keep_id": keep_id, "id": c_id})

                # 3. Delete the Provider
                print(f"  - Deleting provider {del_name} ({del_id})")
                await conn.execute(text("DELETE FROM system_model_providers WHERE id = :id"), {"id": del_id})
                
            print("Cleanup completed successfully.")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            raise

    await async_db_manager.close()

if __name__ == "__main__":
    asyncio.run(cleanup_duplicates())
