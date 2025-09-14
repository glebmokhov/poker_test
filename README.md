# Poker Test Application (Skeleton)

## Overview

Minimal skeleton for the Texas Hold'em test app:
- Backend: FastAPI (no ORM) + asyncpg + repository pattern.
- Frontend: Next.js + TypeScript (single-page) — minimal components included.
- Shared JSON Schema at `schemas/hand.schema.json`.
- Poker calculations: attempted via `pokerkit` if available; fallback split otherwise.

## Quick start with Docker (recommended)

1. Build and start:
   ```bash
   docker compose up -d --build
   ```
2. Open the app in your browser:
   ```
   http://localhost:3000
   ```

## Notes

- The backend will attempt to create the `hands` table on startup (it retries until DB is reachable).
- To run locally without Docker:
  - Backend: use Poetry (see `backend/pyproject.toml`).
  - Frontend: install Node (18+) and run `npm ci` then `npm run dev` inside `frontend/`.

## Tests
- Backend: run pytest inside `backend/`.
- Frontend: run `npm test` inside `frontend/` (basic jest tests included).

## Important
This is a skeleton designed to be readable and educational. You may adapt and extend it.
