from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

import os
from dotenv import load_dotenv

db = SQLAlchemy()
DB_NAME = "database.db"

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Vote, Names

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Looking for a user and use function to load user
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
     # Populating our Names DB
    muts = ['Alex Roddam', 'Alex Stork', 'Cameron Clarke', 'Connor Beadman', 'Diego Disley', 'Dylan Laguerre', 'Geordie Psevdos', 'George Vasili', 'Jack Rider', 'James Hodson', 'John Mastoras', 'Josh Anderson', 'Luke Davies', 'Matt Courtney', 'Matt Pervan', 'Max Roker', 'Maxim Schulz', 'Michael Rao', 'Nick Taylor', 'Ollie Stevens', 'Oskar Hosken', 'Rohnan Madden', 'Ryan Walsh', 'Will Elliott']

    with app.app_context():
        if not Names.query.first():
            for name in muts:
                new_name = Names(name=name, signed_up=0)
                db.session.add(new_name)
            db.session.commit()

    return app

def create_database(app):
    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')
