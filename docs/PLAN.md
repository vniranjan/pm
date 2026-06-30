# Project Plan

This document is the execution plan for the Project Management MVP.

Guiding constraints:
- Keep MVP scope tight. No extra features beyond requirements.
- Prefer simple, idiomatic implementations.
- Prove root cause before fixing issues.
- Testing target: about 80% unit test coverage where practical, plus integration tests that cover critical flows only.

Status legend:
- `[ ]` not started
- `[x]` done

## Part 1: Planning and Project Baseline

Objective:
- Finalize a detailed, approved implementation plan before feature work begins.

Checklist:
- [x] Confirm and document MVP scope, limitations, and non-goals.
- [x] Expand this file with detailed substeps, tests, and success criteria for all parts.
- [x] Add `frontend/AGENTS.md` describing current frontend structure and behavior.
- [x] Keep `backend/AGENTS.md` as placeholder for now; fill in later during backend implementation.
- [x] Get explicit user approval on this plan before moving to Part 2.

Tests:
- [x] Documentation sanity check: steps are actionable and ordered.
- [x] No code changes outside documentation in this part.

Success criteria:
- [x] Plan is explicit enough to execute without ambiguity.
- [x] User approves plan before implementation starts.

## Part 2: Scaffolding (Docker + FastAPI + Scripts)

Objective:
- Establish runnable local containerized baseline with FastAPI backend and scripts.

Checklist:
- [ ] Add Docker setup for single-container app.
- [ ] Initialize backend app in `backend/` using FastAPI.
- [ ] Configure backend to serve simple static hello page at `/`.
- [ ] Add sample API route (for example `/api/health`) and verify from served page.
- [ ] Add start/stop scripts for Mac, Linux, and Windows under `scripts/`.
- [ ] Wire environment loading for local `.env` usage.

Tests:
- [ ] Backend unit tests for health route and app startup.
- [ ] Integration test: container starts and `/` + `/api/health` respond correctly.
- [ ] Script smoke tests: start then stop works on current OS.

Success criteria:
- `docker` run path works locally.
- Visiting `/` returns hello page.
- API call from page to backend succeeds.

## Part 3: Serve Frontend Demo from Backend

Objective:
- Replace hello page with built Next.js frontend served through FastAPI at `/`.

Checklist:
- [ ] Configure frontend static build output for container use.
- [ ] Copy/build frontend artifacts in Docker image.
- [ ] Serve static frontend assets from FastAPI.
- [ ] Ensure `/` loads existing demo Kanban UI.
- [ ] Add `frontend/AGENTS.md` if still missing from Part 1.

Tests:
- [ ] Frontend unit tests for key Kanban rendering behavior.
- [ ] Backend integration test verifies static asset route + index load.
- [ ] End-to-end smoke test: Kanban board renders at `/`.

Success criteria:
- App root shows demo Kanban in containerized run.
- Static assets load without path or MIME issues.

## Part 4: MVP Authentication Flow (Hardcoded Credentials)

Objective:
- Gate Kanban behind login with `user` / `password` and allow logout.

Checklist:
- [ ] Add login UI route/view in frontend.
- [ ] Add backend login endpoint validating hardcoded credentials.
- [ ] Add simple session/token mechanism suitable for MVP.
- [ ] Protect Kanban routes; unauthenticated users see login.
- [ ] Implement logout flow clearing auth state.

Tests:
- [ ] Unit tests for credential validation and auth state transitions.
- [ ] Integration tests: unauthenticated blocked; authenticated allowed.
- [ ] UI integration test: login success + logout returns to login screen.

Success criteria:
- Only authenticated users can access Kanban.
- Invalid credentials are rejected with clear error.

## Part 5: Database Modeling (SQLite + JSON Board State)

Objective:
- Define and document durable data model for one board per user (with multi-user-ready structure).

Checklist:
- [ ] Propose schema in docs and request user sign-off before implementation.
- [ ] Model users table (future-ready, even with MVP single credentials).
- [ ] Model board storage as JSON payload per user.
- [ ] Document migration/initialization strategy (create DB if missing).
- [ ] Document tradeoffs and MVP constraints.

Proposed schema (for approval):
- `users`
  - `id` (INTEGER PRIMARY KEY)
  - `username` (TEXT UNIQUE NOT NULL)
  - `password_hash` (TEXT NOT NULL)
  - `created_at` (TEXT NOT NULL)
- `boards`
  - `id` (INTEGER PRIMARY KEY)
  - `user_id` (INTEGER UNIQUE NOT NULL REFERENCES users(id))
  - `board_json` (TEXT NOT NULL)  # serialized Kanban JSON
  - `updated_at` (TEXT NOT NULL)

Tests:
- [ ] Unit tests for model serialization/deserialization.
- [ ] Integration test creates DB from empty state.
- [ ] Integration test ensures one-board-per-user constraint.

Success criteria:
- Schema documented and approved by user before coding data layer.
- DB bootstraps automatically if file does not exist.

## Part 6: Backend Kanban API

Objective:
- Build CRUD-style endpoints needed by frontend to load and persist Kanban board.

Checklist:
- [ ] Add authenticated endpoint to fetch current user board.
- [ ] Add authenticated endpoint to replace/update board JSON.
- [ ] Validate payload shape minimally but clearly.
- [ ] Ensure user isolation in queries by auth identity.
- [ ] Add clear API error responses.

Tests:
- [ ] Unit tests for service/repository logic.
- [ ] Unit tests for payload validation.
- [ ] Integration tests for auth + board read/write behavior.
- [ ] Integration test for DB auto-create on first run.

Success criteria:
- Backend fully supports persisted Kanban for authenticated user.
- API behavior is deterministic and tested.

## Part 7: Frontend/Backend Integration

Objective:
- Move frontend from local mock state to backend-persisted state.

Checklist:
- [ ] Replace mock/local board loading with API fetch on app load.
- [ ] Persist board changes (rename columns, edit/move cards) via API.
- [ ] Handle loading and error states without overengineering.
- [ ] Keep drag-and-drop UX functional with persistence.

Tests:
- [ ] Frontend unit tests for API client and state update reducers/hooks.
- [ ] Integration tests for initial load + save workflows.
- [ ] End-to-end test for move/edit card persists after refresh.

Success criteria:
- Board modifications persist across page reloads.
- Core Kanban operations still work smoothly.

## Part 8: AI Connectivity via OpenRouter

Objective:
- Add backend AI client and verify reliable connectivity using OpenRouter.

Checklist:
- [ ] Implement backend AI client using OpenRouter with `.env` key.
- [ ] Configure model as `openai/gpt-oss-120b`.
- [ ] Add a minimal backend test route/command for connectivity check.
- [ ] Validate response using simple prompt (`2+2`).

Tests:
- [ ] Unit tests for request construction and error mapping.
- [ ] Integration test with mocked OpenRouter response.
- [ ] Manual connectivity check using real key in local environment.

Success criteria:
- Backend successfully calls OpenRouter and receives valid response.
- Error paths are handled with clear API messages.

## Part 9: Structured Output AI Contract (Plan + Implementation)

Objective:
- Have AI return chat response plus optional board mutation instructions based on board JSON + chat history.

Checklist:
- [ ] Propose final JSON schema below and get user approval before coding this part.
- [ ] Send board JSON + user message + conversation history to model.
- [ ] Enforce structured response parsing and validation.
- [ ] Apply valid board update when included; otherwise no board mutation.
- [ ] Persist board changes atomically after successful validation.

Proposed structured output schema (for approval):
```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "assistant_message": { "type": "string" },
    "board_update": {
      "type": ["object", "null"],
      "additionalProperties": false,
      "properties": {
        "columns": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "properties": {
              "id": { "type": "string" },
              "title": { "type": "string" },
              "card_ids": {
                "type": "array",
                "items": { "type": "string" }
              }
            },
            "required": ["id", "title", "card_ids"]
          }
        },
        "cards": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "properties": {
              "id": { "type": "string" },
              "title": { "type": "string" },
              "description": { "type": "string" }
            },
            "required": ["id", "title", "description"]
          }
        }
      },
      "required": ["columns", "cards"]
    }
  },
  "required": ["assistant_message", "board_update"]
}
```

Tests:
- [ ] Unit tests for schema validation and parser behavior.
- [ ] Unit tests for safe apply logic (valid/invalid updates).
- [ ] Integration tests for chat request leading to no-op and update cases.

Success criteria:
- AI response always includes user-facing message.
- Board updates are optional, validated, and persisted only when valid.

## Part 10: AI Sidebar UX and Live Board Refresh

Objective:
- Add production-ready MVP chat sidebar that can trigger board updates and reflect them immediately.

Checklist:
- [ ] Build sidebar UI integrated with existing Kanban layout.
- [ ] Add message list, input box, submit handling, loading/error states.
- [ ] Display assistant responses clearly.
- [ ] Apply and render board updates from structured output.
- [ ] Trigger immediate UI refresh when board is updated.

Tests:
- [ ] Frontend unit tests for chat state handling.
- [ ] Integration tests for send/receive chat flow.
- [ ] End-to-end test where AI update changes board and UI refreshes.

Success criteria:
- User can chat with AI in sidebar reliably.
- AI-driven board changes appear without manual reload.

## Cross-Cutting Quality Gates

- [ ] Unit test coverage near 80% for backend/frontend core logic, without writing low-value tests.
- [ ] Integration tests cover critical user journeys:
  - Login/logout
  - Load board
  - Edit/move cards and persist
  - AI chat no-op response
  - AI chat with board update
- [ ] Lint/format/test commands documented and runnable locally.
- [ ] Keep README concise and strictly MVP-focused.

## Approval Gates

- [x] Gate A: User approves this expanded plan before implementation begins.
- [ ] Gate B: User approves DB schema documentation before Part 5 implementation.
- [ ] Gate C: User approves structured output schema before Part 9 implementation.
