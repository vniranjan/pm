# Backend Agent Notes

## Purpose

This directory contains the FastAPI backend for the Project Management MVP.

Current status:
- Part 2 scaffolding is implemented.
- Backend serves a static hello page at `/`.
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
  - Routes:
    - `GET /` -> serves `app/static/index.html`
    - `GET /api/health` -> JSON health response
- `app/static/index.html`
  - Part 2 hello page with button that calls `/api/health` from browser.
- `tests/test_main.py`
  - Unit tests for root page and health endpoint.
- `pyproject.toml`
  - Runtime and dev dependency definitions.

## Runtime (Repo Root)

- Build/start container: `docker compose up --build -d`
- Stop container: `docker compose down --remove-orphans`
- App URL: `http://localhost:8000`

## Notes For Next Phases

- This backend is intentionally minimal for scaffold validation.
- Future phases will add auth, persistence, API endpoints for board data, and AI routes.
