import pandas as pd
from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user
from utils.db_models import db, Expense

expenses = Blueprint("expenses", __name__)

@expenses.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files["file"]
        df = pd.read_csv(file)

        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()

        # Handle missing values safely
        df["category"] = df["category"].fillna("Uncategorized")
        df["amount"] = df["amount"].fillna(0)

        for _, row in df.iterrows():
            expense = Expense(
                user_id=current_user.id,
                date=pd.to_datetime(row["date"]).date(),
                amount=float(row["amount"]),
                category=str(row["category"])
            )
            db.session.add(expense)

        db.session.commit()
        return redirect("/dashboard")

    return render_template("upload.html")