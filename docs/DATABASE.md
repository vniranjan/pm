# Database Design (Part 5)

This document defines the MVP database model for persistent Kanban state.

## Goals

- Use SQLite locally.
- Support one board per authenticated user for MVP.
- Keep schema future-ready for multi-user use.
- Store the full board as JSON text for simple reads/writes.
- Create DB automatically if missing.

## SQLite File

- File path (proposed): `backend/data/app.db`
- Behavior:
  - If file does not exist, backend creates directory and DB file on startup.
  - Schema is initialized on startup.

## Schema (Proposed)

### `users`

- `id` INTEGER PRIMARY KEY
- `username` TEXT NOT NULL UNIQUE
- `password_hash` TEXT NOT NULL
- `created_at` TEXT NOT NULL

Notes:
- MVP login is still hardcoded in code (`user` / `password`).
- `users` table is included now to avoid redesign later.
- For MVP seed, we can insert a single row for `user` if missing.

### `boards`

- `id` INTEGER PRIMARY KEY
- `user_id` INTEGER NOT NULL UNIQUE REFERENCES `users(id)` ON DELETE CASCADE
- `board_json` TEXT NOT NULL
- `updated_at` TEXT NOT NULL

Notes:
- `user_id` is `UNIQUE` to enforce exactly one board per user.
- `board_json` stores serialized board state.

## Board JSON Shape (Stored in `boards.board_json`)

```json
{
  "columns": [
    { "id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"] }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Task title",
      "details": "Task details"
    }
  }
}
```

This mirrors current frontend board state shape to keep integration simple.

## Initialization and Migration Strategy

For MVP, use a simple startup initializer:

1. Ensure data directory exists.
2. Open SQLite connection.
3. Run `CREATE TABLE IF NOT EXISTS` for `users` and `boards`.
4. Ensure required indexes/constraints exist.
5. Seed MVP user row (`username = 'user'`) if missing.
6. Seed default board row for that user if missing.

No external migration framework is required for MVP.

If schema changes later:
- Add a lightweight schema version table (or SQLite `PRAGMA user_version`).
- Apply incremental SQL migration steps on startup.

## Query Model (MVP)

- Read board:
  - Resolve authenticated user ID.
  - `SELECT board_json FROM boards WHERE user_id = ?`
- Write board:
  - Replace full JSON payload.
  - `UPDATE boards SET board_json = ?, updated_at = ? WHERE user_id = ?`

This keeps API/service code simple and deterministic.

## Tradeoffs

Pros:
- Very simple persistence path.
- Easy to reason about in tests.
- Matches current frontend data shape.

Cons:
- JSON text is not ideal for partial updates/querying.
- Limited flexibility for analytics/reporting queries.
- Concurrent edits are coarse-grained (whole-board replace).

MVP decision:
- Accept these tradeoffs for speed and simplicity.
- Revisit normalized tables only if product requirements demand it.

## Validation Plan for Part 6+

- Unit tests:
  - serialization/deserialization roundtrip for board JSON
  - default board seed behavior
- Integration tests:
  - DB file created on empty startup
  - one-board-per-user uniqueness enforced
  - board read/write by authenticated user
