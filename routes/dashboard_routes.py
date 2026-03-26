# Dashboard — role-specific views
from datetime import date
from flask import Blueprint, render_template, session
from utils.decorators import login_required
from models.guest_model import list_guests, list_current_guests, occupied_rooms
from models.audit_model import list_logs

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def home():
    role = session.get("role")
    today = date.today().isoformat()
    all_guests = list_guests()
    current = list_current_guests()
    rooms = occupied_rooms()

    # Admin: recent activity + security stats
    recent_audit = []
    failed_logins = 0
    total_logs = 0
    if role == "Admin":
        recent_audit = list_logs(limit=10)
        all_logs = list_logs(limit=500)
        failed_logins = sum(1 for l in all_logs if l["action"] == "LOGIN_FAILED")
        total_logs = len(all_logs)

    return render_template("dashboard.html",
        role=role,
        today=today,
        total_guests=len(all_guests),
        current_guests=len(current),
        occupied_rooms=len(rooms),
        recent_audit=recent_audit,
        failed_logins=failed_logins,
        total_logs=total_logs,
    )
