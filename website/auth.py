from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import select
from .models import User, Vote, Names
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import re

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Looking for a specific entry
        # Filter for all users with this email field
        # Should only be one result
        user = User.query.filter_by(email=email).first()
        if user:
            # If passwords are the same
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required     # Cannot access until user is logged in
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():

    available_names = Names.query.filter_by(signed_up=0)

    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Regular Expression to match email addresses
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", category="error")
        elif not re.match(email_pattern, email):
            flash("Not a valid email address.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 7:
            flash("Password must be at least 7 characters.", category="error")
        else:
            # add user to DB
            new_name = Names.query.filter_by(id=name).first()
            new_user = User(email=email, name=new_name.name, password=generate_password_hash(password1, method="sha256"))
            new_name.signed_up = 1
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for("views.home"))


    return render_template("signup.html", user=current_user, available_names=available_names)


@auth.route("/vote", methods=["GET", "POST"])
@login_required
def vote():

    # Getting all the names we can vote for (except our own)
    vote_names = Names.query.filter(Names.name != current_user.name).all()

    if request.method == "POST":
        # These vote values give the IDs of each person. So lets get their name
        firstv_id = request.form.get("first_vote")
        firstv = Names.query.filter_by(id=firstv_id).first().name
        secondv_id = request.form.get("second_vote")
        secondv = Names.query.filter_by(id=secondv_id).first().name
        current_id = current_user.id

        # Checking if user has already voted.
        existing_vote = Vote.query.filter_by(user_id=current_id).first()
        if existing_vote:
            flash("You have already voted.", category="error")
        elif firstv == secondv:
            flash("Cannot vote for the same person twice.", category="error")
        else:
            new_vote = Vote(first_vote=firstv, second_vote=secondv, user_id=current_user.id)
            db.session.add(new_vote)
            db.session.commit()
            flash("Vote submitted successfully.")

    return render_template("vote.html", user=current_user, vote_names = vote_names)

@auth.route("/termsandconditions", methods=["GET", "POST"])
def tandc():
    return render_template("termsandconditions.html", methods=["GET", "POST"], user=current_user)