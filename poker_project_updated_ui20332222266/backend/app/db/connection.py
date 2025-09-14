import asyncpg
import os
_pool = None

async def init_db_pool(dsn):
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn, min_size=1, max_size=10)
    return _pool

def get_db_pool():
    global _pool
    if _pool is None:
        raise RuntimeError("DB pool not initialized")
    return _pool

async def close_db_pool():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
