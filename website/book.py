#for booking logic
from flask import Blueprint, render_template

book = Blueprint('book', __name__)

@book.route('/start')
def start():
    return render_template("start.html")