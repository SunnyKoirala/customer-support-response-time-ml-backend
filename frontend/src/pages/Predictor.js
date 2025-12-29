import React, { useState } from "react";
import "./Predictor.css"; // Create this CSS file for custom styles

function Predictor() {
  const [formData, setFormData] = useState({
    DailyVolume: "",
    HourOfDay: "",
    DayOfWeek: "",
    Priority: "Low",
    Category: "Software",
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      setPrediction(data.prediction);
    } catch (err) {
      alert("Error connecting to backend");
    }
    setLoading(false);
  };

  return (
    <div className="predictor-card">
      <h2>Customer Support Response Time Predictor</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="number"
          name="DailyVolume"
          placeholder="Daily Volume"
          value={formData.DailyVolume}
          onChange={handleChange}
          required
        />
        <input
          type="number"
          name="HourOfDay"
          placeholder="Hour of Day (0-23)"
          value={formData.HourOfDay}
          onChange={handleChange}
          required
        />
        <input
          type="number"
          name="DayOfWeek"
          placeholder="Day of Week (0=Mon,6=Sun)"
          value={formData.DayOfWeek}
          onChange={handleChange}
          required
        />
        <select name="Priority" value={formData.Priority} onChange={handleChange}>
          <option>Low</option>
          <option>Medium</option>
          <option>High</option>
        </select>
        <select name="Category" value={formData.Category} onChange={handleChange}>
          <option>Software</option>
          <option>Network</option>
          <option>Hardware</option>
        </select>
        <button type="submit">{loading ? "Predicting..." : "Predict"}</button>
      </form>
      {prediction !== null && (
        <div className="prediction">
          Predicted Response Time: <strong>{prediction} hours</strong>
        </div>
      )}
    </div>
  );
}

export default Predictor;
