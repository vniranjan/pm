from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import build_app, sessions


def make_client(tmp_path: Path, frontend_out: Path | None = None) -> TestClient:
    sessions.clear()
    db_path = tmp_path / "app.db"
    return TestClient(build_app(frontend_out_dir=frontend_out, db_path=db_path))


def test_health_returns_ok(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "backend"}


def test_root_serves_html_page(tmp_path: Path) -> None:
    client = make_client(tmp_path)
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

    client = make_client(tmp_path, frontend_out=frontend_out)

    index_response = client.get("/")
    assert index_response.status_code == 200
    assert "Kanban Studio" in index_response.text

    asset_response = client.get("/_next/static/chunk.js")
    assert asset_response.status_code == 200
    assert "console.log('ok');" in asset_response.text


def test_login_rejects_invalid_credentials(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    response = client.post(
        "/api/auth/login",
        json={"username": "wrong", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_login_me_and_logout_flow(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    me_before = client.get("/api/auth/me")
    assert me_before.status_code == 401

    login = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    assert login.status_code == 200
    assert login.json() == {"authenticated": True, "username": "user"}

    me_after = client.get("/api/auth/me")
    assert me_after.status_code == 200
    assert me_after.json() == {"authenticated": True, "username": "user"}

    protected = client.get("/api/protected/ping")
    assert protected.status_code == 200
    assert protected.json() == {"status": "ok", "message": "authenticated"}

    logout = client.post("/api/auth/logout")
    assert logout.status_code == 200
    assert logout.json() == {"authenticated": False}

    me_after_logout = client.get("/api/auth/me")
    assert me_after_logout.status_code == 401

    protected_after_logout = client.get("/api/protected/ping")
    assert protected_after_logout.status_code == 401


def test_board_endpoints_require_auth(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    assert client.get("/api/board").status_code == 401
    assert client.put("/api/board", json={"columns": [], "cards": {}}).status_code == 401


def test_board_can_be_read_and_updated(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    login = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    assert login.status_code == 200

    read_response = client.get("/api/board")
    assert read_response.status_code == 200
    board = read_response.json()
    assert "columns" in board
    assert "cards" in board

    board["columns"][0]["title"] = "Today"
    update_response = client.put("/api/board", json=board)
    assert update_response.status_code == 200
    assert update_response.json()["updated"] is True

    verify_response = client.get("/api/board")
    assert verify_response.status_code == 200
    assert verify_response.json()["columns"][0]["title"] == "Today"


def test_board_validation_rejects_unknown_card_reference(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )

    invalid_board = {
        "columns": [{"id": "col-1", "title": "Backlog", "cardIds": ["missing-card"]}],
        "cards": {},
    }
    response = client.put("/api/board", json=invalid_board)
    assert response.status_code == 422
    assert "missing card IDs" in response.json()["detail"]


def test_board_validation_rejects_card_key_mismatch(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )

    invalid_board = {
        "columns": [{"id": "col-1", "title": "Backlog", "cardIds": ["card-1"]}],
        "cards": {"wrong-key": {"id": "card-1", "title": "Task", "details": "Details"}},
    }
    response = client.put("/api/board", json=invalid_board)
    assert response.status_code == 422
    assert "must match card.id" in response.json()["detail"]
