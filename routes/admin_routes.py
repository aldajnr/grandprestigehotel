# Admin-only routes: staff account management + password view/reset
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, role_required
from utils.validators import is_zetech_email
from models.user_model import (list_users, create_user, get_user_by_id,
                                delete_user, update_user_role,
                                update_user_password, get_user_by_username)
from services.audit_service import log as audit

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
ROLES = ["Admin", "Manager", "Receptionist"]


@admin_bp.route("/users")
@login_required
@role_required("Admin")
def users():
    all_users = list_users()
    audit("ADMIN_USERS_VIEW", notes="Staff list viewed")
    return render_template("admin_users.html", users=all_users, roles=ROLES)


@admin_bp.route("/users/create", methods=["POST"])
@login_required
@role_required("Admin")
def create_staff():
    username = (request.form.get("username") or "").strip().lower()
    password = (request.form.get("password") or "").strip()
    role     = (request.form.get("role") or "").strip()
    if not username or not password or role not in ROLES:
        flash("All fields required.", "danger")
        return redirect(url_for("admin.users"))
    if not is_zetech_email(username):
        flash("Email must end with @zetech.ac.ke", "danger")
        return redirect(url_for("admin.users"))
    if len(password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for("admin.users"))
    if get_user_by_username(username):
        flash("That email is already registered.", "danger")
        return redirect(url_for("admin.users"))
    create_user(username, password, role)
    audit("STAFF_CREATED", notes="Created: " + username)
    flash("Account created for " + username, "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:uid>/role", methods=["POST"])
@login_required
@role_required("Admin")
def change_role(uid):
    new_role = (request.form.get("role") or "").strip()
    if new_role not in ROLES:
        flash("Invalid role.", "danger")
        return redirect(url_for("admin.users"))
    if uid == session["user_id"]:
        flash("Cannot change your own role.", "danger")
        return redirect(url_for("admin.users"))
    update_user_role(uid, new_role)
    audit("STAFF_ROLE_CHANGED", record_id=str(uid), notes="Role -> " + new_role)
    flash("Role updated.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:uid>/reset-password", methods=["POST"])
@login_required
@role_required("Admin")
def admin_reset_password(uid):
    """Admin directly sets a new password for any staff account."""
    new_pass = (request.form.get("new_password") or "").strip()
    confirm  = (request.form.get("confirm_password") or "").strip()
    u = get_user_by_id(uid)
    if not u:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))
    if len(new_pass) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for("admin.users"))
    if new_pass != confirm:
        flash("Passwords do not match.", "danger")
        return redirect(url_for("admin.users"))
    update_user_password(uid, new_pass)
    audit("STAFF_PASSWORD_RESET", record_id=str(uid), notes="Admin reset password for: " + u["username"])
    flash("Password updated for " + u["username"], "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:uid>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def remove_staff(uid):
    if uid == session["user_id"]:
        flash("Cannot delete your own account.", "danger")
        return redirect(url_for("admin.users"))
    u = get_user_by_id(uid)
    if not u:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))
    delete_user(uid)
    audit("STAFF_DELETED", record_id=str(uid), notes="Deleted: " + (u["username"] or ""))
    flash("Account removed.", "success")
    return redirect(url_for("admin.users"))
