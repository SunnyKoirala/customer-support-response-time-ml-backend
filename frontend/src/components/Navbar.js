import React from "react";
import { NavLink } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
return (
<nav className="navbar">
<div className="logo">AI Support</div>
<div className="nav-links">
<NavLink to="/">Home</NavLink>
<NavLink to="/predictor">Predictor</NavLink>
<NavLink to="/about">About</NavLink>
</div>
</nav>
);
}

export default Navbar;