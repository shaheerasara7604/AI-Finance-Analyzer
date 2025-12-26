from flask import Blueprint, render_template, request, redirect
from flask_login import login_user, logout_user, login_required
from utils.db_models import db, User

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            name=request.form["name"],
            email=request.form["email"],
            monthly_income=float(request.form["income"])
        )
        user.set_password(request.form["password"])
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect("/dashboard")
    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")