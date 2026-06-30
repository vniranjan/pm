# Backend Agent Notes

## Purpose

This directory contains the FastAPI backend for the Project Management MVP.

Current status:
- Part 2 and Part 3 scaffolding are implemented.
- Part 4 auth endpoints and session flow are implemented.
- Backend serves exported Next.js frontend assets at `/` when available.
- Backend exposes `GET /api/health`.
- App is containerized and runnable via Docker Compose from the repo root.

## Stack

- Python + FastAPI
- Uvicorn ASGI server
- `python-dotenv` for local `.env` loading
- `uv` for dependency management in Docker and local project workflows
- Pytest for backend tests

## High-Level Structure

- `app/main.py`
  - FastAPI app definition.
  - Loads env vars from project-root `.env`.
  - Uses app factory (`build_app`) to support testable frontend static mounting.
  - Routes:
    - `GET /` -> serves static frontend export (`frontend/out`) when present.
    - Fallback `GET /` -> serves `app/static/index.html` (if frontend export not present).
    - `GET /api/health` -> JSON health response
    - `POST /api/auth/login` -> validates hardcoded credentials (`user` / `password`)
    - `GET /api/auth/me` -> returns authenticated user if cookie session is valid
    - `POST /api/auth/logout` -> clears current session cookie
    - `GET /api/protected/ping` -> auth-protected route for integration checks
- `app/static/index.html`
  - Part 2 hello page with button that calls `/api/health` from browser.
- `tests/test_main.py`
  - Tests for health endpoint, root/static serving, and full auth flow (login/me/protected/logout).
- `pyproject.toml`
  - Runtime and dev dependency definitions.

## Runtime (Repo Root)

- Build/start container: `docker compose up --build -d`
- Stop container: `docker compose down --remove-orphans`
- App URL: `http://localhost:8000`

## Notes For Next Phases

- This backend is intentionally minimal for scaffold validation.
- Future phases will add auth, persistence, API endpoints for board data, and AI routes.
