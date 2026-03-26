# Route guards (login + role)

from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Must login first
        if not session.get("user_id"):
            flash("Please login to continue.", "warning")
            return redirect(url_for("auth.login"))
        # Must verify OTP
        if not session.get("otp_verified"):
            flash("Please verify OTP to continue.", "warning")
            return redirect(url_for("auth.otp"))
        return fn(*args, **kwargs)
    return wrapper

def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if session.get("role") not in roles:
                flash("Access denied.", "danger")
                return redirect(url_for("dashboard.home"))
            return fn(*args, **kwargs)
        return wrapper
    return deco
