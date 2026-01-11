def generate_insights(income, total_expense, status):
    savings = income - total_expense

    if status == "Healthy":
        message = (
            f"Great job! You saved ₹{int(savings)} this month. "
            "You are managing your finances well. Consider investing your surplus."
        )

    elif status == "Risky":
        message = (
            f"You saved ₹{int(savings)} this month, but your expenses are slightly high. "
            "Try reducing non-essential spending to improve your savings."
        )

    else:  # Critical
        message = (
            f"You saved only ₹{int(savings)} this month. "
            "Your expenses are critically high. Focus on cutting discretionary costs immediately."
        )

    return message