from datetime import datetime, time
from enum import Enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class UserRole(str, Enum):
    user = "user"
    owner = "owner"
    admin = "admin"

class FacilityStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class BookingStatus(str, Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole, native_enum=False, length=16), nullable=False, default=UserRole.user)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    facilities = db.relationship("Facility", back_populates="owner", cascade="all, delete-orphan")
    bookings = db.relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Facility(db.Model):
    __tablename__ = "facilities"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(FacilityStatus, native_enum=False, length=16), nullable=False, default=FacilityStatus.pending)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    owner = db.relationship("User", back_populates="facilities")
    courts = db.relationship("Court", back_populates="facility", cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="facility", cascade="all, delete-orphan")

class Court(db.Model):
    __tablename__ = "courts"
    id = db.Column(db.Integer, primary_key=True)
    facility_id = db.Column(db.Integer, db.ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    sport_type = db.Column(db.String(50), nullable=False)
    price_per_hour = db.Column(db.Numeric(10, 2), nullable=False)
    open_time = db.Column(db.Time, nullable=False, default=time(6, 0))
    close_time = db.Column(db.Time, nullable=False, default=time(22, 0))

    facility = db.relationship("Facility", back_populates="courts")
    bookings = db.relationship("Booking", back_populates="court", cascade="all, delete-orphan")

class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    court_id = db.Column(db.Integer, db.ForeignKey("courts.id", ondelete="CASCADE"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum(BookingStatus, native_enum=False, length=16), nullable=False, default=BookingStatus.confirmed)
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="bookings")
    court = db.relationship("Court", back_populates="bookings")

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    facility_id = db.Column(db.Integer, db.ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="reviews")
    facility = db.relationship("Facility", back_populates="reviews")
