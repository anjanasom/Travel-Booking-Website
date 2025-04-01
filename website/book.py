# For booking logic
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from .models import TrainBooking, FlightBooking, db, HotelBooking
from amadeus import Client, ResponseError
from datetime import datetime

book = Blueprint('book', __name__)

#flight api config
amadeus = Client(
    client_id="BpGm7QjbjY7owWyrS8kd3ttVBbOA3Fc5",
    client_secret="AundJzuKMKWkdVBy"
)

API_HEADERS = {
    "x-rapidapi-key": "e56de045fdmshee40693c5fab516p1c43b9jsn871185d200be",
    "x-rapidapi-host": "irctc1.p.rapidapi.com"
}

@book.route('/start2')
def start():
    return render_template("start2.html")

@book.route('/search-trains', methods=['POST'])
def search_trains():
    from_station = request.form.get("from_station")
    to_station = request.form.get("to_station")
    travel_date = request.form.get("travel_date")
    train_class = request.form.get("train_class", "SL")

    if not from_station or not to_station:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("book.start"))

    url = "https://irctc1.p.rapidapi.com/api/v3/trainBetweenStations"
    querystring = {"fromStationCode": from_station, "toStationCode": to_station, "dateOfJourney": travel_date}
    headers = {
        "x-rapidapi-key": "74fabb6f37mshaa0690ab660bc5dp12e7d2jsn4f546578a4ca",
        "x-rapidapi-host": "irctc1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        train_data = response.json()
    else:
        train_data = {"error": "Failed to fetch train data."}

    return render_template("train_results.html", train_data=train_data, from_station=from_station, to_station=to_station, travel_date=travel_date, train_class=train_class)

@book.route('/train/<train_number>/seats')
def train_seat_selection(train_number):
    from_station = request.args.get('from_station')
    to_station = request.args.get('to_station')
    class_type = request.args.get('class_type')
    travel_date = request.args.get('travel_date') 
    quota = "GN"

    if not travel_date:
        flash("Travel date is required.", "error")
        return redirect(url_for("book.start"))

    # Fetch seat availability
    seat_url = "https://irctc1.p.rapidapi.com/api/v1/checkSeatAvailability"
    seat_params = {
        "classType": class_type,
        "fromStationCode": from_station,
        "quota": quota,
        "toStationCode": to_station,
        "trainNo": train_number,
        "date": travel_date  # Pass travel date
    }
    
    seat_response = requests.get(seat_url, headers=API_HEADERS, params=seat_params)
    seat_data = seat_response.json()

    # Extract seat availability details
    available_seats = []
    if "data" in seat_data:
        for seat in seat_data["data"]:
            available_seats.append({
                "date": seat["date"],
                "ticket_fare": seat["ticket_fare"],
                "catering_charge": seat["catering_charge"],
                "total_fare": seat["total_fare"],
                "status": seat["current_status"]
            })

    if not available_seats:
        flash("No seat availability found for the selected train and date.", "error")
        return redirect(url_for("book.start"))

    return render_template(
    'train_seat_selection.html', 
    class_type=class_type,
    train_number=train_number, 
    from_station=from_station,
    to_station=to_station,
    travel_date=travel_date,
    available_seats=available_seats
    )

from datetime import datetime

@book.route('/book-train', methods=['POST'])
@login_required
def book_train():
    user_id = current_user.id
    train_number = request.form.get("train_number")
    from_station = request.form.get("from_station")
    to_station = request.form.get("to_station")
    class_type = request.form.get("class_type")
    travel_date_str = request.form.get("travel_date")  # This is the string
    total_fare = request.form.get("total_fare")
    seat_status = request.form.get("seat_status", "Confirmed")

    if not all([train_number, from_station, to_station, travel_date_str, class_type, total_fare]):
        flash("Missing booking details.", "error")
        return redirect(url_for("book.start"))

    # Convert travel_date_str (which is a string) to a datetime object
    try:
        travel_date = datetime.strptime(travel_date_str, "%Y-%m-%d").date()  # Adjust format as needed
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD.", "error")
        return redirect(url_for("book.start"))

    # Create a TrainBooking object
    new_booking = TrainBooking(
        user_id=user_id,
        train_number=train_number,
        from_station=from_station,
        to_station=to_station,
        class_type=class_type,
        travel_date=travel_date,  # Use the datetime object here
        total_fare=total_fare,
        seat_status=seat_status
    )

    db.session.add(new_booking)
    db.session.commit()

    flash("Train ticket booked successfully!", "success")
    return redirect(url_for("views.dashboard"))


@book.route('/cancel_train_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_train_booking(booking_id):
    booking = TrainBooking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)  # Forbidden
    db.session.delete(booking)
    db.session.commit()
    flash("Train booking canceled successfully!", "success")
    return redirect(url_for('views.dashboard'))


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
    
@book.route('/book-flight', methods=['POST'])
@login_required
def book_flight():
    # Get the flight data from the form
    flight_id = request.form.get('flight_id')
    departure_code = request.form.get('departure_code')
    arrival_code = request.form.get('arrival_code')
    departure_time = request.form.get('departure_time')
    arrival_time = request.form.get('arrival_time')
    price = request.form.get('price')
    traveler_type = request.form.get('traveler_type')

    # Convert departure_time and return_time (if present) to datetime objects
    try:
        departure_date = datetime.fromisoformat(departure_time)  # Convert departure_time to datetime
    except ValueError:
        departure_date = None  # Handle invalid date format if needed

    return_date = None
    if arrival_time:  # If arrival_time exists, convert it to a datetime object
        try:
            return_date = datetime.fromisoformat(arrival_time)
        except ValueError:
            return_date = None  # Handle invalid date format if needed

    user_id = current_user.id
    flight_number = flight_id
    from_city = departure_code
    to_city = arrival_code
    travel_class = traveler_type
    total_fare = price

    # Create a new FlightBooking object
    new_booking = FlightBooking(
        user_id=user_id,
        flight_number=flight_number,
        from_city=from_city,
        to_city=to_city,
        departure_date=departure_date,
        return_date=return_date,  # Can be None for one-way flights
        travel_class=travel_class,
        total_fare=total_fare,
        seat_status="Confirmed"  # Assuming "Confirmed" status by default
    )

    # Add the booking to the database
    db.session.add(new_booking)
    db.session.commit()

    flash("Flight booked successfully!", "success")
    return redirect(url_for("views.dashboard"))


@book.route('/cancel_flight_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_flight_booking(booking_id):
    booking = FlightBooking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)  # Forbidden
    db.session.delete(booking)
    db.session.commit()
    flash("Flight booking canceled successfully!", "success")
    return redirect(url_for('views.dashboard'))


@book.route('/search-buses', methods=['POST'])
def search_buses():
    from_city = request.form.get("from_city")
    to_city = request.form.get("to_city")
    travel_date = request.form.get("travel_date")

    if not from_city or not to_city:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("book.start"))

    return f"Searching buses from {from_city} to {to_city} on {travel_date}"

def search_hotels_by_city(city_code):
    try:
        # Get hotel data using the city code
        response = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)
        hotel_data = response.data  # this should be a list
        
        if not hotel_data:
            flash("No hotels found for the selected city.", "error")
            return []  # return an empty list if no hotels are found

        # Collect hotel details from the returned data
        hotels = []
        for hotel in hotel_data:
            hotel_info = {
                'hotelId': hotel['hotelId'],
                'name': hotel['name'],
                'address': hotel['address']['countryCode'],  # Using country code for simplicity
                # You can expand here to include more info if needed
            }
            hotels.append(hotel_info)

        return hotels  # return a list of hotel details

    except ResponseError as error:
        print(f"Error fetching hotels by city: {error}")
        flash("Failed to fetch hotel data. Please try again later.", "error")
        return []  # return an empty list on error

@book.route('/search-hotels', methods=['POST'])
def search_hotels():
    city_code = request.form.get("hotel_city")
    checkin_date = request.form.get("checkin_date")
    checkout_date = request.form.get("checkout_date")
    num_guests = request.form.get("num_guests", "1") 

    # Validate input
    if not city_code or not checkin_date or not checkout_date:
        flash("Please enter all required fields.", "error")
        return redirect(url_for("book.start"))

    try:
        # Step 2: Get hotel IDs for the city
        hotels = search_hotels_by_city(city_code)
        
        return render_template("hotel_results.html", hotels=hotels, cityCode=city_code, checkin_date=checkin_date, num_guests=num_guests, checkout_date=checkout_date)

    except ResponseError as error:
        print(f"Error fetching hotels: {error}")
        flash("Failed to fetch hotel data. Please try again later.", "error")
        return redirect(url_for("book.start"))

@book.route('/book_hotel/<hotel_id>', methods=['GET', 'POST'])
def book_hotel(hotel_id):
    if request.method == 'POST':
        # Additional details for booking
        checkin_date = request.form.get("checkin_date")
        checkout_date = request.form.get("checkout_date")
        num_guests = request.form.get("num_guests")
        hotel_name = request.form.get("hotel_name")
        address = request.form.get("city")

        try:
            checkIn_date = datetime.strptime(checkin_date, "%Y-%m-%d").date()  # Convert string to date
            checkOut_date = datetime.strptime(checkout_date, "%Y-%m-%d").date()  # Convert string to date
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return redirect(url_for("book.start"))

        # Add booking to the database with more details
        booking = HotelBooking(
            user_id=current_user.id,
            hotel_id=hotel_id,
            hotel_name=hotel_name,
            city=address,
            checkin_date=checkIn_date,
            checkout_date=checkOut_date,
            booking_status="Booked"
        )
        db.session.add(booking)
        db.session.commit()

        flash(f"Booking confirmed for {hotel_name} from {checkin_date} to {checkout_date}.", "success")
        return redirect(url_for('views.dashboard'))
    
@book.route('/cancel_hotel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_hotel_booking(booking_id):
    # Fetch the hotel booking from the database using the booking_id
    booking = HotelBooking.query.get_or_404(booking_id)

    # Check if the booking belongs to the current user
    if booking.user_id != current_user.id:
        abort(403)  # Forbidden, user is not allowed to cancel another user's booking

    # Delete the booking from the database
    db.session.delete(booking)
    db.session.commit()

    # Flash a success message
    flash("Hotel booking canceled successfully!", "success")

    # Redirect to the user's dashboard or another relevant page
    return redirect(url_for('views.dashboard'))  # Adjust to the appropriate redirect URL
