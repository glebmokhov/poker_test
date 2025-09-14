from app.domain.models import Hand, PlayerSnapshot, Action
from app.schemas.hand import HandSchema

def hand_from_schema(schema: HandSchema) -> Hand:
    players = [PlayerSnapshot(
        player_id=p.player_id,
        name=p.name,
        seat=p.seat,
        stack=p.stack,
        hole_cards=p.hole_cards
    ) for p in schema.players]
    actions = [Action(
        timestamp=a.timestamp.isoformat(),
        round=a.round,
        player_id=a.player_id,
        action=a.action,
        amount=a.amount
    ) for a in schema.actions]
    community = {}
    if schema.community:
        community = {
            "flop": schema.community.flop or [],
            "turn": schema.community.turn or [],
            "river": schema.community.river or []
        }
    return Hand(
        hand_id=schema.hand_id,
        table_id=schema.table_id,
        created_at=schema.created_at.isoformat(),
        players=players,
        actions=actions,
        pot=schema.pot,
        winners=schema.winners or {},
        community=community
    )

def hand_from_dict(d: dict) -> Hand:
    players = [PlayerSnapshot(**p) for p in d.get("players",[])]
    actions = [Action(**a) for a in d.get("actions",[])]
    return Hand(
        hand_id=d["hand_id"],
        table_id=d["table_id"],
        created_at=d["created_at"],
        players=players,
        actions=actions,
        pot=d.get("pot",0),
        winners=d.get("winners",{}),
        community=d.get("community",{})
    )
