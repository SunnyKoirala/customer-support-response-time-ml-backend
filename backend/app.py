from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
import openai

# ----------------------------
# Flask app setup
# ----------------------------
app = Flask(__name__)
CORS(app)

# ----------------------------
# AI API key
# ----------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

# ----------------------------
# Model setup
# ----------------------------
MODEL_PATH = "model.pkl"
MAX_RESPONSE_HOURS = 72  # Optional safety cap

# Load training data to know valid categories
df = pd.read_csv("data/customer_support_tickets.csv")

# Rename columns
df.rename(columns={
    "Date of Purchase": "CreatedTime",
    "First Response Time": "ResponseTime",
    "Ticket Priority": "Priority",
    "Ticket Type": "Category"
}, inplace=True)

df["CreatedTime"] = pd.to_datetime(df["CreatedTime"], errors="coerce")
df["ResponseTime"] = pd.to_datetime(df["ResponseTime"], errors="coerce")
df["ResponseHours"] = (df["ResponseTime"] - df["CreatedTime"]).dt.total_seconds() / 3600
df = df[df["ResponseHours"] >= 0].dropna(subset=["ResponseHours", "CreatedTime"])

df["HourOfDay"] = df["CreatedTime"].dt.hour
df["DayOfWeek"] = df["CreatedTime"].dt.dayofweek

daily_volume = df.groupby(df["CreatedTime"].dt.date).size().rename("DailyVolume")
df = df.merge(daily_volume, left_on=df["CreatedTime"].dt.date, right_index=True)

X = df[["DailyVolume", "HourOfDay", "DayOfWeek", "Priority", "Category"]]
y = df["ResponseHours"]

num_cols = ["DailyVolume", "HourOfDay", "DayOfWeek"]
cat_cols = ["Priority", "Category"]

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), cat_cols)
])

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("Model loaded from disk.")
else:
    # Train the model if not found
    model = Pipeline([
        ("prep", preprocessor),
        ("reg", RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42))
    ])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)
    print("Model trained and saved.")

# ----------------------------
# Prediction API
# ----------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    # Validate input
    required_fields = ["DailyVolume", "HourOfDay", "DayOfWeek", "Priority", "Category"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Check categories
    if data["Priority"] not in df["Priority"].unique():
        return jsonify({"error": f"Invalid Priority. Must be one of {list(df['Priority'].unique())}"}), 400
    if data["Category"] not in df["Category"].unique():
        return jsonify({"error": f"Invalid Category. Must be one of {list(df['Category'].unique())}"}), 400

    # Create DataFrame for prediction
    df_input = pd.DataFrame([{
        "DailyVolume": int(data["DailyVolume"]),
        "HourOfDay": int(data["HourOfDay"]),
        "DayOfWeek": int(data["DayOfWeek"]),
        "Priority": data["Priority"],
        "Category": data["Category"]
    }])

    # Clip numeric values to realistic ranges from training data
    df_input["DailyVolume"] = df_input["DailyVolume"].clip(0, df["DailyVolume"].max())
    df_input["HourOfDay"] = df_input["HourOfDay"].clip(0, 23)
    df_input["DayOfWeek"] = df_input["DayOfWeek"].clip(0, 6)

    # Predict
    raw_pred = model.predict(df_input)[0]

    # Optional: clip prediction to MAX_RESPONSE_HOURS
    prediction = round(max(0, min(raw_pred, MAX_RESPONSE_HOURS)), 2)

    return jsonify({"prediction": prediction})

# ----------------------------
# AI Chatbot API
# ----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")
    if not user_message:
        return jsonify({"reply": "Please type a message."})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for a customer support response-time prediction app."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content
    except Exception:
        reply = "Sorry, the AI is currently unavailable."

    return jsonify({"reply": reply})

# ----------------------------
# Run the server
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
