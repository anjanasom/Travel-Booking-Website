#db schema
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    bookings = db.relationship('Booking', backref='user', lazy=True, cascade="all, delete")
