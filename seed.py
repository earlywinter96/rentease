# seed.py
import random
from datetime import datetime, timedelta
from faker import Faker

from app import create_app, db
from app.models import User, Facility, Court, Booking, UserRole, FacilityStatus, BookingStatus

fake = Faker()

app = create_app()
app.app_context().push()

def seed_data():
    db.drop_all()
    db.create_all()

    # --- Create Users ---
    users = []
    for _ in range(5):  # customers
        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            role=UserRole.user
        )
        user.set_password("password")
        users.append(user)
        db.session.add(user)

    owners = []
    for _ in range(2):  # owners
        owner = User(
            name=fake.name(),
            email=fake.unique.email(),
            role=UserRole.owner
        )
        owner.set_password("password")
        owners.append(owner)
        db.session.add(owner)

    db.session.commit()

    # --- Create Facilities & Courts ---
    courts = []
    for owner in owners:
        facility = Facility(
            owner_id=owner.id,
            name=fake.company(),
            location=fake.city(),
            description=fake.text(),
            status=FacilityStatus.approved
        )
        db.session.add(facility)
        db.session.commit()

        for _ in range(3):  # courts per facility
            court = Court(
                facility_id=facility.id,
                name=f"{fake.word().capitalize()} Court",
                sport_type=random.choice(["Tennis", "Badminton", "Football", "Basketball"]),
                price_per_hour=random.randint(200, 800)
            )
            db.session.add(court)
            courts.append(court)

    db.session.commit()

    # --- Create Bookings ---
    for _ in range(50):
        user = random.choice(users)
        court = random.choice(courts)
        date = datetime.utcnow().date() - timedelta(days=random.randint(0, 60))
        start_hour = random.choice(range(6, 20))
        end_hour = start_hour + random.choice([1, 2, 3])
        total_price = (end_hour - start_hour) * float(court.price_per_hour)

        booking = Booking(
            user_id=user.id,
            court_id=court.id,
            date=date,
            start_time=datetime.strptime(f"{start_hour}:00", "%H:%M").time(),
            end_time=datetime.strptime(f"{end_hour}:00", "%H:%M").time(),
            status=random.choice(list(BookingStatus)),
            total_price=total_price
        )
        db.session.add(booking)

    db.session.commit()
    print("✅ Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
