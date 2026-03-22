import logging
from fastapi import APIRouter
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
from app.services.orchestrator import run_agent

# Step 0: Create a logger for the chat route
logger = logging.getLogger("chat")

router = APIRouter()

# Load LLM
# Step 1: Set num_predict to limit response length and stop tokens to prevent
#         the model from generating fake multi-turn conversations
llm = OllamaLLM(
    model="tinyllama",
    num_predict=256,
    stop=["User:", "\nUser ", "\nAssistant:", "\nQuestion:", "\n\n\n"],
)

# Request schema
class QueryRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat(req: QueryRequest):
    # Step 2: Log the incoming user query
    logger.info("Incoming query: %s", req.query)
    response = await run_agent(req.query, llm)
    return {"response": response}