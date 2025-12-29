from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline
import openai
import os

# ----------------------------
# Flask app setup
# ----------------------------
app = Flask(__name__)
CORS(app)  # Allow frontend access

# ----------------------------
# OpenAI API key
# ----------------------------
# Make sure you set this in your environment:
# Windows: setx OPENAI_API_KEY "your_api_key_here"
# Linux/macOS: export OPENAI_API_KEY="your_api_key_here"
openai.api_key = os.getenv("OPENAI_API_KEY")

# ----------------------------
# Load and preprocess dataset
# ----------------------------
df = pd.read_csv("data/customer_support_tickets.csv")

df.rename(columns={
    "Date of Purchase": "CreatedTime",
    "First Response Time": "ResponseTime",
    "Ticket Priority": "Priority",
    "Ticket Type": "Category"
}, inplace=True)

df["CreatedTime"] = pd.to_datetime(df["CreatedTime"], errors="coerce")
df["ResponseTime"] = pd.to_datetime(df["ResponseTime"], errors="coerce")

df["ResponseHours"] = (df["ResponseTime"] - df["CreatedTime"]).dt.total_seconds() / 3600
df["ResponseHours"] = df["ResponseHours"].clip(lower=0, upper=72)  # remove extreme values

df = df.dropna(subset=["ResponseHours", "CreatedTime"])

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

model = Pipeline([
    ("prep", preprocessor),
    ("reg", ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=42))
])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# ----------------------------
# Prediction API
# ----------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    try:
        df_input = pd.DataFrame([{
            "DailyVolume": int(data["DailyVolume"]),
            "HourOfDay": int(data["HourOfDay"]),
            "DayOfWeek": int(data["DayOfWeek"]),
            "Priority": data["Priority"],
            "Category": data["Category"]
        }])
    except Exception:
        return jsonify({"error": "Invalid input"}), 400

    raw_pred = model.predict(df_input)[0]
    prediction = round(max(0, raw_pred), 2)  # no negative predictions
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
    except Exception as e:
        reply = "Sorry, the AI is currently unavailable."

    return jsonify({"reply": reply})

# ----------------------------
# Run the server
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
