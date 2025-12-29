import React, { useState } from "react";
import "./Chatbot.css";
import { API_BASE_URL } from "../config";

fetch(`${API_BASE_URL}/chat`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: userInput })
})
  .then(res => res.json())
  .then(data => setReply(data.reply));

function Chatbot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { from: "bot", text: "👋 Hi! How may I help you?" }
  ]);
  const [input, setInput] = useState("");

  const quickReplies = [
    "What does this app do?",
    "How does prediction work?",
    "Contact support"
  ];

  const toggleChat = () => setOpen(!open);

  const sendMessage = (text) => {
    if (!text.trim()) return;

    const userMsg = { from: "user", text };
    const botMsg = {
      from: "bot",
      text:
        text.includes("predict")
          ? "Our AI predicts response time based on volume, priority, and category."
          : text.includes("contact")
          ? "You can contact support via email or the About page."
          : "This is an AI-powered customer support response time predictor."
    };

    setMessages([...messages, userMsg, botMsg]);
    setInput("");
  };

  return (
    <>
      {/* Floating Button */}
      <div className="chatbot-button" onClick={toggleChat}>
        💬
      </div>

      {/* Chat Window */}
      {open && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            AI Assistant
            <span onClick={toggleChat}>✕</span>
          </div>

          <div className="chatbot-body">
            {messages.map((msg, index) => (
              <div key={index} className={`msg ${msg.from}`}>
                {msg.text}
              </div>
            ))}

            <div className="quick-replies">
              {quickReplies.map((q, i) => (
                <button key={i} onClick={() => sendMessage(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>

          <div className="chatbot-input">
            <input
              type="text"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
            />
            <button onClick={() => sendMessage(input)}>Send</button>
          </div>
        </div>
      )}
    </>
  );
}

export default Chatbot;
