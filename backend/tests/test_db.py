from pathlib import Path
import sqlite3
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db import (
    DEFAULT_BOARD,
    connect,
    get_board_for_user,
    init_db,
    replace_board_for_user,
    validate_credentials,
)


def test_init_db_creates_file_and_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "app.db"
    init_db(db_path)
    assert db_path.exists()

    with connect(db_path) as conn:
        users_table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        ).fetchone()
        boards_table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='boards'"
        ).fetchone()

    assert users_table is not None
    assert boards_table is not None


def test_validate_credentials_uses_mvp_credentials(tmp_path: Path) -> None:
    db_path = tmp_path / "app.db"
    init_db(db_path)

    assert validate_credentials(db_path, "user", "password") is True
    assert validate_credentials(db_path, "user", "wrong") is False
    assert validate_credentials(db_path, "wrong", "password") is False


def test_board_round_trip(tmp_path: Path) -> None:
    db_path = tmp_path / "app.db"
    init_db(db_path)

    initial_board = get_board_for_user(db_path, "user")
    assert initial_board["columns"][0]["id"] == DEFAULT_BOARD["columns"][0]["id"]

    updated = initial_board
    updated["columns"][0]["title"] = "Updated"
    replace_board_for_user(db_path, "user", updated)

    reloaded = get_board_for_user(db_path, "user")
    assert reloaded["columns"][0]["title"] == "Updated"


def test_one_board_per_user_constraint(tmp_path: Path) -> None:
    db_path = tmp_path / "app.db"
    init_db(db_path)

    with connect(db_path) as conn:
        user_id = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            ("user",),
        ).fetchone()["id"]
        # Attempting to insert a second board for same user should fail.
        try:
            conn.execute(
                "INSERT INTO boards (user_id, board_json, updated_at) VALUES (?, ?, ?)",
                (user_id, "{}", "2026-01-01T00:00:00+00:00"),
            )
            assert False, "Expected UNIQUE constraint violation for boards.user_id"
        except sqlite3.IntegrityError as exc:
            assert "UNIQUE constraint failed" in str(exc)
