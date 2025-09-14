from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional

@dataclass
class PlayerSnapshot:
    player_id: str
    name: str
    seat: int
    stack: int
    hole_cards: List[str] = field(default_factory=list)

@dataclass
class Action:
    timestamp: str
    round: str
    player_id: str
    action: str
    amount: int = 0

@dataclass
class Hand:
    hand_id: str
    table_id: str
    created_at: str
    players: List[PlayerSnapshot]
    actions: List[Action]
    pot: int
    winners: Dict[str,int] = field(default_factory=dict)
    community: Optional[Dict[str, List[str]]] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)
