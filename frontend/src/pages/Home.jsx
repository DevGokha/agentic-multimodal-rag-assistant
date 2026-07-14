import { useContext } from "react";
import ChatBox from "../components/ChatBox";
import { AuthContext } from "../context/AuthContext";

function Home() {
  const { logout } = useContext(AuthContext);

  return (
    <div className="app-container">
      <button onClick={logout} className="logout-btn">Logout</button>
      {/* Step 1: App header with gradient title */}
      <div className="app-header">
        <h1>🤖 Agentic AI Assistant</h1>
        <p>Upload documents & ask anything — powered by RAG + LLM</p>
      </div>

      {/* Step 2: Chat interface */}
      <ChatBox />
    </div>
  );
}

export default Home;