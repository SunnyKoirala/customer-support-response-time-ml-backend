import React, { useState } from "react";
import "./Chatbot.css";

function Chatbot() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "👋 Hi! How may I help you today?" }
  ]);
  const [input, setInput] = useState("");

  const botReply = (text) => {
    let reply = "🤖 I'm here to help!";
    if (text.includes("how")) reply = "This AI predicts customer support response time using ML.";
    if (text.includes("model")) reply = "We use ElasticNet regression with engineered features.";
    if (text.includes("feature")) reply = "Features include ticket volume, priority, category & time.";
    if (text.includes("help")) reply = "You can ask about the model, prediction, or features.";

    setMessages((prev) => [...prev, { sender: "bot", text: reply }]);
  };

  const sendMessage = () => {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { sender: "user", text: input }]);
    setTimeout(() => botReply(input.toLowerCase()), 700);
    setInput("");
  };

  const quickAsk = (text) => {
    setMessages((prev) => [...prev, { sender: "user", text }]);
    setTimeout(() => botReply(text.toLowerCase()), 700);
  };

  return (
    <div className="chatbot">
      <div className="chat-header">AI Assistant</div>

      <div className="chat-body">
        {messages.map((msg, i) => (
          <div key={i} className={`msg ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
      </div>

      <div className="quick-options">
        <button onClick={() => quickAsk("How does this AI work?")}>How it works</button>
        <button onClick={() => quickAsk("What model is used?")}>Model</button>
        <button onClick={() => quickAsk("What features are used?")}>Features</button>
      </div>

      <div className="chat-input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question..."
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chatbot;
