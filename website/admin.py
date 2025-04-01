from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import User, TrainBooking, FlightBooking, TravelGroup, HotelBooking
from . import db

admin = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to restrict access to admins only."""
    from functools import wraps
    from flask import abort

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin-dashboard')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    train_bookings = TrainBooking.query.all()
    flight_bookings = FlightBooking.query.all()
    hotel_bookings = HotelBooking.query.all()
    groups = TravelGroup.query.all()
    return render_template('admin_dashboard.html', users=users, train_bookings=train_bookings, flight_bookings=flight_bookings, hotel_bookings=hotel_bookings, groups=groups)

@admin.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/admin/delete_booking/<string:booking_type>/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def delete_booking(booking_type, booking_id):
    if booking_type == "train":
        booking = TrainBooking.query.get_or_404(booking_id)
    else:
        booking = FlightBooking.query.get_or_404(booking_id)
    
    db.session.delete(booking)
    db.session.commit()
    flash(f"{booking_type.capitalize()} booking deleted!", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/admin/delete_group/<int:group_id>', methods=['POST'])
@login_required
@admin_required
def delete_group(group_id):
    group = TravelGroup.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash("Group deleted successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))
