#for backend user authentification
from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return render_template("index.html")

@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if len(email) < 4:
            flash("Email must be at least 4 characters.", category = "error")
        elif len(name) < 2:
            flash("Name must be at least 2 characters.", category = "error")
        elif password != confirm_password:
            flash("Passwords don't match.", category = "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters.", category = "error")
        else:
            # add user to db
            flash("Account created!", category = "success")
    return render_template("signup.html")