import ChatBox from "../components/ChatBox";

function Home() {
  return (
    <div className="app-container">
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