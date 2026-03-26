# Audit logs — Admin only
from flask import Blueprint, render_template, session
from utils.decorators import login_required, role_required
from models.audit_model import list_logs
from services.audit_service import log as audit

audit_bp = Blueprint("audit", __name__, url_prefix="/audit")


@audit_bp.route("/")
@login_required
@role_required("Admin")
def audit_page():
    logs = list_logs(limit=500)
    audit("AUDIT_LOG_VIEW", notes="Full audit trail accessed by Admin")
    return render_template("audit.html", logs=logs)
