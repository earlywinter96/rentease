from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Court, Booking

bp = Blueprint("booking", __name__, url_prefix="/bookings")

# --------------------
# Book a court
# --------------------
@bp.route("/court/<int:court_id>", methods=["GET", "POST"])
@login_required
def book_court(court_id):
    court = Court.query.get_or_404(court_id)

    if request.method == "POST":
        date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        start_time = datetime.strptime(request.form["start_time"], "%H:%M").time()
        end_time = datetime.strptime(request.form["end_time"], "%H:%M").time()

        # Check for overlapping bookings
        existing = Booking.query.filter_by(court_id=court.id, date=date).all()
        for b in existing:
            if b.overlaps(start_time, end_time):
                flash("Selected time slot is already booked.")
                return redirect(url_for("booking.book_court", court_id=court.id))

        # Calculate price
        hours = (datetime.combine(date, end_time) - datetime.combine(date, start_time)).seconds / 3600
        total_price = hours * float(court.price_per_hour)

        booking = Booking(
            user_id=current_user.id,
            court_id=court.id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            total_price=total_price
        )
        db.session.add(booking)
        db.session.commit()
        flash("Booking confirmed!")
        return redirect(url_for("booking.my_bookings"))

    return render_template("book_court.html", court=court)

# --------------------
# My bookings
# --------------------
@bp.route("/my")
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.date.desc()).all()
    return render_template("my_bookings.html", bookings=bookings)
