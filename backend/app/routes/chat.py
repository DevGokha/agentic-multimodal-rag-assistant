import os
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.orchestrator import run_agent

# Step 0: Create a logger for the chat route
logger = logging.getLogger("chat")

# Step 0b: Choose LLM provider based on environment variables
#          - If GROQ_API_KEY is set → use Groq (free cloud API, for deployment)
#          - Otherwise → use Ollama (local inference, for development)
groq_api_key = os.environ.get("GROQ_API_KEY")

if groq_api_key:
    # Step 0c: Use Groq cloud LLM (fast, free, no GPU needed on server)
    from langchain_groq import ChatGroq
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=groq_api_key,
        max_tokens=256,
        temperature=0.7,
    )
    logger.info("Using Groq LLM (cloud)")
else:
    # Step 0d: Use Ollama local LLM
    from langchain_ollama import OllamaLLM
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    llm = OllamaLLM(
        model="tinyllama",
        base_url=ollama_base_url,
        num_predict=256,
        stop=["User:", "\nUser ", "\nAssistant:", "\nQuestion:", "\n\n\n"],
    )
    logger.info("Using Ollama LLM (local)")

router = APIRouter()

# Request schema
class QueryRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat(req: QueryRequest):
    # Step 2: Log the incoming user query
    logger.info("Incoming query: %s", req.query)
    response = await run_agent(req.query, llm)
    return {"response": response}