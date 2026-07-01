import secrets
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.db import (
    MVP_USERNAME,
    get_board_for_user,
    init_db,
    replace_board_for_user,
    validate_credentials,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"
FRONTEND_OUT_DIR = ROOT_DIR / "frontend" / "out"
DB_PATH = ROOT_DIR / "backend" / "data" / "app.db"
AUTH_COOKIE_NAME = "pm_session"
sessions: dict[str, str] = {}

load_dotenv(ROOT_DIR / ".env")


class LoginRequest(BaseModel):
    username: str
    password: str


class BoardCard(BaseModel):
    id: str
    title: str
    details: str


class BoardColumn(BaseModel):
    id: str
    title: str
    card_ids: list[str] = Field(alias="cardIds")

    model_config = {"populate_by_name": True}


class BoardPayload(BaseModel):
    columns: list[BoardColumn]
    cards: dict[str, BoardCard]

    model_config = {"populate_by_name": True}


def get_authenticated_username(request: Request) -> str:
    token = request.cookies.get(AUTH_COOKIE_NAME)
    username = sessions.get(token or "")
    if not token or not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return username


def validate_board_payload(payload: BoardPayload) -> None:
    for key, card in payload.cards.items():
        if key != card.id:
            raise HTTPException(
                status_code=422,
                detail=f"Card dictionary key '{key}' must match card.id '{card.id}'",
            )

    referenced_card_ids = [card_id for col in payload.columns for card_id in col.card_ids]
    missing = [card_id for card_id in referenced_card_ids if card_id not in payload.cards]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Columns reference missing card IDs: {', '.join(sorted(set(missing)))}",
        )


def build_app(frontend_out_dir: Optional[Path] = None, db_path: Optional[Path] = None) -> FastAPI:
    app = FastAPI(title="Project Management MVP Backend")
    resolved_db_path = db_path or DB_PATH
    init_db(resolved_db_path)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "backend"}

    @app.post("/api/auth/login")
    def login(payload: LoginRequest, response: Response) -> dict[str, str | bool]:
        if not validate_credentials(resolved_db_path, payload.username, payload.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = secrets.token_urlsafe(32)
        sessions[token] = payload.username
        response.set_cookie(
            key=AUTH_COOKIE_NAME,
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,
            path="/",
        )
        return {"authenticated": True, "username": MVP_USERNAME}

    @app.get("/api/auth/me")
    def me(request: Request) -> dict[str, str | bool]:
        username = get_authenticated_username(request)
        return {"authenticated": True, "username": username}

    @app.post("/api/auth/logout")
    def logout(request: Request, response: Response) -> dict[str, bool]:
        token = request.cookies.get(AUTH_COOKIE_NAME)
        if token:
            sessions.pop(token, None)
        response.delete_cookie(AUTH_COOKIE_NAME, path="/")
        return {"authenticated": False}

    @app.get("/api/protected/ping")
    def protected_ping(request: Request) -> dict[str, str]:
        get_authenticated_username(request)
        return {"status": "ok", "message": "authenticated"}

    @app.get("/api/board")
    def get_board(request: Request) -> dict:
        username = get_authenticated_username(request)
        try:
            return get_board_for_user(resolved_db_path, username)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.put("/api/board")
    def update_board(request: Request, payload: BoardPayload) -> dict:
        username = get_authenticated_username(request)
        validate_board_payload(payload)
        board_dict = payload.model_dump(by_alias=True)
        try:
            replace_board_for_user(resolved_db_path, username, board_dict)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"updated": True, "board": board_dict}

    resolved_frontend_dir = frontend_out_dir or FRONTEND_OUT_DIR

    if resolved_frontend_dir.exists():
        app.mount(
            "/", StaticFiles(directory=resolved_frontend_dir, html=True), name="frontend"
        )
    else:
        @app.get("/")
        def index() -> FileResponse:
            return FileResponse(STATIC_DIR / "index.html")

    return app


app = build_app()
