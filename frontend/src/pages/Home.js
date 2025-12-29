import React from "react";
import "./Home.css";

function Home() {
return (
<section className="hero">
<h1>
AI-Powered <span>Customer Support Intelligence</span>
</h1>
<p>
Predict response times, optimize ticket workflows,
and deliver world-class customer experiences using AI.
</p>

  <div className="hero-cards">
    <div className="glass-card">🤖 ML Prediction</div>
    <div className="glass-card">📊 Smart Analytics</div>
    <div className="glass-card">⚡ Real-Time API</div>
  </div>
</section>


);
}

export default Home;