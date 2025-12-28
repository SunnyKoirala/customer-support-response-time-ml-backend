from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline

# ----------------------------
# Load dataset
# ----------------------------
df = pd.read_csv("data/customer_support_tickets.csv")

# Rename columns to standard names
df.rename(columns={
    "Date of Purchase": "CreatedTime",
    "First Response Time": "ResponseTime",
    "Ticket Priority": "Priority",
    "Ticket Type": "Category"
}, inplace=True)

# Convert to datetime
df["CreatedTime"] = pd.to_datetime(df["CreatedTime"], errors="coerce")
df["ResponseTime"] = pd.to_datetime(df["ResponseTime"], errors="coerce")

# Compute response time in hours
df["ResponseHours"] = (df["ResponseTime"] - df["CreatedTime"]).dt.total_seconds() / 3600

# ----------------------------
# Remove rows with missing target
# ----------------------------
df = df.dropna(subset=["ResponseHours"])

# Feature engineering
df["HourOfDay"] = df["CreatedTime"].dt.hour
df["DayOfWeek"] = df["CreatedTime"].dt.dayofweek

# Calculate daily ticket volume
daily_volume = df.groupby(df["CreatedTime"].dt.date).size().rename("DailyVolume")
df = df.merge(daily_volume, left_on=df["CreatedTime"].dt.date, right_index=True)

# ----------------------------
# Prepare features and target
# ----------------------------
X = df[["DailyVolume", "HourOfDay", "DayOfWeek", "Priority", "Category"]]
y = df["ResponseHours"]

num_cols = ["DailyVolume", "HourOfDay", "DayOfWeek"]
cat_cols = ["Priority", "Category"]

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), cat_cols)
])

# Build model pipeline
model = Pipeline([
    ("prep", preprocessor),
    ("poly", PolynomialFeatures(degree=2, include_bias=False)),
    ("reg", ElasticNet(alpha=0.1, l1_ratio=0.5))
])

# Split data and train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# ----------------------------
# Flask API
# ----------------------------
app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    df_input = pd.DataFrame([{
        "DailyVolume": data["DailyVolume"],
        "HourOfDay": data["HourOfDay"],
        "DayOfWeek": data["DayOfWeek"],
        "Priority": data["Priority"],
        "Category": data["Category"]
    }])
    prediction = round(model.predict(df_input)[0], 2)
    return jsonify({"prediction": prediction})

if __name__ == "__main__":
    app.run(debug=True)
