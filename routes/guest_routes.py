# Guest routes — strict RBAC
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, role_required
from models.guest_model import (
    create_guest, list_guests, list_current_guests, list_past_guests,
    get_guest_by_id, search_guests, cancel_guest, reschedule_guest, occupied_rooms
)
from services.audit_service import log as audit

guest_bp = Blueprint("guests", __name__, url_prefix="/guests")


@guest_bp.route("/")
@login_required
def guest_list():
    role = session.get("role")
    today = date.today().isoformat()

    # Admin sees ALL guests (present + past)
    # Manager sees present + past
    # Receptionist sees only CURRENT active guests + room availability
    if role == "Receptionist":
        guests = list_current_guests()
        past = []
    elif role == "Manager":
        guests = list_current_guests()
        past = list_past_guests()
    else:  # Admin
        guests = list_guests()
        past = []

    rooms_occupied = occupied_rooms()
    audit("GUEST_LIST_VIEW", notes="Guest list viewed")
    return render_template("guests.html",
        guests=guests, past=past,
        rooms_occupied=rooms_occupied,
        role=role, today=today
    )


@guest_bp.route("/search")
@login_required
def search():
    role = session.get("role")
    q = (request.args.get("q") or "").strip()
    results = []
    if q:
        results = search_guests(q)
        audit("GUEST_SEARCH", notes="Searched: " + q + " | Results: " + str(len(results)))
    today = date.today().isoformat()
    return render_template("guest_search.html", results=results, q=q, role=role, today=today)


@guest_bp.route("/register", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Receptionist", "Manager")
def register():
    if request.method == "POST":
        data = {
            "full_name":      (request.form.get("full_name") or "").strip(),
            "national_id":    (request.form.get("national_id") or "").strip(),
            "phone":          (request.form.get("phone") or "").strip(),
            "room":           (request.form.get("room") or "").strip(),
            "checkin_date":   (request.form.get("checkin_date") or "").strip(),
            "checkout_date":  (request.form.get("checkout_date") or "").strip(),
            "payment_method": (request.form.get("payment_method") or "").strip(),
            "notes":          (request.form.get("notes") or "").strip(),
        }
        for k in ["full_name", "national_id", "phone", "room", "checkin_date", "checkout_date"]:
            if not data[k]:
                flash("All required fields (*) must be filled including check-out date.", "danger")
                return render_template("register.html")
        if data["checkout_date"] <= data["checkin_date"]:
            flash("Check-out date must be after check-in date.", "danger")
            return render_template("register.html")
        guest_id = create_guest(data, created_by=session["user_id"])
        audit("GUEST_CREATED", record_id=str(guest_id),
              notes="Registered: " + data["full_name"] + " | Room " + data["room"])
        flash("Guest registered successfully.", "success")
        return redirect(url_for("guests.guest_list"))
    return render_template("register.html")


@guest_bp.route("/<int:gid>/cancel", methods=["POST"])
@login_required
@role_required("Admin", "Manager")
def cancel(gid):
    g = get_guest_by_id(gid)
    if not g:
        flash("Booking not found.", "danger")
        return redirect(url_for("guests.guest_list"))
    reason = (request.form.get("reason") or "").strip() or "No reason provided"
    cancel_guest(gid, cancelled_by=session["user_id"], reason=reason)
    audit("BOOKING_CANCELLED", record_id=str(gid),
          notes="Cancelled: " + g["full_name"] + " | Reason: " + reason)
    flash("Booking for " + g["full_name"] + " has been cancelled.", "success")
    return redirect(url_for("guests.guest_list"))


@guest_bp.route("/<int:gid>/reschedule", methods=["POST"])
@login_required
@role_required("Admin", "Manager")
def reschedule(gid):
    g = get_guest_by_id(gid)
    if not g:
        flash("Booking not found.", "danger")
        return redirect(url_for("guests.guest_list"))
    new_ci = (request.form.get("checkin_date") or "").strip()
    new_co = (request.form.get("checkout_date") or "").strip()
    if not new_ci or not new_co:
        flash("Both check-in and check-out dates are required.", "danger")
        return redirect(url_for("guests.guest_list"))
    if new_co <= new_ci:
        flash("Check-out must be after check-in.", "danger")
        return redirect(url_for("guests.guest_list"))
    old = g["checkin_date"] + " to " + g["checkout_date"]
    reschedule_guest(gid, new_ci, new_co)
    audit("BOOKING_RESCHEDULED", record_id=str(gid),
          notes=g["full_name"] + " | " + old + " -> " + new_ci + " to " + new_co)
    flash("Booking for " + g["full_name"] + " rescheduled.", "success")
    return redirect(url_for("guests.guest_list"))
