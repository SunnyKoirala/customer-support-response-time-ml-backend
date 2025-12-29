import React from "react";
import Chatbot from "./components/Chatbot";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Predictor from "./pages/Predictor";
import About from "./pages/About";
import "./App.css";


function App() {
return (
<div className="app-layout">
<Navbar />

  <main className="content">
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/predictor" element={<Predictor />} />
      <Route path="/about" element={<About />} />
    </Routes>
  </main>

  <Footer />
  <Chatbot />
</div>
);
}
export default App;