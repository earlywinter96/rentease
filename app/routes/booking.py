from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Facility, Court, FacilityStatus, db
from datetime import datetime

bp = Blueprint("booking", __name__, url_prefix="/bookings")

# --------------------------
# List Facilities (Searchable)
# --------------------------
@bp.route("/facilities")
@login_required
def list_facilities():
    search_query = request.args.get("q", "").strip()
    query = Facility.query.filter(Facility.status == FacilityStatus.approved)

    if search_query:
        query = query.filter(Facility.name.ilike(f"%{search_query}%"))

    facilities = query.all()
    return render_template("bookings/facility_list.html", facilities=facilities, search_query=search_query)


# --------------------------
# View Facility Details
# --------------------------
@bp.route("/facility/<int:facility_id>")
@login_required
def view_facility(facility_id):
    facility = Facility.query.get_or_404(facility_id)
    courts = Court.query.filter_by(facility_id=facility.id).all()
    return render_template("bookings/facility_details.html", facility=facility, courts=courts)


# --------------------------
# Add Facility (Admin/Owner)
# --------------------------
@bp.route("/facilities/add", methods=["GET", "POST"])
@login_required
def add_facility():
    if current_user.role not in ["admin", "owner"]:
        flash("You are not authorized to add a facility.", "danger")
        return redirect(url_for("booking.list_facilities"))

    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        description = request.form["description"]
        image_url = request.form.get("image_url")
        
        new_facility = Facility(
            name=name,
            location=location,
            description=description,
            image_url=image_url,
            status=FacilityStatus.pending,
            owner_id=current_user.id
        )
        db.session.add(new_facility)
        db.session.commit()
        flash("Facility added successfully. Pending approval.", "success")
        return redirect(url_for("booking.list_facilities"))

    return render_template("bookings/facility_form.html")


# --------------------------
# Edit Facility
# --------------------------
@bp.route("/facility/<int:facility_id>/edit", methods=["GET", "POST"])
@login_required
def edit_facility(facility_id):
    facility = Facility.query.get_or_404(facility_id)

    if current_user.role not in ["admin", "owner"] or (facility.owner_id != current_user.id and current_user.role != "admin"):
        flash("You are not authorized to edit this facility.", "danger")
        return redirect(url_for("booking.list_facilities"))

    if request.method == "POST":
        facility.name = request.form["name"]
        facility.location = request.form["location"]
        facility.description = request.form["description"]
        facility.image_url = request.form.get("image_url")
        db.session.commit()
        flash("Facility updated successfully.", "success")
        return redirect(url_for("booking.view_facility", facility_id=facility.id))

    return render_template("bookings/facility_form.html", facility=facility)


# --------------------------
# Book a Court
# --------------------------
@bp.route("/court/<int:court_id>/book", methods=["POST"])
@login_required
def book_court(court_id):
    court = Court.query.get_or_404(court_id)
    date = request.form["date"]
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]

    # TODO: Add booking logic here
    flash(f"Court '{court.name}' booked for {date} from {start_time} to {end_time}", "success")
    return redirect(url_for("booking.view_facility", facility_id=court.facility_id))


@bp.route("/my-bookings")
@login_required
def my_bookings():
    # Fetch only bookings of the current user
    user_bookings = []  # Replace with actual query when Booking model exists
    return render_template("bookings/my_bookings.html", bookings=user_bookings)

# --------------------------
# Admin: Facility Approval Panel
# --------------------------
@bp.route("/admin/facilities")
@login_required
def admin_facilities():
    if current_user.role != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("booking.list_facilities"))

    facilities = Facility.query.order_by(Facility.id.desc()).all()
    return render_template("bookings/admin_facilities.html", facilities=facilities)


@bp.route("/admin/facilities/<int:facility_id>/status", methods=["POST"])
@login_required
def admin_update_facility_status(facility_id):
    if current_user.role != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("booking.list_facilities"))

    facility = Facility.query.get_or_404(facility_id)
    action = request.form.get("action")

    if action == "approve":
        facility.status = FacilityStatus.approved
    elif action == "reject":
        facility.status = FacilityStatus.rejected
    elif action == "pending":
        facility.status = FacilityStatus.pending
    else:
        flash("Invalid action.", "warning")
        return redirect(url_for("booking.admin_facilities"))

    db.session.commit()
    flash(f"Facility '{facility.name}' status updated to {facility.status.value}.", "success")
    return redirect(url_for("booking.admin_facilities"))


# --------------------------
# Admin: Booking Overview
# --------------------------
@bp.route("/admin/bookings")
@login_required
def admin_bookings():
    if current_user.role != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("booking.list_facilities"))

    from app.models import Booking  # Import here to avoid circular import
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    return render_template("bookings/admin_bookings.html", bookings=bookings)


@bp.route("/admin/bookings/<int:booking_id>/action", methods=["POST"])
@login_required
def admin_booking_action(booking_id):
    if current_user.role != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("booking.list_facilities"))

    from app.models import Booking, BookingStatus
    booking = Booking.query.get_or_404(booking_id)
    action = request.form.get("action")

    if action == "confirm":
        booking.status = BookingStatus.confirmed
    elif action == "complete":
        booking.status = BookingStatus.completed
    elif action == "cancel":
        booking.status = BookingStatus.cancelled
    else:
        flash("Invalid action.", "warning")
        return redirect(url_for("booking.admin_bookings"))

    db.session.commit()
    flash(f"Booking #{booking.id} updated to {booking.status.value}.", "success")
    return redirect(url_for("booking.admin_bookings"))

