import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib

# Sample training data (synthetic but realistic)
data = {
    "income": [30000, 30000, 30000, 50000, 50000, 50000],
    "expense": [20000, 28000, 29500, 30000, 45000, 49000],
}

df = pd.DataFrame(data)

df["savings_ratio"] = (df["income"] - df["expense"]) / df["income"]

def label(r):
    if r >= 0.20:
        return 2      # Healthy
    elif r >= 0.05:
        return 1      # Risky
    return 0          # Critical

df["label"] = df["savings_ratio"].apply(label)

X = df[["savings_ratio"]]
y = df["label"]

model = LogisticRegression()
model.fit(X, y)

joblib.dump(model, "models/finance_model.pkl")

print("Model trained and saved")