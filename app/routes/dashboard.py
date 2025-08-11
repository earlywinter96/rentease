from sqlalchemy import func
from flask_login import login_required
from app.models import db, Booking, Court, User

@main.route("/dashboard")
@login_required
def dashboard():
    # KPIs
    total_rentals = db.session.query(func.count(Booking.id)).scalar() or 0
    total_revenue = db.session.query(func.coalesce(func.sum(Booking.total_price), 0)).scalar() or 0
    active_rentals = db.session.query(func.count(Booking.id)).filter(Booking.status == "confirmed").scalar() or 0
    late_returns = 0  # Add logic later if you want

    # Most Rented Products
    top_products = db.session.query(
        Court.name,
        func.count(Booking.id).label("rentals")
    ).join(Booking).group_by(Court.name).order_by(func.count(Booking.id).desc()).limit(5).all()

    # Revenue Trends by Month
    revenue_trends = db.session.query(
        func.to_char(Booking.date, 'Mon').label("month"),
        func.sum(Booking.total_price).label("revenue")
    ).group_by("month").order_by(func.min(Booking.date)).all()

    # Top Customers
    top_customers = db.session.query(
        User.name,
        func.count(Booking.id).label("total_orders"),
        func.sum(Booking.total_price).label("total_spent"),
        func.max(Booking.date).label("last_order")
    ).join(Booking).group_by(User.id).order_by(func.sum(Booking.total_price).desc()).limit(5).all()

    return render_template(
        "bookings/dashboard.html",
        total_rentals=total_rentals,
        total_revenue=total_revenue,
        active_rentals=active_rentals,
        late_returns=late_returns,
        top_products=top_products,
        revenue_trends=revenue_trends,
        top_customers=top_customers
    )
