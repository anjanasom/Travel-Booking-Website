#to make 'website' a python package
from dotenv import load_dotenv
import os

load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default_secret_key")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    migrate.init_app(app, db)

    from .views import views
    from .auth import auth
    from .book import book
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(book, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')

    from .models import User, TrainBooking, FlightBooking, TravelGroup, GroupMembers, HotelBooking, BusBooking

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"  # Redirect users to login if unauthorized
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))  # Load user from DB

    return app

def create_database(app):
    DB_PATH = path.join(path.dirname(__file__), DB_NAME) 
    
    if not path.exists(DB_PATH):
        with app.app_context():
            db.create_all()
            print('Created Database!')
