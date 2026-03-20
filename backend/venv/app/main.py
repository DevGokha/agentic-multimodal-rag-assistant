from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.llms import Ollama

app = FastAPI()

# Load LLM (mistral)
llm = Ollama(model="mistral")

# Request schema
class QueryRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "Agentic AI Backend Running 🚀"}

@app.post("/chat")
async def chat(req: QueryRequest):
    response = llm.invoke(req.query)
    return {"response": response}