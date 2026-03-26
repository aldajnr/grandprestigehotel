# User model

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db


def create_user(username: str, password: str, role: str):
    db = get_db()
    db.execute(
        "INSERT INTO users(username, password_hash, role, created_at) VALUES (?,?,?,?)",
        (username.strip().lower(), generate_password_hash(password), role, datetime.utcnow().isoformat())
    )
    db.commit()


def get_user_by_username(username: str):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE username=?", (username.strip().lower(),)).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None


def list_users():
    db = get_db()
    # Include password_hash so admin can inspect it (shown masked in UI)
    return [dict(r) for r in db.execute(
        "SELECT id, username, role, password_hash, created_at FROM users ORDER BY id DESC"
    ).fetchall()]


def delete_user(user_id: int):
    db = get_db()
    db.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()


def update_user_role(user_id: int, new_role: str):
    db = get_db()
    db.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
    db.commit()


def update_user_password(user_id: int, new_password: str):
    db = get_db()
    db.execute("UPDATE users SET password_hash=? WHERE id=?",
               (generate_password_hash(new_password), user_id))
    db.commit()


def verify_password(hash_: str, password: str) -> bool:
    return check_password_hash(hash_, password)
