from flask import Blueprint, render_template
from flask_login import login_required, current_user
from utils.db_models import Expense, db
from sqlalchemy import func

import plotly.express as px
import pandas as pd
import joblib

dashboard = Blueprint("dashboard", __name__)

# 🔹 Load ML model once
model = joblib.load("models/finance_model.pkl")

@dashboard.route("/dashboard")
@login_required
def dashboard_view():
    # 🔹 Total expenses
    total = db.session.query(func.sum(Expense.amount)) \
        .filter_by(user_id=current_user.id).scalar() or 0

    # 🔹 Category-wise expenses
    categories = db.session.query(
        Expense.category,
        func.sum(Expense.amount)
    ).filter_by(user_id=current_user.id) \
     .group_by(Expense.category).all()

    # 🔹 Financial calculations
    income = current_user.monthly_income
    savings = income - total

    if income > 0:
        ratio = savings / income
        prediction = model.predict([[ratio]])[0]
        status = {0: "Critical", 1: "Risky", 2: "Healthy"}[prediction]
    else:
        ratio = 0
        status = "Unknown"

    # 🔹 Plotly pie chart
    chart = None
    if categories:
        df = pd.DataFrame(categories, columns=["category", "amount"])
        fig = px.pie(
            df,
            names="category",
            values="amount",
            title="Expense Distribution"
        )
        chart = fig.to_html(full_html=False)

    return render_template(
        "dashboard.html",
        user=current_user,
        total=total,
        categories=categories,
        savings=savings,
        ratio=round(ratio, 2),
        status=status,
        chart=chart
    )