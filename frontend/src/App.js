import { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input) return;

    setMessages([...messages, { sender: "user", text: input }]);

    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: input })
    });

    const data = await response.json();

    setMessages(prev => [...prev, { sender: "bot", text: data.reply }]);
    setInput("");
  };

  return (
    <div className="App">
      <h2>Student Mental Health Chatbot</h2>
      <div className="chat-box" style={{ border: '1px solid #ccc', padding: 10, height: 300, overflowY: 'auto' }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ margin: '10px 0', textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
            <strong>{msg.sender === "user" ? "You" : "Bot"}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <input
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyPress={e => e.key === 'Enter' && sendMessage()}
        placeholder="Type your thoughts..."
        style={{ width: '80%', padding: 8 }}
      />
      <button onClick={sendMessage} style={{ padding: '8px 16px', marginLeft: 10 }}>Send</button>
    </div>
  );
}

export default App;