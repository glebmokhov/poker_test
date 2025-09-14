
"use client";
import React, { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

type Hand = {
  hand_id: string;
  table_id: string;
  created_at: string;
  players: any[];
  actions: any[];
  pot: number;
  winners: Record<string, number>;
  community: any;
};

export default function HandHistory() {
  const [hands, setHands] = useState<Hand[]>([]);

  async function load() {
    const res = await fetch(`${API_BASE}/api/v1/hands`);
    if (!res.ok) return;
    const data = await res.json();
    setHands(data || []);
  }

  useEffect(() => {
    load();
  }, []);

  function shortActions(actions: any[]) {
    return (actions || []).map((a) => a.action + (a.amount ? ":" + a.amount : "")).join(", ");
  }

  return (
    <div>
      <button onClick={load} style={{ marginBottom: 8 }}>
        Refresh
      </button>
      {hands.length === 0 && <div>No hands</div>}
      <ul>
        {hands.map((h) => (
          <li key={h.hand_id} style={{ marginBottom: 12, borderBottom: "1px solid #eee", paddingBottom: 8 }}>
            <div>
              <strong>{h.hand_id}</strong>
            </div>
            <div>Stacks: {h.players ? h.players.map((p: any) => p.stack).join(", ") : ""}</div>
            <div>Cards: {h.players ? h.players.map((p: any) => (p.hole_cards || []).join("")).join(" | ") : ""}</div>
            <div>Actions: {shortActions(h.actions || [])}</div>
            <div>Winners: {h.winners ? Object.entries(h.winners).map(([k, v]) => k + ":" + v).join(", ") : ""}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
