from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Users, Names
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import re
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Looking for a specific entry
        # Filter for all users with this email field
        # Should only be one result
        user = Users.query.filter_by(email=email).first()
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

        user = Users.query.filter_by(email=email).first()
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
            new_user = Users(email=email, name=new_name.name, password=generate_password_hash(password1, method="sha256"))
            new_name.signed_up = 1
            db.session.add(new_user)
            db.session.commit()

            # Mail stuff
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("oskarhosken@gmail.com", os.getenv("GMAIL_PASSWORD"))

            msg = MIMEMultipart()
            msg['From'] = "Mut House Voting <oskarhosken@gmail.com>"
            msg['To'] = email
            msg['Subject'] = "Sign Up Confirmation - Phillip Island House Voting."

            email_body = f"Hi {new_name.name},\nThank you for signing up to the Mut Phillip Island House Voting Service."

            msg.attach(MIMEText(email_body, 'plain'))

            server.sendmail("oskarhosken@gmail.com", email, msg.as_string())
            server.quit()

            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for("views.home"))


    return render_template("signup.html", user=current_user, available_names=available_names)

@auth.route("/termsandconditions", methods=["GET", "POST"])
def tandc():
    return render_template("termsandconditions.html", methods=["GET", "POST"], user=current_user)
