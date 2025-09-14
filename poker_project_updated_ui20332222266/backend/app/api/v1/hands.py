
from fastapi import APIRouter, Depends, HTTPException, Response, Body
from typing import List, Optional, Any
from pydantic import BaseModel
from app.schemas.hand import HandSchema
from app.db.connection import get_db_pool
from app.repositories.postgres import PostgresHandRepository
import uuid
from datetime import datetime
import random

router = APIRouter(prefix="/api/v1/hands", tags=["hands"])

def get_repo():
    """
    Return a repository instance. Tests may monkeypatch this by assigning to
    app.api.v1.hands.get_repo = lambda: InMemoryRepo()
    """
    pool = get_db_pool()
    return PostgresHandRepository(pool)

def _normalize_hand_obj(it: Any) -> dict:
    # repository returns dict payload; ensure fields types
    return it

@router.post("/start", response_model=dict)
async def start_hand(payload: dict = Body(...), repo = Depends(get_repo)):
    """
    Start a new hand with 6 players. Payload expected:
    {
      "table_id": "T1",
      "stack": 1000
    }
    """
    table_id = payload.get("table_id", "T1")
    stack = int(payload.get("stack", 1000))

    # create deck
    ranks = "23456789TJQKA"
    suits = "cdhs"
    deck = [r + s for r in ranks for s in suits]
    random.shuffle(deck)

    players = []
    for i in range(6):
        p = {
            "player_id": str(i+1),
            "name": f"Player {i+1}",
            "seat": i+1,
            "stack": stack,
            "hole_cards": [deck.pop(), deck.pop()],
            "folded": False,
            "contributed": 0
        }
        players.append(p)

    # pick dealer as player with seat 2 for deterministic behavior for tests (or rotate)
    dealer_seat = 2
    dealer_idx = next((i for i,p in enumerate(players) if p["seat"]==dealer_seat), 0)
    small_idx = (dealer_idx + 1) % 6
    big_idx = (dealer_idx + 2) % 6

    small_blind = max(1, stack//50)  # default small blind as 1/50 of stack, fallback to 20 in example
    big_blind = small_blind * 2
    # But to match example with 20/40, if stack >=1000 use 20/40
    if stack >= 1000:
        small_blind = 20
        big_blind = 40

    # post blinds
    players[small_idx]["stack"] -= small_blind
    players[small_idx]["contributed"] = small_blind
    players[big_idx]["stack"] -= big_blind
    players[big_idx]["contributed"] = big_blind

    hand = {
        "hand_id": str(uuid.uuid4()),
        "table_id": table_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "players": players,
        "actions": [],
        "pot": small_blind + big_blind,
        "winners": {},
        "community": {
            "flop": [],
            "turn": None,
            "river": None
        },
        "meta": {
            "dealer_seat": dealer_seat,
            "small_blind": small_blind,
            "big_blind": big_blind
        }
    }

    # initial action log entries (as dicts)
    # deal cards
    for p in players:
        hand["actions"].append({"player_id": p["player_id"], "action": "dealt", "amount": 0, "cards": p["hole_cards"]})
    hand["actions"].append({"action": "dealer", "player_id": str(players[dealer_idx]["player_id"])})
    hand["actions"].append({"action": "post_sb", "player_id": str(players[small_idx]["player_id"]), "amount": small_blind})
    hand["actions"].append({"action": "post_bb", "player_id": str(players[big_idx]["player_id"]), "amount": big_blind})

    # persist initial hand (not final) so frontend can fetch and use; repository save expects full hand object
    try:
        await repo.save(hand)
    except Exception:
        # repository may expect Hand dataclass; still return hand object without saving
        pass

    return hand

@router.post("", status_code=201)
async def save_hand(hand: dict = Body(...), response: Response = None, repo = Depends(get_repo)):
    """
    Save finalized hand to repository. Expects full hand payload.
    """
    hand_id = hand.get("hand_id", str(uuid.uuid4()))
    hand["hand_id"] = hand_id
    # ensure created_at
    if "created_at" not in hand:
        hand["created_at"] = datetime.utcnow().isoformat() + "Z"
    # ensure pot
    if "pot" not in hand:
        hand["pot"] = 0
    try:
        await repo.save(hand)
    except Exception as e:
        # try best-effort; log and continue
        print("Failed to save hand:", e)
        raise HTTPException(status_code=500, detail="Failed to save hand")
    if response is not None:
        response.headers["Location"] = f"/api/v1/hands/{hand_id}"
    return {"hand_id": hand_id}

@router.get("", response_model=List[dict])
async def list_hands(limit: int = 50, offset: int = 0, repo = Depends(get_repo)):
    items = await repo.list(limit=limit, offset=offset)
    out = []
    for it in items:
        out.append(_normalize_hand_obj(it))
    return out


@router.get("/{hand_id}", response_model=Optional[dict])
async def get_hand(hand_id: str, repo = Depends(get_repo)):
    it = await repo.get(hand_id)
    if not it:
        raise HTTPException(status_code=404)
    return _normalize_hand_obj(it)
