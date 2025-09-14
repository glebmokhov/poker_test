import json
from app.repositories.base import HandRepository
from app.domain.models import Hand, PlayerSnapshot, Action
import asyncpg

def _dict_to_hand(d):
    # Convert stored dict to Hand dataclass-like dict
    return d

class PostgresHandRepository(HandRepository):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def save(self, hand: Hand):
        payload = hand
        try:
            if hasattr(hand, "to_dict"):
                payload = hand.to_dict()
        except Exception:
            payload = hand
        hand_id = payload.get("hand_id")
        table_id = payload.get("table_id")
        created_at = payload.get("created_at")
        async with self.pool.acquire() as conn:
            await conn.execute(
                \"\"\"
                INSERT INTO hands (hand_id, table_id, created_at, payload)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (hand_id) DO UPDATE
                SET table_id = EXCLUDED.table_id,
                    created_at = EXCLUDED.created_at,
                    payload = EXCLUDED.payload
                \"\"\",
                hand_id, table_id, created_at, json.dumps(payload)
            )


    async def get(self, hand_id: str):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT payload FROM hands WHERE hand_id=$1", hand_id)
            if not row:
                return None
            return json.loads(row["payload"])

    async def list(self, limit=50, offset=0):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT payload FROM hands ORDER BY created_at DESC LIMIT $1 OFFSET $2", limit, offset)
            return [json.loads(r["payload"]) for r in rows]
