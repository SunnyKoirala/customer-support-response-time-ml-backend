import pandas as pd
import numpy as np
from flask import Flask, request, render_template_string
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline

Load dataset

df = pd.read_csv("data/support_tickets.csv", parse_dates=["CreatedTime", "ResponseTime"])

Compute response time in hours

df["ResponseHours"] = (df["ResponseTime"] - df["CreatedTime"]).dt.total_seconds() / 3600

Feature engineering

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
("cat", OneHotEncoder(drop="first"), cat_cols)
])

model = Pipeline([
("prep", preprocessor),
("poly", PolynomialFeatures(degree=2, include_bias=False)),
("reg", ElasticNet(alpha=0.1, l1_ratio=0.5))
])

X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.2, random_state=42
)

model.fit(X_train, y_train)

Flask app

app = Flask(name)

HTML = """

<h2>Customer Support Response Time Prediction</h2> <form method="post"> Daily Volume: <input type="number" name="volume" required><br><br> Hour of Day (0-23): <input type="number" name="hour" required><br><br> Day of Week (0=Mon,6=Sun): <input type="number" name="day" required><br><br> Priority: <select name="priority"> <option>Low</option> <option>Medium</option> <option>High</option> </select><br><br> Category: <select name="category"> <option>Software</option> <option>Network</option> <option>Hardware</option> </select><br><br> <input type="submit"> </form>

{% if prediction %}

<h3>Predicted Response Time: {{ prediction }} hours</h3> {% endif %} """

@app.route("/", methods=["GET", "POST"])
def predict():
prediction = None
if request.method == "POST":
data = pd.DataFrame([{
"DailyVolume": int(request.form["volume"]),
"HourOfDay": int(request.form["hour"]),
"DayOfWeek": int(request.form["day"]),
"Priority": request.form["priority"],
"Category": request.form["category"]
}])
prediction = round(model.predict(data)[0], 2)
return render_template_string(HTML, prediction=prediction)

if name == "main":
app.run(debug=True)