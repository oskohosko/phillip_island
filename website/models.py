from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_vote = db.Column(db.String(100))
    second_vote = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    votes = db.relationship("Vote")