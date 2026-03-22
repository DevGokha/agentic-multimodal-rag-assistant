import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, upload

# Step 0: Configure structured logging format
# Shows timestamp, log level, module name, and the message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)-20s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(
    title="Agentic AI Backend",
    description="RAG + Agents + Tools + Memory",
    version="1.0.0"
)

# Step 1: Enable CORS so the React frontend (port 5173) can call the backend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(chat.router)
app.include_router(upload.router)

@app.get("/")
def root():
    return {"message": "Agentic AI Backend Running 🚀"}