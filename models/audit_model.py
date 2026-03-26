# Audit log model

from datetime import datetime
from models import db as D


def add_log(user_id, username, role, action, record_id="", ip="", notes=""):
    D.execute(
        """INSERT INTO audit_logs(user_id, username, role, action, record_id, ip_address, notes, created_at)
           VALUES (?,?,?,?,?,?,?,?)""",
        (user_id, username, role, action, str(record_id or ""), ip, notes, datetime.utcnow().isoformat())
    )
    D.commit()


def list_logs(limit=300):
    return D.fetchall(
        "SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,)
    )
