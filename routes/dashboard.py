from flask import Blueprint, render_template
from flask_login import login_required, current_user
from utils.db_models import Expense, db
from sqlalchemy import func, extract
from utils.insights import generate_insights

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

    # 🔹 User-friendly advice
    advice = generate_insights(income, total, status)

    # 🔹 Pie chart
    chart = None
    if categories:
        df_cat = pd.DataFrame(categories, columns=["category", "amount"])
        fig_cat = px.pie(
            df_cat,
            names="category",
            values="amount",
            title="Expense Distribution",
            template="plotly_dark"
        )
        chart = fig_cat.to_html(full_html=False)

    # 🔹 Monthly trend
    monthly_data = db.session.query(
        extract("month", Expense.date),
        func.sum(Expense.amount)
    ).filter_by(user_id=current_user.id) \
     .group_by(extract("month", Expense.date)) \
     .order_by(extract("month", Expense.date)) \
     .all()

    trend_chart = None
    trend_message = None

    if monthly_data:
        df_trend = pd.DataFrame(monthly_data, columns=["month", "total"])
        df_trend["month"] = df_trend["month"].astype(int)

        fig_trend = px.line(
            df_trend,
            x="month",
            y="total",
            markers=True,
            title="Monthly Expense Trend",
            template="plotly_dark"
        )

        trend_chart = fig_trend.to_html(full_html=False)

        if len(monthly_data) >= 2:
            last, prev = monthly_data[-1][1], monthly_data[-2][1]
            if prev > 0:
                change = ((last - prev) / prev) * 100
                trend_message = f"Your spending changed by {change:.1f}% compared to last month."

    # 🔹 Recent transactions (NEW)
    recent_expenses = Expense.query \
        .filter_by(user_id=current_user.id) \
        .order_by(Expense.date.desc()) \
        .limit(10) \
        .all()

    return render_template(
        "dashboard.html",
        user=current_user,
        total=total,
        categories=categories,
        savings=savings,
        ratio=round(ratio, 2),
        status=status,
        advice=advice,
        chart=chart,
        trend_chart=trend_chart,
        trend_message=trend_message,
        recent_expenses=recent_expenses
    )