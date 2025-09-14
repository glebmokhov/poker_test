
"use client";

import React, { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

type Player = {
  player_id: string;
  name: string;
  seat: number;
  stack: number;
  hole_cards: string[];
  folded?: boolean;
  contributed?: number;
};

type Action = {
  timestamp: string;
  round: string;
  player_id: string;
  action: string;
  amount?: number;
};

type Hand = {
  hand_id: string;
  table_id: string;
  created_at: string;
  players: Player[];
  actions: Action[];
  pot: number;
  winners: Record<string, number>;
  community: { flop: string[]; turn: string[]; river: string[] };
};

export default function PlayField() {
  const [hand, setHand] = useState<Hand | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [stackInput, setStackInput] = useState<number>(1000);
  const [betAmount, setBetAmount] = useState<number>(50);

  function pushLog(line: string) {
    setLogs((l) => [...l, line]);
  }

  async function handleStart() {
    const payload = { table_id: "T1", stack: stackInput };
    const res = await fetch(`${API_BASE}/api/v1/hands/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      pushLog("Failed to start hand: " + res.status);
      return;
    }
    const h = await res.json();
    setHand(h);
    pushLog("Started hand " + h.hand_id);
    (h.actions || []).forEach((a: any) => {
      if (a.action === "post_sb") pushLog(`${a.player_id} posts small blind - ${a.amount} chips`);
      if (a.action === "post_bb") pushLog(`${a.player_id} posts big blind - ${a.amount} chips`);
    });
    const bbAction = (h.actions || []).find((a: any) => a.action === "post_bb");
    const bbIndex = h.players.findIndex((p: any) => p.player_id === (bbAction ? bbAction.player_id : ""));
    const first = (bbIndex + 1) % (h.players.length || 1);
    pushLog(`Action starts with ${h.players[first]?.name || "Unknown"}`);
  }

  async function saveHand() {
    if (!hand) return;
    const res = await fetch(`${API_BASE}/api/v1/hands`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(hand),
    });
    if (!res.ok) {
      pushLog("Failed to save hand: " + res.status);
      return;
    }
    pushLog("Saved hand " + hand.hand_id);
  }

  function shortActions(actions: Action[]) {
    return actions.map((a) => `${a.action}${a.amount ? ":" + a.amount : ""}`).join(", ");
  }

  return (
    <div>
      <div style={{ marginBottom: 12 }}>
        <label>
          Default stack:
          <input
            type="number"
            value={stackInput}
            onChange={(e) => setStackInput(Number(e.target.value))}
            style={{ marginLeft: 8 }}
          />
        </label>
        <button onClick={handleStart} style={{ marginLeft: 8 }}>
          Start
        </button>
        <button onClick={saveHand} style={{ marginLeft: 8 }}>
          Save
        </button>
      </div>

      <div style={{ marginBottom: 12 }}>
        <strong>Logs</strong>
        <div style={{ maxHeight: 150, overflow: "auto", background: "#fafafa", padding: 8 }}>
          {logs.map((l, i) => (
            <div key={i}>{l}</div>
          ))}
        </div>
      </div>

      <div>
        <h3>Current Hand</h3>
        {!hand && <div>No active hand</div>}
        {hand && (
          <div>
            <div>
              <strong>{hand.hand_id}</strong> — Pot: {hand.pot}
            </div>
            <div>Players: {hand.players.map((p) => `${p.name}(${p.stack})`).join(" | ")}</div>
            <div>Actions: {shortActions(hand.actions || [])}</div>
            <div style={{ marginTop: 8 }}>
              <label>
                Bet amount:
                <input
                  type="number"
                  value={betAmount}
                  onChange={(e) => setBetAmount(Number(e.target.value))}
                  style={{ marginLeft: 8 }}
                />
              </label>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
