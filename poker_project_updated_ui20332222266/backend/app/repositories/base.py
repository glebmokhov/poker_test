from typing import List, Optional
from app.domain.models import Hand

class HandRepository:
    async def save(self, hand: Hand) -> None:
        raise NotImplementedError

    async def get(self, hand_id: str) -> Optional[Hand]:
        raise NotImplementedError

    async def list(self, limit: int = 50, offset: int = 0) -> List[Hand]:
        raise NotImplementedError
