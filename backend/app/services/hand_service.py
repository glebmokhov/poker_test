import logging
from app.repositories.base import HandRepository
from app.schemas.hand import HandSchema
from app.services.helpers import hand_from_schema
from app.domain.models import Hand

logger = logging.getLogger(__name__)

try:
    import pokerkit
    from pokerkit import Automation, NoLimitTexasHoldem
    POKERKIT_AVAILABLE = True
except Exception:
    POKERKIT_AVAILABLE = False
    logger.info("pokerkit not available; using fallback payouts")

class HandService:
    def __init__(self, repo: HandRepository):
        self.repo = repo

    async def complete_and_save_hand(self, hand_schema: HandSchema) -> Hand:
        hand = hand_from_schema(hand_schema)

        # Try using pokerkit if available and community cards present
        if POKERKIT_AVAILABLE and hand.community and any(hand.community.get(k) for k in ("flop","turn","river")):
            try:
                automations = (
                    Automation.ANTE_POSTING,
                    Automation.BET_COLLECTION,
                    Automation.BLIND_OR_STRADDLE_POSTING,
                    Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                    Automation.HAND_KILLING,
                    Automation.CHIPS_PUSHING,
                    Automation.CHIPS_PULLING,
                )
                stacks = tuple(p.stack for p in hand.players)
                small_big = (20,40)
                state = NoLimitTexasHoldem.create_state(
                    automations,
                    False,
                    0,
                    small_big,
                    20,
                    stacks,
                    len(hand.players)
                )
                # feed holes
                for p in hand.players:
                    if p.hole_cards:
                        try:
                            state.deal_hole(''.join(p.hole_cards))
                        except Exception:
                            pass
                # feed board
                comm = hand.community or {}
                if comm.get('flop'):
                    state.burn_card()
                    state.deal_board(''.join(comm.get('flop',[])))
                if comm.get('turn'):
                    state.burn_card()
                    state.deal_board(''.join(comm.get('turn',[])))
                if comm.get('river'):
                    state.burn_card()
                    state.deal_board(''.join(comm.get('river',[])))
                # obtain payoffs if available
                payoffs = getattr(state, 'payoffs', None)
                if callable(payoffs):
                    payoffs = payoffs()
                if payoffs:
                    winners = {}
                    for idx, p in enumerate(hand.players):
                        try:
                            winners[p.player_id] = int(payoffs[idx])
                        except Exception:
                            winners[p.player_id] = 0
                    hand.winners = winners
            except Exception as e:
                logger.exception("pokerkit integration failed: %s", e)

        # fallback simple split among non-folded players
        if not hand.winners:
            active = [p for p in hand.players if not self._player_folded(p.player_id, hand.actions)]
            if active:
                share = hand.pot // len(active)
                hand.winners = {p.player_id: share for p in active}
            else:
                hand.winners = {p.player_id: 0 for p in hand.players}

        await self.repo.save(hand)
        return hand

    def _player_folded(self, player_id: str, actions) -> bool:
        for a in actions:
            act = a.action if hasattr(a,'action') else a.get('action')
            pid = a.player_id if hasattr(a,'player_id') else a.get('player_id')
            if pid == player_id and act in ('f','fold'):
                return True
        return False
