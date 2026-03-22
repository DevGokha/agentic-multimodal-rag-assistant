import { useState, useRef, useEffect } from "react";
import { sendQuery, uploadFile, uploadImage } from "../services/api";

function ChatBox() {
  // Step 1: State for input, messages, and loading indicator
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);

  // Step 1b: Handle PDF upload from the chat input area
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    // Step 1c: Show upload status as a bot message
    setMessages((prev) => [...prev, { role: "bot", text: `📄 Uploading "${file.name}"...` }]);
    try {
      const res = await uploadFile(file);
      setMessages((prev) => [...prev, { role: "bot", text: res.message || "✅ File uploaded successfully!" }]);
    } catch {
      setMessages((prev) => [...prev, { role: "bot", text: "❌ Upload failed. Please try again." }]);
    }
    // Step 1d: Reset the file input so the same file can be re-uploaded
    e.target.value = null;
  };

  // Step 1e: Handle image upload — sends to vision model for AI description
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Step 1f: Create a local preview URL for the image and show it in chat
    const previewUrl = URL.createObjectURL(file);
    setMessages((prev) => [
      ...prev,
      { role: "user", text: `🖼️ Uploaded image`, image: previewUrl },
    ]);
    setLoading(true);

    try {
      // Step 1g: Send the image to the backend vision model
      const res = await uploadImage(file);
      const botMsg = { role: "bot", text: res.description || "Could not analyze the image." };
      setMessages((prev) => [...prev, botMsg]);
      // Step 1h: Speak the image description aloud
      speak(res.description);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "❌ Image analysis failed. Make sure the vision model is running." },
      ]);
    } finally {
      setLoading(false);
    }
    // Step 1i: Reset the file input
    e.target.value = null;
  };

  // Step 2: Auto-scroll to newest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Step 3: Voice input via Web Speech API
  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const recognition = new SpeechRecognition();
    recognition.onresult = (event) => {
      setInput(event.results[0][0].transcript);
    };
    recognition.start();
  };

  // Step 3b: Text-to-speech — reads bot response aloud like ChatGPT
  const speak = (text) => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  };

  // Step 4: Send message to the backend
  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    // Step 4a: Add user message to chat
    const userMsg = { role: "user", text: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // Step 4b: Call backend and add bot response
      const res = await sendQuery(trimmed);
      const botMsg = { role: "bot", text: res.response };
      setMessages((prev) => [...prev, botMsg]);
      // Step 4b2: Automatically speak the bot's response aloud
      speak(res.response);
    } catch {
      // Step 4c: Handle errors gracefully
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "⚠️ Could not reach the server. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Step 5: Send on Enter key press
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Step 6: Render the chat UI
  return (
    <div className="chat-container">
      {/* Step 7: Messages area */}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <span className="icon">💬</span>
            <p>Start a conversation — ask anything!</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message-row ${msg.role}`}>
            {/* Step 8: Avatar */}
            <div className="message-avatar">
              {msg.role === "user" ? "👤" : "🤖"}
            </div>
            {/* Step 9: Message bubble */}
            <div className="message-bubble">
              {/* Step 9a: Show image preview if the message has an image */}
              {msg.image && (
                <img
                  src={msg.image}
                  alt="Uploaded"
                  className="chat-image-preview"
                />
              )}
              {msg.text}
              {/* Step 9b: Speaker button on bot messages to replay audio */}
              {msg.role === "bot" && (
                <button
                  className="speak-btn"
                  onClick={() => speak(msg.text)}
                  title="Read aloud"
                >
                  🔊
                </button>
              )}
            </div>
          </div>
        ))}

        {/* Step 10: Typing animation while loading */}
        {loading && (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Step 11: Input area */}
      <div className="chat-input-area">
        <button className="mic-btn" onClick={startListening} title="Voice input">
          🎤
        </button>
        <button className="mic-btn" onClick={() => fileInputRef.current?.click()} title="Upload PDF">
          📎
        </button>
        <button className="mic-btn" onClick={() => imageInputRef.current?.click()} title="Upload Image">
          🖼️
        </button>
        <input
          type="file"
          accept=".pdf"
          ref={fileInputRef}
          onChange={handleFileUpload}
          style={{ display: "none" }}
        />
        <input
          type="file"
          accept="image/*"
          ref={imageInputRef}
          onChange={handleImageUpload}
          style={{ display: "none" }}
        />
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          Send ➤
        </button>
      </div>
    </div>
  );
}

export default ChatBox;