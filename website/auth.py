#for backend user authentification
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category = 'success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect', category = 'error')
        else:
            flash('User does not exist', category = 'error')
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    is_admin = current_user.is_admin  # Save before logout
    logout_user()
    return redirect(url_for('auth.admin_login' if is_admin else 'views.home'))

@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already in use', category = 'error')
        elif len(email) < 4:
            flash("Email must be at least 4 characters.", category = "error")
        elif len(name) < 2:
            flash("Name must be at least 2 characters.", category = "error")
        elif password != confirm_password:
            flash("Passwords don't match.", category = "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters.", category = "error")
        else:
            admin_emails = {"admin7103@gmail.com", "another_admin@example.com"}  # Add emails here
            if email in admin_emails:
                new_user = User(email=email, name=name, password=generate_password_hash(password), is_admin=True)
            else:
                new_user = User(email=email, name=name, password=generate_password_hash(password))

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created!", category = "success")
            return redirect(url_for('views.home'))


    return render_template("signup.html", user=current_user)

@auth.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email, is_admin=True).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash("Invalid admin credentials", "error")

    return render_template("admin_login.html", user=current_user)
