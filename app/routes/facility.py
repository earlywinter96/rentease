# app/routes/facility.py
from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func, or_
from decimal import Decimal
from app import db
from app.models import Facility, Court, FacilityStatus

bp = Blueprint("facility", __name__, url_prefix="/rentals")


@bp.route("/", methods=["GET"])
def list_rentals():
    """
    Public rentals listing with optional filters.
    Query params:
      - q          (search text)
      - location   (string)
      - sport      (string)
      - price_min  (decimal)
      - price_max  (decimal)
      - page       (int)
    """
    q = (request.args.get("q") or "").strip()
    location = (request.args.get("location") or "").strip()
    sport = (request.args.get("sport") or "").strip()

    try:
        price_min = Decimal(request.args.get("price_min")) if request.args.get("price_min") else None
        price_max = Decimal(request.args.get("price_max")) if request.args.get("price_max") else None
    except Exception:
        price_min = price_max = None

    page = max(int(request.args.get("page", 1)), 1)
    per_page = int(current_app.config.get("ITEMS_PER_PAGE", 12))

    # Subquery to get min price per facility
    subq = (
        db.session.query(
            Court.facility_id.label("facility_id"),
            func.min(Court.price_per_hour).label("min_price")
        )
        .group_by(Court.facility_id)
        .subquery()
    )

    # Base query with price
    query = (
        db.session.query(Facility, subq.c.min_price)
        .outerjoin(subq, Facility.id == subq.c.facility_id)
        .filter(Facility.status == FacilityStatus.approved)
    )

    # Filters
    if q:
        like_q = f"%{q}%"
        query = query.filter(
            or_(Facility.name.ilike(like_q), Facility.description.ilike(like_q))
        )

    if location:
        query = query.filter(Facility.location.ilike(f"%{location}%"))

    if sport:
        query = query.join(Court).filter(Court.sport_type.ilike(f"%{sport}%"))

    if price_min is not None:
        query = query.filter(subq.c.min_price >= price_min)

    if price_max is not None:
        query = query.filter(subq.c.min_price <= price_max)

    # Sorting
    query = query.order_by(
        subq.c.min_price.asc().nulls_last(),
        Facility.name.asc()
    )

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    results = [
        {
            "facility": facility,
            "starting_price": float(min_price) if min_price is not None else None
        }
        for facility, min_price in pagination.items
    ]

    return render_template(
        "rentals/list.html",
        results=results,
        pagination=pagination,
        q=q,
        location=location,
        sport=sport,
        price_min=str(price_min) if price_min is not None else "",
        price_max=str(price_max) if price_max is not None else "",
    )


@bp.route("/<int:facility_id>")
def rental_detail(facility_id):
    """Public facility details page."""
    facility = Facility.query.get_or_404(facility_id)
    courts = facility.courts or []
    prices = [c.price_per_hour for c in courts if c.price_per_hour is not None]
    starting_price = float(min(prices)) if prices else None

    return render_template(
        "rentals/detail.html",
        facility=facility,
        courts=courts,
        starting_price=starting_price
    )


# ---------------------------
# ADMIN: Facility Approval Panel
# ---------------------------
@bp.route("/admin/facility-approvals", methods=["GET", "POST"])
@login_required
def facility_approvals():
    """Admin-only page for approving or rejecting facilities."""
    if current_user.role != "admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("facility.list_rentals"))

    if request.method == "POST":
        facility_id = request.form.get("facility_id")
        action = request.form.get("action")

        facility = Facility.query.get_or_404(facility_id)

        if action == "approve":
            facility.status = FacilityStatus.approved
            flash(f"✅ Facility '{facility.name}' approved.", "success")
        elif action == "reject":
            facility.status = FacilityStatus.rejected
            flash(f"❌ Facility '{facility.name}' rejected.", "danger")

        db.session.commit()
        return redirect(url_for("facility.facility_approvals"))

    pending_facilities = Facility.query.filter_by(status=FacilityStatus.pending).all()
    return render_template("bookings/admin_facilities.html", facilities=pending_facilities)
