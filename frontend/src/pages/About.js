import React from "react";
import "./About.css";

function About() {
return (
<div className="about-container">
<h1>About This AI System</h1>
<p>
This AI-powered platform predicts customer support response time
using real-world ticket data and machine learning models.
</p>

  <div className="about-grid">
    <div>⚙️ Flask REST API</div>
    <div>📈 Scikit-Learn ML Model</div>
    <div>⚛️ React Frontend</div>
    <div>☁️ Render Deployment</div>
  </div>
</div>


);
}

export default About;