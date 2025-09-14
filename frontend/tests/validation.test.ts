import { validateHandMinimal } from "../lib/validation";

test("validation passes for valid hand", () => {
  const h = {
    hand_id: "h1",
    table_id: "T",
    created_at: new Date().toISOString(),
    players: [{ player_id: "p1", name: "A", seat: 1, stack: 1000 }],
    actions: [],
    pot: 0,
    winners: {},
  };
  expect(validateHandMinimal(h)).toBe(true);
});
