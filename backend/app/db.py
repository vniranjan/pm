import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MVP_USERNAME = "user"
MVP_PASSWORD = "password"

DEFAULT_BOARD: dict[str, Any] = {
    "columns": [
        {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
        {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
        {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
        {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
        {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
    ],
    "cards": {
        "card-1": {
            "id": "card-1",
            "title": "Align roadmap themes",
            "details": "Draft quarterly themes with impact statements and metrics.",
        },
        "card-2": {
            "id": "card-2",
            "title": "Gather customer signals",
            "details": "Review support tags, sales notes, and churn feedback.",
        },
        "card-3": {
            "id": "card-3",
            "title": "Prototype analytics view",
            "details": "Sketch initial dashboard layout and key drill-downs.",
        },
        "card-4": {
            "id": "card-4",
            "title": "Refine status language",
            "details": "Standardize column labels and tone across the board.",
        },
        "card-5": {
            "id": "card-5",
            "title": "Design card layout",
            "details": "Add hierarchy and spacing for scanning dense lists.",
        },
        "card-6": {
            "id": "card-6",
            "title": "QA micro-interactions",
            "details": "Verify hover, focus, and loading states.",
        },
        "card-7": {
            "id": "card-7",
            "title": "Ship marketing page",
            "details": "Final copy approved and asset pack delivered.",
        },
        "card-8": {
            "id": "card-8",
            "title": "Close onboarding sprint",
            "details": "Document release notes and share internally.",
        },
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    created_at = utc_now()

    with connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS boards (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                board_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )

        conn.execute(
            """
            INSERT INTO users (username, password_hash, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO NOTHING
            """,
            (MVP_USERNAME, hash_password(MVP_PASSWORD), created_at),
        )

        user_id_row = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (MVP_USERNAME,),
        ).fetchone()

        if user_id_row:
            conn.execute(
                """
                INSERT INTO boards (user_id, board_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO NOTHING
                """,
                (user_id_row["id"], json.dumps(DEFAULT_BOARD), created_at),
            )


def validate_credentials(db_path: Path, username: str, password: str) -> bool:
    # MVP requirement: login is hardcoded to user/password.
    if username != MVP_USERNAME or password != MVP_PASSWORD:
        return False

    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    return row is not None


def get_board_for_user(db_path: Path, username: str) -> dict[str, Any]:
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT b.board_json
            FROM boards b
            INNER JOIN users u ON u.id = b.user_id
            WHERE u.username = ?
            """,
            (username,),
        ).fetchone()

    if not row:
        raise ValueError("Board not found for user")

    return json.loads(row["board_json"])


def replace_board_for_user(db_path: Path, username: str, board: dict[str, Any]) -> None:
    with connect(db_path) as conn:
        updated = conn.execute(
            """
            UPDATE boards
            SET board_json = ?, updated_at = ?
            WHERE user_id = (SELECT id FROM users WHERE username = ?)
            """,
            (json.dumps(board), utc_now(), username),
        )

    if updated.rowcount == 0:
        raise ValueError("Board not found for user")
