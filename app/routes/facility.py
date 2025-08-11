from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Facility, FacilityStatus, Court
from app.utils import role_required  # custom decorator

bp = Blueprint("facility", __name__, url_prefix="/facilities")

# --------------------
# List all facilities (public)
# --------------------
@bp.route("/")
def list_facilities():
    facilities = Facility.query.filter(Facility.status == FacilityStatus.approved).all()
    return render_template("facility_list.html", facilities=facilities)

# --------------------
# Add a new facility (owner/admin)
# --------------------
@bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("owner", "admin")
def add_facility():
    if request.method == "POST":
        facility = Facility(
            owner_id=current_user.id,
            name=request.form["name"],
            location=request.form["location"],
            description=request.form.get("description", ""),
            status=FacilityStatus.pending
        )
        db.session.add(facility)
        db.session.commit()
        flash("Facility submitted for approval.")
        return redirect(url_for("facility.list_facilities"))

    return render_template("facility_form.html")

# --------------------
# Add a court to an existing facility
# --------------------
@bp.route("/<int:facility_id>/courts/new", methods=["GET", "POST"])
@login_required
@role_required("owner", "admin")
def add_court(facility_id):
    facility = Facility.query.get_or_404(facility_id)
    if facility.owner_id != current_user.id and current_user.role.value != "admin":
        flash("You do not own this facility.")
        return redirect(url_for("facility.list_facilities"))

    if request.method == "POST":
        court = Court(
            facility_id=facility.id,
            name=request.form["name"],
            sport_type=request.form["sport_type"],
            price_per_hour=float(request.form["price_per_hour"])
        )
        db.session.add(court)
        db.session.commit()
        flash("Court added successfully.")
        return redirect(url_for("facility.list_facilities"))

    return render_template("court_form.html", facility=facility)
