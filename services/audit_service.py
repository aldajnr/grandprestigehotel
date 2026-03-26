# Central audit function used by routes

from flask import request, session
from models.audit_model import add_log

def log(action: str, record_id: str = "", notes: str = ""):
    add_log(
        session.get("user_id"),
        session.get("username"),
        session.get("role"),
        action,
        record_id=record_id,
        ip=request.remote_addr or "",
        notes=notes
    )
