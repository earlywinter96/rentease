from datetime import datetime, date, time as dtime, timedelta
from app import create_app, db
from app.models import User, Facility, Court, Booking, Review, UserRole, FacilityStatus, BookingStatus

def main():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Users
        admin = User(name="Admin", email="admin@demo.com", role=UserRole.admin)
        admin.set_password("Admin@123")

        owner = User(name="Owner One", email="owner@demo.com", role=UserRole.owner)
        owner.set_password("Owner@123")

        user = User(name="Customer One", email="user@demo.com", role=UserRole.user)
        user.set_password("User@123")

        db.session.add_all([admin, owner, user])
        db.session.commit()

        # Facility (approved)
        fac = Facility(
            owner_id=owner.id,
            name="Ace Sports Arena",
            location="Sector 21, Noida",
            description="Indoor badminton and table tennis",
            status=FacilityStatus.approved,
        )
        db.session.add(fac)
        db.session.commit()

        # Court
        court = Court(
            facility_id=fac.id,
            name="Badminton Court 1",
            sport_type="badminton",
            price_per_hour=200,
            open_time=dtime(6, 0),
            close_time=dtime(22, 0),
        )
        db.session.add(court)
        db.session.commit()

        # One booking for today 7–8 AM
        today = date.today()
        booking = Booking(
            user_id=user.id,
            court_id=court.id,
            date=today,
            start_time=dtime(7, 0),
            end_time=dtime(8, 0),
            status=BookingStatus.confirmed,
            total_price=200,
        )
        db.session.add(booking)

        # One review
        rev = Review(
            user_id=user.id,
            facility_id=fac.id,
            rating=5,
            comment="Great court and clean facility!"
        )
        db.session.add(rev)

        db.session.commit()
        print("Seed complete. Demo users: admin@demo.com/Admin@123, owner@demo.com/Owner@123, user@demo.com/User@123")

if __name__ == "__main__":
    main()
