import secrets
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


ROOT_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"
FRONTEND_OUT_DIR = ROOT_DIR / "frontend" / "out"
AUTH_COOKIE_NAME = "pm_session"
MVP_USERNAME = "user"
MVP_PASSWORD = "password"
sessions: set[str] = set()

load_dotenv(ROOT_DIR / ".env")


class LoginRequest(BaseModel):
    username: str
    password: str


def validate_credentials(username: str, password: str) -> bool:
    return username == MVP_USERNAME and password == MVP_PASSWORD


def get_authenticated_username(request: Request) -> str:
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return MVP_USERNAME


def build_app(frontend_out_dir: Optional[Path] = None) -> FastAPI:
    app = FastAPI(title="Project Management MVP Backend")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "backend"}

    @app.post("/api/auth/login")
    def login(payload: LoginRequest, response: Response) -> dict[str, str | bool]:
        if not validate_credentials(payload.username, payload.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = secrets.token_urlsafe(32)
        sessions.add(token)
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
            sessions.discard(token)
        response.delete_cookie(AUTH_COOKIE_NAME, path="/")
        return {"authenticated": False}

    @app.get("/api/protected/ping")
    def protected_ping(request: Request) -> dict[str, str]:
        get_authenticated_username(request)
        return {"status": "ok", "message": "authenticated"}

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
