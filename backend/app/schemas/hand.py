from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class PlayerSnapshotSchema(BaseModel):
    player_id: str
    name: str
    seat: int
    stack: int
    hole_cards: List[str] = []

class ActionSchema(BaseModel):
    timestamp: datetime
    round: str
    player_id: str
    action: str
    amount: int = 0

class CommunitySchema(BaseModel):
    flop: Optional[List[str]] = None
    turn: Optional[List[str]] = None
    river: Optional[List[str]] = None

class HandSchema(BaseModel):
    hand_id: str
    table_id: str
    created_at: datetime
    players: List[PlayerSnapshotSchema]
    actions: List[ActionSchema]
    pot: int
    winners: Dict[str, int] = {}
    community: Optional[CommunitySchema] = None
