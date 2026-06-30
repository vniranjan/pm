from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import build_app, sessions


client = TestClient(build_app())


def test_health_returns_ok() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "backend"}


def test_root_serves_html_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!doctype html>" in response.text.lower()


def test_root_serves_frontend_export_when_present(tmp_path: Path) -> None:
    frontend_out = tmp_path / "out"
    next_static = frontend_out / "_next" / "static"
    next_static.mkdir(parents=True)

    index_html = frontend_out / "index.html"
    index_html.write_text(
        "<!doctype html><html><body><h1>Kanban Studio</h1></body></html>",
        encoding="utf-8",
    )

    chunk_file = next_static / "chunk.js"
    chunk_file.write_text("console.log('ok');", encoding="utf-8")

    test_client = TestClient(build_app(frontend_out))

    index_response = test_client.get("/")
    assert index_response.status_code == 200
    assert "Kanban Studio" in index_response.text

    asset_response = test_client.get("/_next/static/chunk.js")
    assert asset_response.status_code == 200
    assert "console.log('ok');" in asset_response.text


def test_login_rejects_invalid_credentials() -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "wrong", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_login_me_and_logout_flow() -> None:
    sessions.clear()
    auth_client = TestClient(build_app())

    me_before = auth_client.get("/api/auth/me")
    assert me_before.status_code == 401

    login = auth_client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    assert login.status_code == 200
    assert login.json() == {"authenticated": True, "username": "user"}

    me_after = auth_client.get("/api/auth/me")
    assert me_after.status_code == 200
    assert me_after.json() == {"authenticated": True, "username": "user"}

    protected = auth_client.get("/api/protected/ping")
    assert protected.status_code == 200
    assert protected.json() == {"status": "ok", "message": "authenticated"}

    logout = auth_client.post("/api/auth/logout")
    assert logout.status_code == 200
    assert logout.json() == {"authenticated": False}

    me_after_logout = auth_client.get("/api/auth/me")
    assert me_after_logout.status_code == 401

    protected_after_logout = auth_client.get("/api/protected/ping")
    assert protected_after_logout.status_code == 401
