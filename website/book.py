#for booking logic
from flask import Blueprint, render_template, request, redirect, url_for, flash

book = Blueprint('book', __name__)

@book.route('/start2')
def start():
    return render_template("start2.html")

@book.route('/search-flights', methods = ['POST'])
def search_flights():
    from_city = request.form.get("from_city")
    to_city = request.form.get("to_city")
    departure_date = request.form.get("departure_date")
    return_date = request.form.get("return_date", None)
    trip_type = request.form.get("trip_type")
    travellers_class = request.form.get("travellers_class")

    if not from_city or not to_city:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("book.start2"))

    return f"Searching flights from {from_city} to {to_city} on {departure_date} - {trip_type}"

@book.route('/search-trains', methods=['POST'])
def search_trains():
    from_station = request.form.get("from_station")
    to_station = request.form.get("to_station")
    travel_date = request.form.get("travel_date")
    train_class = request.form.get("train_class")

    if not from_station or not to_station:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("book.start2"))

    return f"Searching trains from {from_station} to {to_station} on {travel_date} - {train_class}"

@book.route('/search-buses', methods=['POST'])
def search_buses():
    from_city = request.form.get("from_city")
    to_city = request.form.get("to_city")
    travel_date = request.form.get("travel_date")

    if not from_city or not to_city:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("book.start2"))

    return f"Searching buses from {from_city} to {to_city} on {travel_date}"

@book.route('/search-hotels', methods=['POST'])
def search_hotels():
    hotel_city = request.form.get("hotel_city")
    checkin_date = request.form.get("checkin_date")
    checkout_date = request.form.get("checkout_date")
    num_guests = request.form.get("num_guests")

    if not hotel_city:
        flash("Please enter a city for hotel search.", "error")
        return redirect(url_for("book.start2"))

    return f"Searching hotels in {hotel_city} from {checkin_date} to {checkout_date} for {num_guests}"