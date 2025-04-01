#for all the url endpoints
from flask import Blueprint, render_template,  redirect, url_for, request, flash
from flask_login import login_required, current_user
from . import db
from .models import TrainBooking, FlightBooking, TravelGroup

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("index.html", user=current_user)

@views.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template("contact.html")

@views.route('/packages')
def packages():
    return render_template("packages.html")

@views.route('/groups')
def view_groups():
    groups = TravelGroup.query.all()
    return render_template('travelgroups.html', groups=groups)

@views.route('/creategroup', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        contact_info = request.form.get('contact_info')
        destinations = request.form.get('destinations')

        # Create a new group
        new_group = TravelGroup(
            name=name,
            description=description,
            contact_info=contact_info,
            destinations=destinations,
            leader_id=current_user.id
        )

        new_group.members.append(current_user)


        db.session.add(new_group)
        db.session.commit()
        return redirect(url_for('views.view_groups'))

    return render_template('create_group.html', user=current_user)

@views.route('/join_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def join_group(group_id):
    group = TravelGroup.query.get_or_404(group_id)

    # Check if user is already a member
    if current_user in group.members:
        return redirect(url_for('views.view_groups'))

    # Add user to group
    group.members.append(current_user)
    db.session.commit()

    return redirect(url_for('views.view_groups'))

@views.route('/leave_travel_group/<int:group_id>', methods=['POST'])
@login_required
def leave_travel_group(group_id):
    group = TravelGroup.query.get_or_404(group_id)

    if current_user not in group.members:
        flash("You are not a member of this group.", 'danger')
        return redirect(url_for('views.dashboard'))

    group.members.remove(current_user)
    db.session.commit()

    flash("You have left the group.", 'success')
    return redirect(url_for('views.dashboard'))


@views.route('/dashboard')
@login_required
def dashboard():
    train_bookings = TrainBooking.query.filter_by(user_id=current_user.id).all()
    flight_bookings = FlightBooking.query.filter_by(user_id=current_user.id).all()
    travel_groups = TravelGroup.query.filter(TravelGroup.members.any(id=current_user.id)).all()

    return render_template(
        "dashboard.html", 
        user=current_user, 
        train_bookings=train_bookings, 
        flight_bookings=flight_bookings, 
        travel_groups=travel_groups
    )