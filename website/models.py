from . import db
from flask_login import UserMixin

# Database keeping the available names
class Names(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    signed_up = db.Column(db.Integer)

class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_vote = db.Column(db.String(100))
    second_vote = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    votes = db.relationship("Votes")

