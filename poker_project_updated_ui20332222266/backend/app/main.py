from fastapi import FastAPI
from app.api.v1.hands import router as hands_router
from app.db.connection import init_db_pool, close_db_pool, get_db_pool
import asyncio
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Poker API")

# allow frontend origin to call API
_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hands_router)

async def ensure_db_ready(dsn, attempts=20, wait=1.0):
    # Attempt to init pool; retry until DB is ready
    for i in range(attempts):
        try:
            await init_db_pool(dsn)
            # create table if not exists
            pool = get_db_pool()
            async with pool.acquire() as conn:
                await conn.execute('''
                CREATE TABLE IF NOT EXISTS hands (
                    hand_id UUID PRIMARY KEY,
                    table_id TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL,
                    payload JSONB NOT NULL
                );
                ''')
            return
        except Exception as e:
            if i == attempts-1:
                raise
            await asyncio.sleep(wait)

@app.on_event('startup')
async def startup():
    dsn = os.getenv('DATABASE_URL', 'postgresql://postgres:password@db:5432/pokerdb')
    await ensure_db_ready(dsn)

@app.on_event('shutdown')
async def shutdown():
    await close_db_pool()
