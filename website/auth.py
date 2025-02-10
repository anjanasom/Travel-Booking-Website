#for backend user authentification
from flask import Blueprint, render_template, request

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return render_template("index.html")

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
    return render_template("signup.html")