from flask import Blueprint, render_template, request, flash
from .models import Users, Votes, Names
from . import db
from flask_login import login_required, current_user
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

vote = Blueprint("vote", __name__)

@vote.route("/vote", methods=["GET", "POST"])
@login_required
def voting():
    all_voted = False
    # Getting all the names we can vote for (except our own)
    vote_names = Names.query.filter(Names.name != current_user.name).all()

    if request.method == "POST":
        # These vote values give the IDs of each person. So lets get their name
        firstv_id = request.form.get("first_vote")
        firstv = Names.query.filter_by(id=firstv_id).first().name
        secondv_id = request.form.get("second_vote")
        secondv = Names.query.filter_by(id=secondv_id).first().name
        current_id = current_user.id

        current_email = Users.query.filter_by(id=current_id).first().email
        current_name = Users.query.filter_by(id=current_id).first().name

        # Checking if user has already voted.
        existing_vote = Votes.query.filter_by(user_id=current_id).first()
        if existing_vote:
            flash("You have already voted.", category="error")
        elif firstv == secondv:
            flash("Cannot vote for the same person twice.", category="error")
        else:
            new_vote = Votes(first_vote=firstv_id, second_vote=secondv_id, user_id=current_user.id)
            db.session.add(new_vote)
            db.session.commit()

            # Email stuff
            # Mailing confirmation of votes
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("oskarhosken@gmail.com", os.getenv("GMAIL_PASSWORD"))

            msg = MIMEMultipart()
            msg['From'] = "Mut House Voting <oskarhosken@gmail.com>"
            msg['To'] = current_email
            msg['Subject'] = "Voting Confirmation"

            email_body = f"Hi {current_name},\nYour votes have been submitted. Here they are for reference:\n1. {firstv}.\n2. {secondv}."

            msg.attach(MIMEText(email_body, 'plain'))

            server.sendmail("oskarhosken@gmail.com", current_email, msg.as_string())
            server.quit()

            flash("Vote submitted successfully.")

    # This means that everyone has voted and now we need to get the houses.
    if len(Votes.query.all()) == len(Names.query.all()):
        all_voted = True
        houses = generate_houses()

    return render_template("vote.html", user=current_user, vote_names=vote_names, all_voted=all_voted)

def generate_houses():
    pass