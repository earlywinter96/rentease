# app/routes/main.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import date
from app import db
from app.models import User, Booking, Court, Facility, UserRole, BookingStatus

main = Blueprint("main", __name__)

# -------------------- Redirect old auth paths --------------------
@main.route("/register")
def redirect_register():
    return redirect(url_for("auth.register"))

@main.route("/login")
def redirect_login():
    return redirect(url_for("auth.login"))

# -------------------- Dashboard --------------------
@main.route("/dashboard")
@login_required
def dashboard():
    """
    Role-based scoping:
      - admin: everything
      - owner: only their facilities & related bookings
      - user: only their bookings
    """

    booking_filters = []
    join_court = False
    join_facility = False

    if current_user.role == UserRole.owner:
        join_court = True
        join_facility = True
        booking_filters.append(Facility.owner_id == current_user.id)
    elif current_user.role == UserRole.user:
        booking_filters.append(Booking.user_id == current_user.id)

    def booking_query(agg_func):
        query = db.session.query(agg_func)
        if join_facility:
            query = query.join(Court, Booking.court_id == Court.id) \
                         .join(Facility, Court.facility_id == Facility.id)
        elif join_court:
            query = query.join(Court, Booking.court_id == Court.id)
        return query.filter(*booking_filters)

    total_rentals = booking_query(func.count(Booking.id)).scalar() or 0
    total_revenue = booking_query(func.coalesce(func.sum(Booking.total_price), 0)).scalar() or 0
    active_rentals = booking_query(func.count(Booking.id)) \
        .filter(Booking.status == BookingStatus.confirmed).scalar() or 0
    late_returns = booking_query(func.count(Booking.id)) \
        .filter(Booking.date < date.today(), Booking.status == BookingStatus.confirmed).scalar() or 0

    top_products_q = db.session.query(
        Court.name,
        func.count(Booking.id).label("rentals")
    ).join(Booking, Booking.court_id == Court.id)

    if join_facility:
        top_products_q = top_products_q.join(Facility, Court.facility_id == Facility.id).filter(*booking_filters)
    elif current_user.role == UserRole.user:
        top_products_q = top_products_q.filter(Booking.user_id == current_user.id)

    top_products = top_products_q.group_by(Court.name) \
                                 .order_by(func.count(Booking.id).desc()) \
                                 .limit(6).all()

    revenue_trends_q = db.session.query(
        func.to_char(Booking.date, "Mon").label("month"),
        func.coalesce(func.sum(Booking.total_price), 0).label("revenue")
    )

    if join_facility:
        revenue_trends_q = revenue_trends_q.join(Court, Booking.court_id == Court.id) \
                                           .join(Facility, Court.facility_id == Facility.id) \
                                           .filter(*booking_filters)
    elif current_user.role == UserRole.user:
        revenue_trends_q = revenue_trends_q.filter(Booking.user_id == current_user.id)

    revenue_trends = revenue_trends_q.group_by("month") \
                                     .order_by(func.min(Booking.date)).all()

    top_customers = []
    if current_user.role in (UserRole.admin, UserRole.owner):
        customers_q = db.session.query(
            User.name,
            func.count(Booking.id).label("total_orders"),
            func.coalesce(func.sum(Booking.total_price), 0).label("total_spent"),
            func.max(Booking.date).label("last_order")
        ).join(Booking, Booking.user_id == User.id)

        if join_facility:
            customers_q = customers_q.join(Court, Booking.court_id == Court.id) \
                                     .join(Facility, Court.facility_id == Facility.id) \
                                     .filter(*booking_filters)

        top_customers = customers_q.group_by(User.id) \
                                   .order_by(func.sum(Booking.total_price).desc()) \
                                   .limit(6).all()

    return render_template(
        "bookings/dashboard.html",
        total_rentals=int(total_rentals),
        total_revenue=float(total_revenue),
        active_rentals=int(active_rentals),
        late_returns=int(late_returns),
        top_products=top_products,
        revenue_trends=revenue_trends,
        top_customers=top_customers,
        role=current_user.role.value if isinstance(current_user.role, UserRole) else str(current_user.role)
    )

# -------------------- Home --------------------
@main.route("/")
def home():
    return render_template("bookings/index.html")
