import React from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="logo">AI Support Predictor</div>
      <ul className="nav-links">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/predictor">Predictor</Link></li>
        <li><Link to="/about">About</Link></li>
      </ul>
    </nav>
  );
}

export default Navbar;
