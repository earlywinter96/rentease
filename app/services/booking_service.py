from app.models import Booking, BookingStatus

def has_conflict(session, court_id, date, start_time, end_time):
    return session.query(Booking.id).filter(
        Booking.court_id == court_id,
        Booking.date == date,
        Booking.status == BookingStatus.confirmed,
        Booking.start_time < end_time,
        Booking.end_time > start_time,
    ).first() is not None
