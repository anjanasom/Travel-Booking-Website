# For booking logic
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from amadeus import Client, ResponseError

book = Blueprint('book', __name__)

#flight api config
amadeus = Client(
    client_id="BpGm7QjbjY7owWyrS8kd3ttVBbOA3Fc5",
    client_secret="AundJzuKMKWkdVBy"
)

@book.route('/start2')
def start():
    return render_template("start2.html")

@book.route('/search-trains', methods=['POST'])
def search_trains():
    from_station = request.form.get("from_station")
    to_station = request.form.get("to_station")
    travel_date = request.form.get("travel_date")

    if not from_station or not to_station:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("book.start2"))

    url = "https://irctc1.p.rapidapi.com/api/v3/trainBetweenStations"
    querystring = {"fromStationCode": from_station, "toStationCode": to_station, "dateOfJourney": travel_date}
    headers = {
        "x-rapidapi-key": "e56de045fdmshee40693c5fab516p1c43b9jsn871185d200be",
        "x-rapidapi-host": "irctc1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        train_data = response.json()
    else:
        train_data = {"error": "Failed to fetch train data."}

    return render_template("train_results.html", train_data=train_data)

@book.route('/search-flights', methods=['POST'])
def search_flights():
    from_city = request.form.get("from_city")
    to_city = request.form.get("to_city")
    departure_date = request.form.get("departure_date")
    return_date = request.form.get("return_date", None)
    trip_type = request.form.get("trip_type")
    adults = request.form.get("adults", "1")
    children = request.form.get("children", "0")
    travel_class = request.form.get("travel_class", "ECONOMY").upper()

    if not from_city or not to_city or not departure_date:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("book.start"))

    try:
        # Create the query parameters
        params = {
            "originLocationCode": from_city,
            "destinationLocationCode": to_city,
            "departureDate": departure_date,
            "adults": int(adults),
            "children": int(children),
            "travelClass": travel_class,
            "currencyCode": "INR"
        }

        # Include returnDate only for round-trip
        if trip_type == "round-trip" and return_date:
            params["returnDate"] = return_date

        # Fetch flight offers
        response = amadeus.shopping.flight_offers_search.get(**params)
        flight_data = response.data

        if not flight_data:
            flash("No flights found for the selected date.", "error")
            return redirect(url_for("book.start"))

        return render_template("flight_results.html", flight_data=flight_data)

    except ResponseError as error:
        print(f"Error fetching flights: {error}")
        flash("Failed to fetch flight data. Please try again later.", "error")
        return redirect(url_for("book.start"))

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