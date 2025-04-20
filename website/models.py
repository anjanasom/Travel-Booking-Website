from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    train_bookings = db.relationship('TrainBooking', backref='user', lazy=True, cascade="all, delete")
    flight_bookings = db.relationship('FlightBooking', backref='user', lazy=True, cascade="all, delete")
    
    # Many-to-Many Relationship with TravelGroup
    groups = db.relationship('TravelGroup', secondary='group_members', back_populates='members')

class TrainBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    train_number = db.Column(db.String(10), nullable=False)
    from_station = db.Column(db.String(10), nullable=False)
    to_station = db.Column(db.String(10), nullable=False)
    class_type = db.Column(db.String(5), nullable=False)
    travel_date = db.Column(db.Date, nullable=False)
    total_fare = db.Column(db.Float, nullable=False)
    seat_status = db.Column(db.String(20), nullable=False)  # Confirmed, Waiting, etc.
    booked_at = db.Column(db.DateTime(timezone=True), default=func.now())

class FlightBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flight_number = db.Column(db.String(20), nullable=False)
    from_city = db.Column(db.String(50), nullable=False)
    to_city = db.Column(db.String(50), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)  # Nullable for one-way trips
    travel_class = db.Column(db.String(10), nullable=False)
    total_fare = db.Column(db.Float, nullable=False)
    seat_status = db.Column(db.String(20), nullable=False)  # Confirmed, Waiting, etc.
    booked_at = db.Column(db.DateTime(timezone=True), default=func.now())

class TravelGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    contact_info = db.Column(db.String(100), nullable=False)  # Contact info (Phone number)
    destinations = db.Column(db.String(255), nullable=False)  # Destinations
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who created the group
    leader = db.relationship('User', backref='created_groups', lazy=True)  # Relationship to the leader
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())

    # Corrected Many-to-Many Relationship
    members = db.relationship('User', secondary='group_members', back_populates='groups')

class GroupMembers(db.Model):
    __tablename__ = 'group_members'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('travel_group.id'), nullable=False)

class HotelBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.String(100), nullable=False)
    hotel_name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    checkin_date = db.Column(db.Date, nullable=False)
    checkout_date = db.Column(db.Date, nullable=False)
    booking_status = db.Column(db.String(20), default="Pending")

