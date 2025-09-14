import { createHandDraft } from "../lib/gameLogic";

test("createHandDraft creates valid hand", () => {
  const h = createHandDraft({
    tableId: "T1",
    players: [{ player_id: "p1", name: "A", seat: 1, stack: 1000 }],
  });
  expect(h.hand_id).toBeDefined();
  expect(h.players.length).toBe(1);
});
