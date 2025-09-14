import pytest
from httpx import AsyncClient
from app.main import app
from app.api.v1 import hands as hands_module

class InMemoryRepo:
    def __init__(self):
        self._store = {}

    async def save(self, hand):
        self._store[hand.hand_id] = hand

    async def get(self, hand_id):
        return self._store.get(hand_id)

    async def list(self, limit=50, offset=0):
        return list(self._store.values())

@pytest.fixture(autouse=True)
def override_repo():
    hands_module.get_repo = lambda: InMemoryRepo()
    yield

@pytest.mark.asyncio
async def test_create_and_get_hand():
    async with AsyncClient(app=app, base_url='http://test') as client:
        payload = {
            "hand_id": "00000000-0000-0000-0000-000000000001",
            "table_id": "T1",
            "created_at": "2025-09-14T12:00:00Z",
            "players": [
                {"player_id": "p1", "name": "Alice", "seat": 1, "stack": 1000, "hole_cards": ["Ah","Kd"]},
                {"player_id": "p2", "name": "Bob", "seat": 2, "stack": 1000, "hole_cards": ["2c","3d"]}
            ],
            "actions": [],
            "pot": 200,
            "winners": {},
            "community": {"flop":["3h","Kd","Qs"], "turn":["Td"], "river":["2s"]}
        }
        r = await client.post('/api/v1/hands', json=payload)
        assert r.status_code == 201
        assert r.headers.get('Location') == f"/api/v1/hands/{payload['hand_id']}"
        r2 = await client.get('/api/v1/hands')
        assert r2.status_code == 200
        assert any(h['hand_id']==payload['hand_id'] for h in r2.json())
