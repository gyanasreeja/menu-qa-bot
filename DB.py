"""SQLite storage: users (hashed passwords) and per-user search history."""
import hashlib
import hmac
import os
import re
import sqlite3

DB_PATH = "app.db"
ITERATIONS = 200_000


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with _conn() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                salt BLOB NOT NULL,
                pw_hash BLOB NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )


def _hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)


def register_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,30}", username):
        return False, "Username must be 3-30 characters: letters, numbers, _ . -"
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    salt = os.urandom(16)
    try:
        with _conn() as c:
            c.execute(
                "INSERT INTO users (username, salt, pw_hash) VALUES (?, ?, ?)",
                (username, salt, _hash(password, salt)),
            )
    except sqlite3.IntegrityError:
        return False, "That username is already taken."
    return True, "Account created! You can log in now."


def authenticate(username: str, password: str):
    """Returns {'id', 'username'} on success, else None."""
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()
    if row and hmac.compare_digest(row["pw_hash"], _hash(password, row["salt"])):
        return {"id": row["id"], "username": row["username"]}
    return None


def save_search(user_id: int, question: str, answer: str):
    with _conn() as c:
        c.execute(
            "INSERT INTO searches (user_id, question, answer) VALUES (?, ?, ?)",
            (user_id, question, answer),
        )


def get_history(user_id: int, limit: int = 100):
    """Newest first."""
    with _conn() as c:
        rows = c.execute(
            "SELECT id, question, answer, created_at FROM searches "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_search(user_id: int, search_id: int):
    with _conn() as c:
        c.execute(
            "DELETE FROM searches WHERE id = ? AND user_id = ?", (search_id, user_id)
        )


def clear_history(user_id: int):
    with _conn() as c:
        c.execute("DELETE FROM searches WHERE user_id = ?", (user_id,))