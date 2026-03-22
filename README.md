# Agentic Multimodal RAG Assistant

An intelligent AI assistant built with a **multi-agent architecture** that autonomously routes queries to specialized agents — LLM, RAG, Web Search, Vision, and Calculator — based on user intent. Powered by local LLMs via Ollama (no API keys required).

---

## Features

- **Autonomous Agent Routing** — A planner agent analyzes each query and routes it to the best-suited agent automatically
- **RAG Pipeline** — Upload PDFs, extract text, generate vector embeddings, store in FAISS, and retrieve relevant context for answers
- **Vision Agent** — Upload images and get AI-powered descriptions using a local vision model (Moondream)
- **Web Search Agent** — Fetch live information from the web via DuckDuckGo (no API key needed)
- **Calculator Tool** — Handles math expressions through a dedicated tool agent
- **Voice I/O** — Speech-to-text input and text-to-speech output using the Web Speech API
- **Conversation Memory** — Maintains chat history for context-aware multi-turn dialogue
- **Structured Logging** — Logs agent selection, response time, and query details for every request
- **Agent Evaluation** — Automated test suite validating routing accuracy across all agent types
- **Local-First** — Runs entirely offline using Ollama — no OpenAI/cloud API keys required

---

## Architecture

```
                         +-----------+
                         |   User    |
                         +-----+-----+
                               |
                    Text / Voice / Image / PDF
                               |
                   +-----------v-----------+
                   |    React Frontend     |
                   | (Vite + Web Speech)   |
                   +-----------+-----------+
                               |
                          REST API
                               |
                   +-----------v-----------+
                   |  FastAPI Backend      |
                   |  /chat  /upload       |
                   |  /upload-image        |
                   +-----------+-----------+
                               |
                   +-----------v-----------+
                   |    Planner Agent      |
                   |  (Intent Detection)   |
                   +-----------+-----------+
                               |
            +--------+---------+---------+--------+
            |        |         |         |        |
       +----v--+ +---v---+ +--v---+ +---v---+ +--v--------+
       |  LLM  | |  RAG  | | Web  | | Vision| | Calculator|
       | Agent | | Agent | |Search| | Agent | |   Tool    |
       +---+---+ +---+---+ +--+---+ +---+---+ +--+--------+
           |         |        |          |         |
       +---v---+ +---v---+ +--v---+ +---v---+ +---v---+
       |Ollama | |FAISS  | |DDG   | |Moon-  | | Regex |
       |Tiny-  | |Vector | |API   | |dream  | | Eval  |
       |Llama  | |Store  | |      | |Vision | |       |
       +-------+ +-------+ +------+ +-------+ +-------+
```

### Agent Routing Logic

| User Intent           | Detected By                              | Routed To                    | Example                     |
| --------------------- | ---------------------------------------- | ---------------------------- | --------------------------- |
| General question      | Default                                  | **LLM Agent** (Ollama)       | "What is machine learning?" |
| PDF/document question | Keywords: `pdf`, `document`, `notes`     | **RAG Agent** (FAISS)        | "What does the PDF say?"    |
| Live/current info     | Keywords: `search`, `latest`, `trending` | **Web Search Agent** (DDG)   | "Search latest AI news"     |
| Math calculation      | Keyword: `calculate`                     | **Calculator Tool**          | "Calculate 25 \* 4"         |
| Image upload          | File type detection                      | **Vision Agent** (Moondream) | Upload an image via the UI  |

---

## Tech Stack

### Backend

| Technology                 | Purpose                                     |
| -------------------------- | ------------------------------------------- |
| **Python 3.12**            | Runtime                                     |
| **FastAPI**                | REST API framework                          |
| **LangChain**              | LLM orchestration & RAG pipeline            |
| **Ollama**                 | Local LLM inference (TinyLlama + Moondream) |
| **FAISS**                  | Vector similarity search                    |
| **HuggingFace Embeddings** | Text embeddings (all-MiniLM-L6-v2)          |
| **DuckDuckGo Search**      | Web search (no API key)                     |

### Frontend

| Technology         | Purpose                      |
| ------------------ | ---------------------------- |
| **React 19**       | UI framework                 |
| **Vite**           | Build tool & dev server      |
| **Web Speech API** | Voice input & text-to-speech |
| **Vanilla CSS**    | Dark glassmorphism theme     |

---

## Project Structure

```
agentic-multimodal-rag-assistant/
|
+-- backend/
|   +-- app/
|   |   +-- main.py                 # FastAPI app + CORS + logging config
|   |   +-- agents/
|   |   |   +-- planner.py          # Autonomous agent router (intent detection)
|   |   |   +-- tool.py             # Calculator tool agent
|   |   |   +-- web_search.py       # DuckDuckGo web search agent
|   |   +-- routes/
|   |   |   +-- chat.py             # POST /chat endpoint
|   |   |   +-- upload.py           # POST /upload + /upload-image endpoints
|   |   +-- services/
|   |   |   +-- orchestrator.py     # Agent orchestration + logging
|   |   |   +-- memory.py           # In-memory conversation history
|   |   +-- utils/
|   |       +-- rag.py              # PDF processing + FAISS vector search
|   |       +-- image.py            # Vision model image analysis
|   +-- tests/
|   |   +-- test_planner.py         # Agent routing evaluation (14 test cases)
|   +-- data/
|       +-- documents/              # Uploaded PDFs & images
|
+-- frontend/
    +-- src/
        +-- components/
        |   +-- ChatBox.jsx          # Main chat UI (text, voice, file upload)
        |   +-- Message.jsx          # Message bubble component
        |   +-- Upload.jsx           # Upload component
        +-- pages/
        |   +-- Home.jsx             # Main page layout
        +-- services/
        |   +-- api.js               # API calls (chat, upload, upload-image)
        +-- App.jsx                  # App root
        +-- App.css                  # Dark glassmorphism theme
        +-- index.jsx                # Entry point
```

---

## Setup & Installation

### Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **Ollama** — [Install from ollama.com](https://ollama.com)

### 1. Clone the Repository

```bash
git clone https://github.com/DevGokha/agentic-multimodal-rag-assistant.git
cd agentic-multimodal-rag-assistant
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn langchain langchain-ollama langchain-community
pip install faiss-cpu sentence-transformers pypdf python-multipart
pip install ddgs requests
```

### 3. Pull Ollama Models

```bash
# Text model (637 MB)
ollama pull tinyllama

# Vision model (1.7 GB)
ollama pull moondream
```

### 4. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
# Backend runs at http://localhost:8000
```

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:5173
```

### 6. Run Agent Evaluation

```bash
cd backend
python -m tests.test_planner
```

---

## Usage

1. **Chat** — Type any question and the planner agent auto-routes to the best agent
2. **Upload PDF** — Click the 📎 button to upload a PDF, then ask "What does the PDF say?"
3. **Upload Image** — Click the 🖼️ button to upload an image for AI description
4. **Voice Input** — Click the 🎤 button to speak your question
5. **Web Search** — Ask "Search latest AI news" to fetch live results
6. **Calculator** — Ask "Calculate 25 \* 4 + 10" for math

---

## API Endpoints

| Method | Endpoint        | Description                                      |
| ------ | --------------- | ------------------------------------------------ |
| `POST` | `/chat`         | Send a text query — auto-routed by planner agent |
| `POST` | `/upload`       | Upload a PDF for RAG processing                  |
| `POST` | `/upload-image` | Upload an image for vision model analysis        |
| `GET`  | `/`             | Health check                                     |

---

## Evaluation Results

```
=================================================================
  AGENT ROUTING EVALUATION
=================================================================

  [PASS] Test  1/14 | Expected: llm          | Got: llm          | "hello"
  [PASS] Test  2/14 | Expected: llm          | Got: llm          | "What is machine learning?"
  [PASS] Test  3/14 | Expected: llm          | Got: llm          | "Tell me a joke"
  [PASS] Test  4/14 | Expected: llm          | Got: llm          | "How does gravity work?"
  [PASS] Test  5/14 | Expected: web_search   | Got: web_search   | "search latest AI trends"
  [PASS] Test  6/14 | Expected: web_search   | Got: web_search   | "What is the latest news?"
  [PASS] Test  7/14 | Expected: web_search   | Got: web_search   | "Find online resources"
  [PASS] Test  8/14 | Expected: web_search   | Got: web_search   | "What is currently trending?"
  [PASS] Test  9/14 | Expected: tool         | Got: tool         | "calculate 25 * 4 + 10"
  [PASS] Test 10/14 | Expected: tool         | Got: tool         | "calculate the square root"
  [PASS] Test 11/14 | Expected: rag          | Got: rag          | "What does the pdf say?"
  [PASS] Test 12/14 | Expected: rag          | Got: rag          | "Summarize the document"
  [PASS] Test 13/14 | Expected: rag          | Got: rag          | "Explain the notes"
  [PASS] Test 14/14 | Expected: rag          | Got: rag          | "What is in the uploaded file?"

  Results: 14/14 passed | Accuracy: 100.0%
```

---

## Structured Logging

Every request is logged with agent selection and response time:

```
2026-03-22 14:58:18 | INFO    | chat                 | Incoming query: search python 3.13
2026-03-22 14:58:18 | INFO    | orchestrator         | Agent: web_search    | Query: search python 3.13
2026-03-22 14:58:23 | INFO    | orchestrator         | Agent: web_search    | Time: 4.99s | Response: ...
```

---

## License

This project is open source and available under the [MIT License](LICENSE).
