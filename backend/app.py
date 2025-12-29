from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
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

# Convert to datetime safely
df["CreatedTime"] = pd.to_datetime(df["CreatedTime"], errors="coerce")
df["ResponseTime"] = pd.to_datetime(df["ResponseTime"], errors="coerce")

# ----------------------------
# Compute response time in hours
# ----------------------------
df["ResponseHours"] = (
    df["ResponseTime"] - df["CreatedTime"]
).dt.total_seconds() / 3600

# 🔒 IMPORTANT: remove invalid / extreme values
df["ResponseHours"] = df["ResponseHours"].clip(lower=0, upper=72)

# Remove rows with missing target
df = df.dropna(subset=["ResponseHours", "CreatedTime"])

# ----------------------------
# Feature engineering
# ----------------------------
df["HourOfDay"] = df["CreatedTime"].dt.hour
df["DayOfWeek"] = df["CreatedTime"].dt.dayofweek

# Daily ticket volume
daily_volume = (
    df.groupby(df["CreatedTime"].dt.date)
    .size()
    .rename("DailyVolume")
)

df = df.merge(
    daily_volume,
    left_on=df["CreatedTime"].dt.date,
    right_index=True
)

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

# ----------------------------
# Build stable model pipeline
# ----------------------------
model = Pipeline([
    ("prep", preprocessor),
    ("reg", ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=42))
])

# Train model
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model.fit(X_train, y_train)

# ----------------------------
# Flask API
# ----------------------------
app = Flask(__name__)
CORS(app)  # Allow frontend / Postman access

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    df_input = pd.DataFrame([{
        "DailyVolume": int(data["DailyVolume"]),
        "HourOfDay": int(data["HourOfDay"]),
        "DayOfWeek": int(data["DayOfWeek"]),
        "Priority": data["Priority"],
        "Category": data["Category"]
    }])

    raw_pred = model.predict(df_input)[0]
    prediction = round(max(0, raw_pred), 2)  # 🔒 protect output

    return jsonify({"prediction": prediction})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
