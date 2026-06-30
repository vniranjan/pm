from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


ROOT_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"
FRONTEND_OUT_DIR = ROOT_DIR / "frontend" / "out"

load_dotenv(ROOT_DIR / ".env")

def build_app(frontend_out_dir: Optional[Path] = None) -> FastAPI:
    app = FastAPI(title="Project Management MVP Backend")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "backend"}

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
