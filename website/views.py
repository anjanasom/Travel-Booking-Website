#for all the url endpoints
from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("index.html")

@views.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template("contact.html")

@views.route('/packages')
def packages():
    return render_template("packages.html")

@views.route('/travelgroups')
def travelgroups():
    return render_template("travelgroups.html")

