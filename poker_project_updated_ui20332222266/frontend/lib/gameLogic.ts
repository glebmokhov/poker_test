export function createHandDraft(params: {
  tableId: string;
  players: Array<{ player_id: string; name: string; seat: number; stack: number }>;
}) {
  const hand = {
    hand_id: crypto.randomUUID(),
    table_id: params.tableId,
    created_at: new Date().toISOString(),
    players: params.players.map(p => ({ ...p, hole_cards: [] })),
    actions: [],
    pot: 0,
    winners: {},
    community: {
      flop: [],
      turn: [],
      river: []
    }
  };
  return hand;
}

export function appendAction(hand: any, action: { timestamp?: string; round: string; player_id: string; action: string; amount?: number }) {
  const a = {
    timestamp: action.timestamp ?? new Date().toISOString(),
    round: action.round,
    player_id: action.player_id,
    action: action.action,
    amount: action.amount ?? 0
  };
  hand.actions.push(a);
  if (a.action.startsWith("b") || a.action.startsWith("r") || a.action === "allin" || a.action === "c") {
    hand.pot += a.amount || 0;
  }
  return hand;
}
